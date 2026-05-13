import settings as s
import pygame as pg
import math

"""
Ce fichier contient la classe Enemy pour la gestion des ennemis.
"""

# ==== Enemy ====
class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.xy = pg.math.Vector2(x, y)
        self.image = self.load_image("assets/player.png")
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        self.angle = 0

    def load_image(self, path):
        img = pg.image.load(path).convert_alpha().subsurface((0, 0, 32, 32))
        return img

    def move(self):
        pass

    def sync_rects(self):
        self.rect.midbottom = self.xy.x, self.xy.y
        self.feet.midbottom = self.rect.midbottom

    def update(self):
        self.move()
        self.sync_rects()