import pygame
from settings import (
    PLAYER_SPEED, PLAYER_HP, PLAYER_ATTACK, PLAYER_DEFENSE,
    TILE_SIZE, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
)


class Player:
    def __init__(self, x=0, y=0):
        self.world_x = float(x)
        self.world_y = float(y)
        self.speed = PLAYER_SPEED
        self.size = TILE_SIZE - 4

        self.base_max_hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.hp = PLAYER_HP
        self.base_attack = PLAYER_ATTACK
        self.attack = PLAYER_ATTACK
        self.base_defense = PLAYER_DEFENSE
        self.defense = PLAYER_DEFENSE
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.score = 0
        self.kills = 0
        self.leveled_up = False

    def handle_input(self, keys, world):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        half = self.size / 2
        new_x = self.world_x + dx * self.speed
        new_y = self.world_y + dy * self.speed

        if world.is_rect_walkable(new_x, self.world_y, half):
            self.world_x = new_x
        if world.is_rect_walkable(self.world_x, new_y, half):
            self.world_y = new_y

    def take_damage(self, amount):
        damage = max(1, amount - self.defense)
        self.hp -= damage
        return damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_exp(self, amount):
        self.exp += amount
        self.score += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level_up()

    def add_kill(self):
        self.kills += 1
        self.score += 10

    def level_up(self):
        self.level += 1
        hp_gain = 20 + self.level * 5
        atk_gain = 3 + self.level // 3
        def_gain = 1 + self.level // 4
        self.base_max_hp += hp_gain
        self.max_hp = self.base_max_hp
        self.hp = self.max_hp
        self.base_attack += atk_gain
        self.attack = self.base_attack
        self.base_defense += def_gain
        self.defense = self.base_defense
        self.exp_to_next = int(self.exp_to_next * 1.4)
        self.leveled_up = True

    def is_alive(self):
        return self.hp > 0

    def get_screen_pos(self):
        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    def draw(self, screen):
        sx, sy = self.get_screen_pos()
        body_rect = pygame.Rect(
            sx - self.size // 2, sy - self.size // 2,
            self.size, self.size
        )
        pygame.draw.rect(screen, COLORS["blue"], body_rect)
        pygame.draw.rect(screen, COLORS["light_blue"], body_rect, 2)

        eye_size = 4
        pygame.draw.rect(screen, COLORS["white"],
                         (sx - 6, sy - 6, eye_size, eye_size))
        pygame.draw.rect(screen, COLORS["white"],
                         (sx + 2, sy - 6, eye_size, eye_size))
