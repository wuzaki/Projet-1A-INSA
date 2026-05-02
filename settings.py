import pygame as pg

pg.init()

# ==== App Settings ====
WIDTH, HEIGHT = 1280, 680 # pg.display.Info().current_w, pg.display.Info().current_h
FPS = 60

# ==== Player Settings ====
SPEED = 860
ROT_SPEED = 4.2
FRICTION = -5
ACC_STRENGTH = 860

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
ENEMY_MIN_DIST = 100 # pixels
ENEMY_MAX_DIST = 400 # pixels
ENEMY_DELAY_DETECTION = 1.0 # secondes

def world_to_grid(pos, tile_size):
    return int(pos[0] // tile_size), int(pos[1] // tile_size)

def grid_to_world(cell, tile_size):
    return cell[0] * tile_size, cell[1] * tile_size