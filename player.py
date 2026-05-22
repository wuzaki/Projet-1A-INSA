import settings as s
import pygame as pg
import time as t
import math

from weapon import Weapon

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

        # ==== Health and Weapon ====
        self.health = 100
        self.weapon = Weapon(self.game, self, "single", ammo_count=100)

    def lose_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            # self.kill()
            return

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

        # Get Angle
        result = self.get_angle_coord()
        self.angle = s.get_angle(result[0], result[1])

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
        img = pg.image.load(path).convert_alpha().subsurface((0, 0, 32, 32))
        return img

    def sync_rects(self):
        self.rect.midbottom = self.xy.x, self.xy.y
        self.feet.midbottom = self.rect.midbottom

    def get_angle_coord(self):
        cam = self.game.world_graph.get_group()._map_layer
        start_screen = cam.translate_point(self.rect.center)
        end_screen = pg.mouse.get_pos()

        return start_screen, end_screen

    def update(self):
        self.move()
        self.sync_rects()

    def draw(self, screen):
        self.show_angle(screen)
        self.show_health(screen)
        self.show_ammo_count(screen)

    def show_health(self, screen):
        s.show_basic_text(screen, f"Health: {self.health}", (10, 40))

    def show_ammo_count(self, screen):
        s.show_basic_text(screen, f"Ammo: {self.weapon.ammo_count}", (10, 60))

    def show_angle(self, screen):
        # ==== Angle Visualizer ====
        cam = self.game.world_graph.get_group()._map_layer  # caméra pyscroll
        length = 30
        
        start_world = self.rect.center
        end_world = (
             start_world[0] + length * math.cos(self.angle),
             start_world[1] + length * math.sin(self.angle)
        )

        start_screen = cam.translate_point(start_world)
        end_screen = cam.translate_point(end_world)

        pg.draw.line(screen, (220, 220, 220, 10), start_screen, end_screen, 2)
