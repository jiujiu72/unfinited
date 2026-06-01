import pygame
import sys
from settings import (
    TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    GAME_STATE_MENU, GAME_STATE_PLAYING, GAME_STATE_PAUSED, GAME_STATE_GAMEOVER,
)
from player import Player
from world import World
from monster import MonsterManager
from bullet import BulletManager
from items import ItemManager
from inventory import Inventory
from ui import UI
from database import save_score, get_high_score


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.state = GAME_STATE_MENU
        self.ui = UI()
        self.player = None
        self.world = None
        self.monster_manager = None
        self.bullet_manager = None
        self.item_manager = None
        self.inventory = None
        self.high_score = get_high_score()

    def new_game(self):
        self.world = World()
        spawn_x, spawn_y = self.world.get_player_spawn_world()
        self.player = Player(spawn_x, spawn_y)
        self.monster_manager = MonsterManager(self.world)
        self.monster_manager.spawn_initial(spawn_x, spawn_y)
        self.bullet_manager = BulletManager()
        self.item_manager = ItemManager(self.world)
        self.item_manager.spawn_initial(spawn_x, spawn_y)
        self.inventory = Inventory()
        self.state = GAME_STATE_PLAYING

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == GAME_STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        self.new_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False

                elif self.state == GAME_STATE_PLAYING:
                    if self.inventory and self.inventory.is_open:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_e:
                            self.inventory.use_item(
                                self.inventory.selected_index, self.player
                            )
                        else:
                            self.inventory.handle_input(event)
                    elif event.key == pygame.K_TAB:
                        self.inventory.is_open = True
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GAME_STATE_PAUSED

                elif self.state == GAME_STATE_PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_q:
                        self.state = GAME_STATE_MENU

                elif self.state == GAME_STATE_GAMEOVER:
                    if event.key == pygame.K_r:
                        self.new_game()
                    elif event.key == pygame.K_q:
                        self.state = GAME_STATE_MENU

        return True

    def _update(self, dt):
        if self.state == GAME_STATE_PLAYING:
            if self.inventory and self.inventory.is_open:
                return

            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, self.world)

            self.monster_manager.update(self.player, dt)

            kills = self.bullet_manager.update(
                self.player, self.monster_manager.monsters, self.world
            )
            self.player.kills += kills

            for mx, my in self.bullet_manager.killed_positions:
                self.item_manager.drop_from_monster(mx, my)

            self.item_manager.update(self.player, self.inventory)
            self.inventory.update_buffs(self.player)

            self._apply_equipment_bonuses()

            if self.player.leveled_up:
                self.player.leveled_up = False

            if not self.player.is_alive():
                self._game_over()

    def _apply_equipment_bonuses(self):
        bonuses = self.inventory.get_equipment_bonuses()
        self.player.attack = self.player.base_attack + bonuses["attack"]
        self.player.defense = self.player.base_defense + bonuses["defense"]
        for buff in self.inventory.buffs:
            if buff["stat"] == "attack":
                self.player.attack += buff["value"]
            elif buff["stat"] == "defense":
                self.player.defense += buff["value"]
            elif buff["stat"] == "speed":
                pass

    def _game_over(self):
        self.state = GAME_STATE_GAMEOVER
        save_score(self.player.score, self.player.level, self.player.kills)
        self.high_score = get_high_score()

    def _draw(self):
        self.screen.fill((0, 0, 0))

        if self.state == GAME_STATE_MENU:
            self.ui.draw_menu(self.screen, self.high_score)

        elif self.state == GAME_STATE_PLAYING:
            self.world.draw(self.screen, self.player.world_x, self.player.world_y)
            self.item_manager.draw(self.screen, self.player.world_x, self.player.world_y)
            self.monster_manager.draw(self.screen, self.player.world_x, self.player.world_y)
            self.bullet_manager.draw(self.screen, self.player.world_x, self.player.world_y)
            self.player.draw(self.screen)
            self.ui.draw_hud(self.screen, self.player, self.inventory)
            self.inventory.draw(self.screen, self.ui.font_medium,
                                self.ui.font_small, self.player)

        elif self.state == GAME_STATE_PAUSED:
            self.world.draw(self.screen, self.player.world_x, self.player.world_y)
            self.monster_manager.draw(self.screen, self.player.world_x, self.player.world_y)
            self.bullet_manager.draw(self.screen, self.player.world_x, self.player.world_y)
            self.player.draw(self.screen)
            self.ui.draw_hud(self.screen, self.player)
            self.ui.draw_pause(self.screen)

        elif self.state == GAME_STATE_GAMEOVER:
            self.world.draw(self.screen, self.player.world_x, self.player.world_y)
            self.player.draw(self.screen)
            self.ui.draw_gameover(self.screen, self.player, self.high_score)

        pygame.display.flip()
