import pygame
import random
import math
from settings import TILE_SIZE, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


ITEM_TYPES = {
    "health_potion": {
        "name": "生命药水",
        "category": "consumable",
        "color": (255, 80, 80),
        "effect": "heal",
        "value": 30,
        "description": "恢复30点生命值",
        "drop_weight": 35,
    },
    "big_health_potion": {
        "name": "大生命药水",
        "category": "consumable",
        "color": (255, 40, 40),
        "effect": "heal",
        "value": 60,
        "description": "恢复60点生命值",
        "drop_weight": 15,
    },
    "attack_boost": {
        "name": "力量卷轴",
        "category": "consumable",
        "color": (255, 160, 0),
        "effect": "buff_attack",
        "value": 5,
        "duration": 600,
        "description": "攻击力+5，持续10秒",
        "drop_weight": 20,
    },
    "defense_boost": {
        "name": "护盾卷轴",
        "category": "consumable",
        "color": (100, 200, 255),
        "effect": "buff_defense",
        "value": 5,
        "duration": 600,
        "description": "防御力+5，持续10秒",
        "drop_weight": 15,
    },
    "speed_boost": {
        "name": "疾风卷轴",
        "category": "consumable",
        "color": (0, 255, 180),
        "effect": "buff_speed",
        "value": 2,
        "duration": 480,
        "description": "速度+2，持续8秒",
        "drop_weight": 10,
    },
    "iron_sword": {
        "name": "铁剑",
        "category": "equipment",
        "slot": "weapon",
        "color": (200, 200, 220),
        "effect": "equip_attack",
        "value": 5,
        "description": "攻击力+5",
        "drop_weight": 12,
    },
    "steel_sword": {
        "name": "钢剑",
        "category": "equipment",
        "slot": "weapon",
        "color": (220, 220, 255),
        "effect": "equip_attack",
        "value": 10,
        "description": "攻击力+10",
        "drop_weight": 5,
    },
    "leather_armor": {
        "name": "皮甲",
        "category": "equipment",
        "slot": "armor",
        "color": (160, 100, 50),
        "effect": "equip_defense",
        "value": 3,
        "description": "防御力+3",
        "drop_weight": 12,
    },
    "iron_armor": {
        "name": "铁甲",
        "category": "equipment",
        "slot": "armor",
        "color": (180, 180, 200),
        "effect": "equip_defense",
        "value": 7,
        "description": "防御力+7",
        "drop_weight": 5,
    },
    "speed_boots": {
        "name": "疾风靴",
        "category": "equipment",
        "slot": "accessory",
        "color": (100, 255, 200),
        "effect": "equip_speed",
        "value": 1,
        "description": "速度+1",
        "drop_weight": 8,
    },
}

PICKUP_RANGE = 40


class Item:
    def __init__(self, item_type, world_x, world_y):
        self.item_type = item_type
        self.data = ITEM_TYPES[item_type]
        self.world_x = world_x
        self.world_y = world_y
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.alive = True

    @property
    def name(self):
        return self.data["name"]

    @property
    def category(self):
        return self.data["category"]

    def draw(self, screen, camera_x, camera_y, tick):
        offset_x = SCREEN_WIDTH // 2 - camera_x
        offset_y = SCREEN_HEIGHT // 2 - camera_y
        sx = int(self.world_x + offset_x)
        sy = int(self.world_y + offset_y + math.sin((tick + self.bob_offset) * 0.05) * 3)

        if not (-20 < sx < SCREEN_WIDTH + 20 and -20 < sy < SCREEN_HEIGHT + 20):
            return

        color = self.data["color"]
        if self.category == "consumable":
            pygame.draw.circle(screen, color, (sx, sy), 8)
            pygame.draw.circle(screen, COLORS["white"], (sx, sy), 8, 1)
            pygame.draw.circle(screen, (255, 255, 255, 128), (sx - 2, sy - 2), 3)
        else:
            rect = pygame.Rect(sx - 8, sy - 8, 16, 16)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLORS["white"], rect, 1)
            pygame.draw.line(screen, COLORS["yellow"],
                            (sx - 4, sy), (sx + 4, sy), 2)


class ItemManager:
    def __init__(self, world):
        self.world = world
        self.items = []
        self.tick = 0

    def spawn_initial(self, player_x, player_y):
        spawn_points = self.world.dungeon.spawn_points
        if not spawn_points:
            return
        num_items = random.randint(8, 15)
        for _ in range(num_items):
            tx, ty = random.choice(spawn_points)
            wx = tx * TILE_SIZE + TILE_SIZE // 2
            wy = ty * TILE_SIZE + TILE_SIZE // 2
            dist = math.hypot(wx - player_x, wy - player_y)
            if dist < 150:
                continue
            item_type = self._random_item_type()
            self.items.append(Item(item_type, wx, wy))

    def spawn_in_room(self, room):
        num = random.randint(1, 2)
        for _ in range(num):
            tx = random.randint(room.x + 1, room.x + room.w - 2)
            ty = random.randint(room.y + 1, room.y + room.h - 2)
            if self.world.dungeon.is_walkable(tx, ty):
                wx = tx * TILE_SIZE + TILE_SIZE // 2
                wy = ty * TILE_SIZE + TILE_SIZE // 2
                item_type = self._random_item_type()
                self.items.append(Item(item_type, wx, wy))

    def drop_from_monster(self, monster_x, monster_y):
        if random.random() < 0.25:
            item_type = self._random_item_type()
            self.items.append(Item(item_type, monster_x, monster_y))

    def update(self, player, inventory):
        self.tick += 1
        picked = []
        for item in self.items:
            if not item.alive:
                continue
            dist = math.hypot(item.world_x - player.world_x,
                              item.world_y - player.world_y)
            if dist <= PICKUP_RANGE:
                if inventory.add_item(item):
                    item.alive = False
                    picked.append(item)
        self.items = [i for i in self.items if i.alive]
        return picked

    def draw(self, screen, camera_x, camera_y):
        for item in self.items:
            item.draw(screen, camera_x, camera_y, self.tick)

    def _random_item_type(self):
        types = list(ITEM_TYPES.keys())
        weights = [ITEM_TYPES[t]["drop_weight"] for t in types]
        return random.choices(types, weights=weights, k=1)[0]
