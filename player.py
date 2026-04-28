import settings as s
import pygame as pg
import time as t
import math

"""
Ce fichier contient la classe Player pour la gestion du personnage du joueur.
By Luc ALLEBEE
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
        self.angle = 0

        # ==== Sprite ====
        self.image = self.load_image("assets/player.png")
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

    def move(self):
        keys = pg.key.get_pressed()
        dt = self.game.dt

        # reset accel
        self.acc = pg.Vector2(0, 0)

        direction = pg.Vector2(math.cos(self.angle), math.sin(self.angle))

        # ==== INPUT ====
        if keys[pg.K_UP]:
            self.acc += direction * s.ACC_STRENGTH
        if keys[pg.K_DOWN]:
            self.acc -= direction * s.ACC_STRENGTH

        if keys[pg.K_LEFT]:
            self.angle -= s.ROT_SPEED * dt
        if keys[pg.K_RIGHT]:
            self.angle += s.ROT_SPEED * dt

        # ==== FRICTION ====
        self.acc += self.vel * s.FRICTION

        # ==== PHYSIQUE ====
        self.vel += self.acc * dt

        # limite vitesse
        if self.vel.length() > s.SPEED:
            self.vel.scale_to_length(s.SPEED)

        self.check_walls(dt)

        self.angle %= math.tau

    def check_walls(self, dt):
        walls = self.game.world_graph.get_walls()
        # Pour X
        self.xy.x += self.vel.x * dt
        self.update()
        if self.feet.collidelist(walls) != -1:
            self.xy.x -= self.vel.x * dt
            self.vel.x = 0
    
        # Pour Y
        self.xy.y += self.vel.y * dt
        self.update()
        if self.feet.collidelist(walls) != -1:
            self.xy.y -= self.vel.y * dt
            self.vel.y = 0

    def load_image(self, path):
        sprite_sheet = pg.image.load(path).convert_alpha()
        img = sprite_sheet.subsurface((0, 0, 32, 32))
        img.set_colorkey([0, 0, 0])
        return img

    def update(self):
        self.rect.midbottom = self.xy
        self.feet.midbottom = self.rect.midbottom
