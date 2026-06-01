import pygame
import random
from settings import TILE_SIZE, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT

TILE_FLOOR = 0
TILE_WALL = 1
TILE_OBSTACLE = 2
TILE_CORRIDOR = 3

TILE_DRAW_COLORS = {
    TILE_FLOOR: COLORS["dark_gray"],
    TILE_WALL: COLORS["brown"],
    TILE_OBSTACLE: (80, 80, 80),
    TILE_CORRIDOR: (60, 60, 50),
}


class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def center(self):
        return self.x + self.w // 2, self.y + self.h // 2

    def intersects(self, other, margin=1):
        return not (self.x + self.w + margin <= other.x or
                    other.x + other.w + margin <= self.x or
                    self.y + self.h + margin <= other.y or
                    other.y + other.h + margin <= self.y)


class BSPNode:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left = None
        self.right = None
        self.room = None

    def split(self, min_size=8):
        if self.left is not None:
            return
        if self.w < min_size * 2 and self.h < min_size * 2:
            return

        if self.w > self.h:
            horizontal = False
        elif self.h > self.w:
            horizontal = True
        else:
            horizontal = random.random() < 0.5

        if horizontal:
            if self.h < min_size * 2:
                return
            split_pos = random.randint(min_size, self.h - min_size)
            self.left = BSPNode(self.x, self.y, self.w, split_pos)
            self.right = BSPNode(self.x, self.y + split_pos, self.w, self.h - split_pos)
        else:
            if self.w < min_size * 2:
                return
            split_pos = random.randint(min_size, self.w - min_size)
            self.left = BSPNode(self.x, self.y, split_pos, self.h)
            self.right = BSPNode(self.x + split_pos, self.y, self.w - split_pos, self.h)

        self.left.split(min_size)
        self.right.split(min_size)

    def create_rooms(self, rooms, min_room=4, padding=2):
        if self.left is None and self.right is None:
            rw = random.randint(min_room, max(min_room, self.w - padding * 2))
            rh = random.randint(min_room, max(min_room, self.h - padding * 2))
            rx = self.x + random.randint(padding, max(padding, self.w - rw - padding))
            ry = self.y + random.randint(padding, max(padding, self.h - rh - padding))
            self.room = Room(rx, ry, rw, rh)
            rooms.append(self.room)
        else:
            if self.left:
                self.left.create_rooms(rooms, min_room, padding)
            if self.right:
                self.right.create_rooms(rooms, min_room, padding)

    def get_room(self):
        if self.room:
            return self.room
        if self.left:
            r = self.left.get_room()
            if r:
                return r
        if self.right:
            r = self.right.get_room()
            if r:
                return r
        return None


