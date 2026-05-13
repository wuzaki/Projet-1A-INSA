import settings as s
import pygame as pg
import time as t
import math

"""
Ce fichier contient la classe Player pour la gestion du personnage du joueur.
"""

# ==== Player ====
class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self._layer = 12  # plus petit que le joueur

        # ==== Position ====
        self.xy = pg.math.Vector2(x, y)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)
        self.rel = 0
        self.angle = 0

        # ==== Sprite ====
        self.image = self.load_image("assets/player.png")
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

    def move(self):
        keys = pg.key.get_pressed()
        dt = self.game.dt

        direction = pg.Vector2(0, 0)

        if keys[pg.K_z]:
            direction.y -= 1
        if keys[pg.K_s]:
            direction.y += 1
        if keys[pg.K_q]:
            direction.x -= 1
        if keys[pg.K_d]:
            direction.x += 1

        # évite boost diagonale
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.vel += direction * s.ACCEL * dt
        
        # friction progressive
        self.vel -= self.vel * s.FRICTION * dt

        # limite vitesse max
        if self.vel.length() > s.MAX_SPEED:
            self.vel.scale_to_length(s.MAX_SPEED)

        # stop micro-glissement
        if self.vel.length_squared() < 4:
            self.vel.xy = (0, 0)

        self.check_walls(dt)

        self.angle %= math.tau

    def check_walls(self, dt):
        walls = self.game.world_graph.get_walls()
        # Pour X
        self.xy.x += self.vel.x * dt
        self.sync_rects()
        if self.feet.collidelist(walls) != -1:
            self.xy.x -= self.vel.x * dt
            self.vel.x = 0
    
        # Pour Y
        self.xy.y += self.vel.y * dt
        self.sync_rects()
        if self.feet.collidelist(walls) != -1:
            self.xy.y -= self.vel.y * dt
            self.vel.y = 0

    def load_image(self, path):
        sprite_sheet = pg.image.load(path).convert_alpha()
        img = sprite_sheet.subsurface((0, 0, 32, 32))
        img.set_colorkey([0, 0, 0])
        return img

    def sync_rects(self):
        # Arrondi explicite pour éviter le jitter d'arrondi aléatoire
        self.rect.midbottom = self.xy.x, self.xy.y
        self.feet.midbottom = self.rect.midbottom

    def update(self):
        self.move()
        self.sync_rects()
