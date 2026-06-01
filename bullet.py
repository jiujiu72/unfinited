import pygame
import math
from settings import TILE_SIZE, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


class Bullet:
    def __init__(self, x, y, dx, dy, damage, speed=8):
        self.world_x = float(x)
        self.world_y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.radius = 4
        self.lifetime = 120
        self.alive = True

    def update(self, world):
        self.world_x += self.dx * self.speed
        self.world_y += self.dy * self.speed
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.alive = False
            return

        if not world.is_walkable_world(self.world_x, self.world_y):
            self.alive = False

    def check_hit(self, monster):
        dist = math.hypot(monster.world_x - self.world_x, monster.world_y - self.world_y)
        return dist < (self.radius + monster.size / 2)

    def draw(self, screen, camera_x, camera_y):
        offset_x = SCREEN_WIDTH // 2 - camera_x
        offset_y = SCREEN_HEIGHT // 2 - camera_y
        sx = int(self.world_x + offset_x)
        sy = int(self.world_y + offset_y)

        if -10 < sx < SCREEN_WIDTH + 10 and -10 < sy < SCREEN_HEIGHT + 10:
            pygame.draw.circle(screen, COLORS["yellow"], (sx, sy), self.radius)
            pygame.draw.circle(screen, COLORS["white"], (sx, sy), self.radius - 1)


class BulletManager:
    def __init__(self):
        self.bullets = []
        self.fire_timer = 0
        self.fire_interval = 30

    def update(self, player, monsters, world):
        self.fire_timer += 1
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            self._auto_fire(player, monsters)

        kills = 0
        self.killed_positions = []
        for bullet in self.bullets:
            bullet.update(world)
            if not bullet.alive:
                continue
            for monster in monsters:
                if bullet.check_hit(monster):
                    dead = monster.take_damage(bullet.damage)
                    bullet.alive = False
                    if dead:
                        player.gain_exp(monster.exp_reward)
                        kills += 1
                        self.killed_positions.append(
                            (monster.world_x, monster.world_y)
                        )
                    break

        self.bullets = [b for b in self.bullets if b.alive]
        return kills

    def _auto_fire(self, player, monsters):
        nearest = None
        min_dist = float('inf')
        for m in monsters:
            dist = math.hypot(m.world_x - player.world_x, m.world_y - player.world_y)
            if dist < 400 and dist < min_dist:
                min_dist = dist
                nearest = m

        if nearest:
            dx = nearest.world_x - player.world_x
            dy = nearest.world_y - player.world_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                self.bullets.append(Bullet(player.world_x, player.world_y, dx, dy, player.attack))
        else:
            self.bullets.append(Bullet(player.world_x, player.world_y, 1, 0, player.attack))

    def draw(self, screen, camera_x, camera_y):
        for bullet in self.bullets:
            bullet.draw(screen, camera_x, camera_y)
