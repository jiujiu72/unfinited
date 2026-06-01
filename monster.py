import pygame
import random
import math
from settings import TILE_SIZE, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from pathfinding import astar


class Monster:
    def __init__(self, world_x, world_y, monster_type="slime"):
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.monster_type = monster_type
        self.size = TILE_SIZE - 8

        stats = MONSTER_TYPES.get(monster_type, MONSTER_TYPES["slime"])
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.attack = stats["attack"]
        self.exp_reward = stats["exp"]
        self.color = stats["color"]
        self.detect_range = stats["detect_range"]

        self.state = "wander"
        self.attack_cooldown = 0
        self.hit_flash = 0

        self.path = []
        self.path_recalc_timer = random.randint(0, 15)
        self.wander_target = None
        self.wander_cooldown = 0

    def update(self, player_x, player_y, world, dt, player=None):
        dist = math.hypot(player_x - self.world_x, player_y - self.world_y)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

        if dist < self.detect_range:
            self.state = "chase"
            self._chase(player_x, player_y, world, player)
        else:
            self.state = "wander"
            self._wander(world)

    def _get_tile(self):
        return int(self.world_x) // TILE_SIZE, int(self.world_y) // TILE_SIZE

    def _chase(self, player_x, player_y, world, player=None):
        self.path_recalc_timer -= 1
        player_tile = (int(player_x) // TILE_SIZE, int(player_y) // TILE_SIZE)
        my_tile = self._get_tile()

        if self.path_recalc_timer <= 0 or not self.path:
            self.path_recalc_timer = 15
            self.path = astar(world.dungeon, my_tile, player_tile)

        if self.path:
            self._follow_path(world, player=player)
        else:
            self._direct_move(player_x, player_y, world, player)

    def _wander(self, world):
        if self.wander_cooldown > 0:
            self.wander_cooldown -= 1

        if not self.path and self.wander_cooldown <= 0:
            self._pick_wander_target(world)

        if self.path:
            self._follow_path(world, speed_mult=0.4)
        else:
            self.wander_cooldown = random.randint(30, 60)

    def _pick_wander_target(self, world):
        my_tile = self._get_tile()
        for _ in range(8):
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            target = (my_tile[0] + dx, my_tile[1] + dy)
            if world.dungeon.is_walkable(target[0], target[1]):
                path = astar(world.dungeon, my_tile, target)
                if path:
                    self.path = path
                    return

    def _follow_path(self, world, speed_mult=1.0, player=None):
        if not self.path:
            return

        target_tile = self.path[0]
        target_x = target_tile[0] * TILE_SIZE + TILE_SIZE // 2
        target_y = target_tile[1] * TILE_SIZE + TILE_SIZE // 2

        dx = target_x - self.world_x
        dy = target_y - self.world_y
        dist = math.hypot(dx, dy)

        if dist < self.speed * speed_mult + 2:
            self.path.pop(0)
            if not self.path:
                return

        if dist > 0:
            dx /= dist
            dy /= dist

        move_speed = self.speed * speed_mult
        new_x = self.world_x + dx * move_speed
        new_y = self.world_y + dy * move_speed

        half = self.size / 2

        if player:
            pdist = math.hypot(new_x - player.world_x, new_y - player.world_y)
            min_dist = (self.size + player.size) / 2
            if pdist < min_dist:
                return

        if world.is_rect_walkable(new_x, self.world_y, half):
            self.world_x = new_x
        if world.is_rect_walkable(self.world_x, new_y, half):
            self.world_y = new_y

    def _direct_move(self, target_x, target_y, world, player=None):
        dx = target_x - self.world_x
        dy = target_y - self.world_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist

        new_x = self.world_x + dx * self.speed
        new_y = self.world_y + dy * self.speed
        half = self.size / 2

        if player:
            pdist = math.hypot(new_x - player.world_x, new_y - player.world_y)
            min_dist = (self.size + player.size) / 2
            if pdist < min_dist:
                return

        if world.is_rect_walkable(new_x, self.world_y, half):
            self.world_x = new_x
        elif world.is_rect_walkable(self.world_x, new_y, half):
            self.world_y = new_y

    def check_collision_with_player(self, player):
        dist = math.hypot(player.world_x - self.world_x, player.world_y - self.world_y)
        collision_dist = (self.size + player.size) / 2
        if dist <= collision_dist + 2 and self.attack_cooldown <= 0:
            player.take_damage(self.attack)
            self.attack_cooldown = 60
            return True
        return False

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 8
        self.path = []
        self.path_recalc_timer = 0
        return self.hp <= 0

    def is_alive(self):
        return self.hp > 0

    def draw(self, screen, camera_x, camera_y):
        offset_x = SCREEN_WIDTH // 2 - camera_x
        offset_y = SCREEN_HEIGHT // 2 - camera_y
        sx = int(self.world_x + offset_x)
        sy = int(self.world_y + offset_y)

        if not (-self.size < sx < SCREEN_WIDTH + self.size and
                -self.size < sy < SCREEN_HEIGHT + self.size):
            return

        color = COLORS["white"] if self.hit_flash > 0 else self.color
        body_rect = pygame.Rect(sx - self.size // 2, sy - self.size // 2, self.size, self.size)
        pygame.draw.rect(screen, color, body_rect)
        pygame.draw.rect(screen, (0, 0, 0), body_rect, 1)

        if self.state == "chase":
            pygame.draw.circle(screen, COLORS["red"], (sx - 4, sy - 4), 3)
            pygame.draw.circle(screen, COLORS["red"], (sx + 4, sy - 4), 3)
        else:
            pygame.draw.circle(screen, COLORS["white"], (sx - 4, sy - 4), 2)
            pygame.draw.circle(screen, COLORS["white"], (sx + 4, sy - 4), 2)

        if self.hp < self.max_hp:
            bar_w = self.size
            bar_h = 4
            bar_x = sx - bar_w // 2
            bar_y = sy - self.size // 2 - 8
            ratio = self.hp / self.max_hp
            pygame.draw.rect(screen, COLORS["dark_gray"], (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, COLORS["red"], (bar_x, bar_y, int(bar_w * ratio), bar_h))


MONSTER_TYPES = {
    "slime": {
        "hp": 30,
        "speed": 1.5,
        "attack": 5,
        "exp": 15,
        "color": (0, 180, 80),
        "detect_range": 150,
    },
    "bat": {
        "hp": 20,
        "speed": 3.0,
        "attack": 3,
        "exp": 10,
        "color": (100, 50, 150),
        "detect_range": 200,
    },
    "skeleton": {
        "hp": 50,
        "speed": 1.8,
        "attack": 10,
        "exp": 30,
        "color": (200, 200, 180),
        "detect_range": 180,
    },
    "demon": {
        "hp": 80,
        "speed": 2.2,
        "attack": 15,
        "exp": 50,
        "color": (180, 30, 30),
        "detect_range": 220,
    },
}


class MonsterManager:
    def __init__(self, world):
        self.monsters = []
        self.world = world
        self.max_monsters = 20
        self.spawn_timer = 0
        self.spawn_interval = 120

    def spawn_initial(self, player_x, player_y):
        spawn_points = self.world.dungeon.spawn_points
        if not spawn_points:
            return
        num_initial = min(12, len(spawn_points) // 10)
        chosen = random.sample(spawn_points, min(num_initial, len(spawn_points)))
        for tx, ty in chosen:
            wx = tx * TILE_SIZE + TILE_SIZE // 2
            wy = ty * TILE_SIZE + TILE_SIZE // 2
            dist = math.hypot(wx - player_x, wy - player_y)
            if dist > 200:
                mtype = self._random_type()
                self.monsters.append(Monster(wx, wy, mtype))

    def _random_type(self):
        r = random.random()
        if r < 0.4:
            return "slime"
        elif r < 0.65:
            return "bat"
        elif r < 0.85:
            return "skeleton"
        else:
            return "demon"

    def update(self, player, dt):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval and len(self.monsters) < self.max_monsters:
            self.spawn_timer = 0
            self._spawn_near_player(player.world_x, player.world_y)

        for monster in self.monsters[:]:
            monster.update(player.world_x, player.world_y, self.world, dt, player)
            monster.check_collision_with_player(player)

        self.monsters = [m for m in self.monsters if m.is_alive()]

    def _spawn_near_player(self, px, py):
        spawn_points = self.world.dungeon.spawn_points
        if not spawn_points:
            return
        for _ in range(10):
            tx, ty = random.choice(spawn_points)
            wx = tx * TILE_SIZE + TILE_SIZE // 2
            wy = ty * TILE_SIZE + TILE_SIZE // 2
            dist = math.hypot(wx - px, wy - py)
            if 300 < dist < 800:
                mtype = self._random_type()
                self.monsters.append(Monster(wx, wy, mtype))
                return

    def draw(self, screen, camera_x, camera_y):
        for monster in self.monsters:
            monster.draw(screen, camera_x, camera_y)
