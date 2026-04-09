import pygame as pg

pg.init()

# ==== App Settings ====
WIDTH, HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
FPS = 120

# ==== Player Settings ====
SPEED = 1.25
ROT_SPEED = 0.04
FRICTION = -0.048
ACC_STRENGTH = 0.5

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
ENEMY_SPEED = 0.6  # pixels / seconde
ENEMY_MIN_DIST = 100   # distance minimale avant de s'arrêter
ENEMY_MAX_DIST = 400  # distance maximale avant de commencer à te suivre
ENEMY_DELAY_DETECTION = 1  # temps en ms avant de détecter le joueur

def world_to_grid(pos, tile_size):
    return int(pos[0] // tile_size), int(pos[1] // tile_size)

def grid_to_world(cell, tile_size):
    return cell[0] * tile_size, cell[1] * tile_size