class DungeonMap:
    def __init__(self, width=80, height=60):
        self.width = width
        self.height = height
        self.tiles = [[TILE_WALL] * width for _ in range(height)]
        self.rooms = []
        self.spawn_points = []
        self._generate()

    def _generate(self):
        root = BSPNode(0, 0, self.width, self.height)
        root.split(min_size=10)
        root.create_rooms(self.rooms, min_room=5, padding=2)

        for room in self.rooms:
            for y in range(room.y, min(room.y + room.h, self.height)):
                for x in range(room.x, min(room.x + room.w, self.width)):
                    self.tiles[y][x] = TILE_FLOOR

        self._connect_rooms(root)
        self._place_obstacles()
        self._compute_spawn_points()

    def _connect_rooms(self, node):
        if node.left is None or node.right is None:
            return
        self._connect_rooms(node.left)
        self._connect_rooms(node.right)

        room_a = node.left.get_room()
        room_b = node.right.get_room()
        if room_a and room_b:
            self._carve_corridor(room_a.center, room_b.center)

    def _carve_corridor(self, start, end):
        x1, y1 = start
        x2, y2 = end

        if random.random() < 0.5:
            self._carve_h(x1, x2, y1)
            self._carve_v(y1, y2, x2)
        else:
            self._carve_v(y1, y2, x1)
            self._carve_h(x1, x2, y2)

    def _carve_h(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= y < self.height and 0 <= x < self.width:
                if self.tiles[y][x] == TILE_WALL:
                    self.tiles[y][x] = TILE_CORRIDOR

    def _carve_v(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= y < self.height and 0 <= x < self.width:
                if self.tiles[y][x] == TILE_WALL:
                    self.tiles[y][x] = TILE_CORRIDOR

    def _place_obstacles(self):
        for room in self.rooms:
            num_obstacles = random.randint(0, max(1, (room.w * room.h) // 20))
            for _ in range(num_obstacles):
                ox = random.randint(room.x + 1, room.x + room.w - 2)
                oy = random.randint(room.y + 1, room.y + room.h - 2)
                if 0 <= oy < self.height and 0 <= ox < self.width:
                    if (ox, oy) != room.center:
                        self.tiles[oy][ox] = TILE_OBSTACLE

    def _compute_spawn_points(self):
        for room in self.rooms:
            for y in range(room.y + 1, room.y + room.h - 1):
                for x in range(room.x + 1, room.x + room.w - 1):
                    if self.tiles[y][x] == TILE_FLOOR:
                        self.spawn_points.append((x, y))

    def is_walkable(self, tile_x, tile_y):
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x] in (TILE_FLOOR, TILE_CORRIDOR)
        return False

    def get_player_spawn(self):
        if self.rooms:
            return self.rooms[0].center
        return (self.width // 2, self.height // 2)


class World:
    def __init__(self):
        self.dungeon = DungeonMap(width=80, height=60)

    def regenerate(self):
        self.dungeon = DungeonMap(width=80, height=60)

    def is_walkable_world(self, world_x, world_y):
        tile_x = int(world_x) // TILE_SIZE
        tile_y = int(world_y) // TILE_SIZE
        return self.dungeon.is_walkable(tile_x, tile_y)

    def is_rect_walkable(self, cx, cy, half_size):
        corners = [
            (cx - half_size, cy - half_size),
            (cx + half_size, cy - half_size),
            (cx - half_size, cy + half_size),
            (cx + half_size, cy + half_size),
        ]
        for wx, wy in corners:
            tx = int(wx) // TILE_SIZE
            ty = int(wy) // TILE_SIZE
            if not self.dungeon.is_walkable(tx, ty):
                return False
        return True

    def get_player_spawn_world(self):
        tx, ty = self.dungeon.get_player_spawn()
        return tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2

    def draw(self, screen, camera_x, camera_y):
        offset_x = SCREEN_WIDTH // 2 - camera_x
        offset_y = SCREEN_HEIGHT // 2 - camera_y

        start_col = max(0, int((camera_x - SCREEN_WIDTH // 2) // TILE_SIZE) - 1)
        end_col = min(self.dungeon.width, int((camera_x + SCREEN_WIDTH // 2) // TILE_SIZE) + 2)
        start_row = max(0, int((camera_y - SCREEN_HEIGHT // 2) // TILE_SIZE) - 1)
        end_row = min(self.dungeon.height, int((camera_y + SCREEN_HEIGHT // 2) // TILE_SIZE) + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = self.dungeon.tiles[row][col]
                screen_x = col * TILE_SIZE + offset_x
                screen_y = row * TILE_SIZE + offset_y
                color = TILE_DRAW_COLORS.get(tile, COLORS["black"])
                pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                if tile == TILE_WALL:
                    pygame.draw.rect(screen, (100, 60, 30), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
                elif tile == TILE_OBSTACLE:
                    pygame.draw.line(screen, COLORS["gray"],
                                     (screen_x + 4, screen_y + 4),
                                     (screen_x + TILE_SIZE - 4, screen_y + TILE_SIZE - 4), 2)
                    pygame.draw.line(screen, COLORS["gray"],
                                     (screen_x + TILE_SIZE - 4, screen_y + 4),
                                     (screen_x + 4, screen_y + TILE_SIZE - 4), 2)

    def cleanup_distant_chunks(self, camera_x, camera_y):
        pass
