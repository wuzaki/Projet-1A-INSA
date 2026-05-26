import pygame as pg
import math

pg.init()
pg.font.init()

# ==== App Settings ====
WIDTH, HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
FPS = 60

# ==== Player Settings ====
ACCEL = 1600
FRICTION = 3.5 # 5.5
MAX_SPEED = 150 # 250


MOUSE_SENSITIVITY = 0.3
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

TILE_SIZE = 32

# ==== Terminal Settings ====
TERM_WIDTH, TERM_HEIGHT = 800, 600
FONT_SIZE = 20
TERM_FONT = pg.font.SysFont("Monospace", FONT_SIZE, "bold")
LINE_HEIGHT = FONT_SIZE + 5
BG_COLOR = (10, 10, 30)
TEXT_COLOR = (0, 255, 0)
HIGHLIGHT_COLOR = (0, 100, 0)

# ==== Enemy Settings ====
ENEMY_SPEED = 68 # pixels/seconde
ENEMY_MOVE_MIN_DIST = 100 # pixels
ENEMY_SHOOT_MAX_DIST = 180 # pixels
ENEMY_MAX_DIST = 400 # pixels
ENEMY_DELAY_DETECTION = 1.0 # secondes

ENEMY_COLOR_HEALTH_BAR = (204, 29, 29)

# ==== Weapon Constants ====
WEAPONS_DATA = {
        "single": {"cooldown": 0.1, "damage": 25, "max_ammo": 32},
        "shotgun": {"cooldown": 0.5, "damage": 10, "max_ammo": 50},
        "knife": {"cooldown": 0.2, "damage": 50, "max_ammo": 9999},
        "enemy_single": {"cooldown": 0.25, "damage": 5, "max_ammo": None},
        "enemy_shotgun": {"cooldown": 0.5, "damage": 10, "max_ammo": None},
}

def get_text_surf(text):
    font = pg.font.SysFont("Raleway", 28)
    return font.render(text, True, (255, 255, 255))

def show_basic_text(screen, surf, pos):
     screen.blit(surf, pos)

def show_fps(screen, clock):
    font = pg.font.SysFont("Raleway", 28)
    fps_text = font.render(f"FPS: {round(clock.get_fps(), 2)}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

def get_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.atan2(dy, dx)

def correct_shift(screen_x, screen_y, world_x, world_y, zoom):
    x = (screen_x - world_x) * zoom
    y = (screen_y - world_y) * zoom
    return x, y

def world_to_grid(pos):
    return int(pos[0] // TILE_SIZE), int(pos[1] // TILE_SIZE)

def grid_to_world(cell):
    return cell[0] * TILE_SIZE, cell[1] * TILE_SIZE