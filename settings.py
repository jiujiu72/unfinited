TITLE = "程序员无限肉鸽游戏"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 40

PLAYER_SPEED = 4
PLAYER_HP = 100
PLAYER_ATTACK = 10
PLAYER_DEFENSE = 5

BULLET_INTERVAL = 30
BULLET_SPEED = 8
BULLET_RANGE = 400

MONSTER_SPAWN_INTERVAL = 120
MONSTER_MAX_COUNT = 20

COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "dark_gray": (50, 50, 50),
    "green": (0, 200, 0),
    "dark_green": (0, 100, 0),
    "red": (200, 0, 0),
    "blue": (0, 100, 200),
    "yellow": (200, 200, 0),
    "brown": (139, 90, 43),
    "light_blue": (100, 180, 255),
    "orange": (220, 120, 0),
    "purple": (150, 50, 200),
}

GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_PAUSED = "paused"
GAME_STATE_GAMEOVER = "gameover"
