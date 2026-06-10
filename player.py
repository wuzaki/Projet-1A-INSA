import settings as s
import pygame as pg
import time as t
import math

from weapon import Weapon
from utils.animation import AnimateSprite
from utils.shadow import Shadow
from utils.weapon_zone import WeaponZone

"""
Ce fichier contient la classe Player pour la gestion du personnage du joueur.
"""

# ==== Player ====
class Player(AnimateSprite):
    def __init__(self, game, x, y):
        super().__init__("assets/pixil-frame-0.png")
        self.game = game
        self._layer = 12  # plus petit que le joueur

        # ==== Position ====
        self.xy = pg.math.Vector2(x, y)
        self.vel = pg.math.Vector2(0, 0)
        # self.acc = pg.math.Vector2(0, 0)
        self.rel = 0
        self.angle = 0

        # ==== Sprite ====
        # self.image = self.load_image("assets/player.png")
        # self.sprite_sheet = pg.image.load("assets/player.png").convert_alpha()
        # self.image = self.get_image(0, 0)
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

        # ==== Health and Weapon ====
        self.health = 100
        self.weapon_list = [Weapon(self.game, self, "knife")]
        self.weapon = self.weapon_list[0]

        # ==== Add Shadow / Others ====
        self.shadow = Shadow(self.game, self, width=20, height=6)
        self.weapon_zone = WeaponZone(self.game, self.weapon.mode)

    def lose_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.show_death()
            self.game.new_game()
            # self.kill()
        elif self.health > 100:
            self.health = 100

    def show_death(self):
        pg.draw.rect(self.game.screen, "black", self.game.screen.get_rect())
        temp_surf = s.get_text_surf("You died!", s.FONTS["pixel"][32])
        temp_rect = temp_surf.get_rect()
        temp_rect.center = self.game.screen.get_rect().center
        self.game.screen.blit(temp_surf, temp_rect)
        pg.display.flip()
        t.sleep(3)

    def move(self):
        keys = pg.key.get_pressed()
        dt = self.game.dt

        direction = pg.Vector2(0, 0)

        if keys[pg.K_q]:
            direction.x -= 1
            side = "left"
        if keys[pg.K_d]:
            direction.x += 1
            side = "right"
        if keys[pg.K_z]:
            direction.y -= 1
            side = "up"
        if keys[pg.K_s]:
            direction.y += 1
            side = "down"

        # évite boost diagonale
        if direction.length_squared() > 0:
            self.switch_animation(side) # Animation du sprite
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

    def get_image(self, x, y):
        image = pg.Surface([32, 32], pg.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def load_image(self, path):
        img = pg.image.load(path).convert_alpha().subsurface((0, 0, 32, 32)) # subsurface((0, 0, 32, 32))
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
        self.shadow.sync_rects()
        self.weapon.update()
        # self.switch_animation("down")

        if (self.weapon.ammo_count <= 0 and self.weapon.stock_ammo > 0 and t.time() - self.weapon.last_shot_time > self.weapon.reload_time):
            self.weapon.reload_ammo()

    def draw(self, screen):
        # self.show_angle(screen)
        # self.show_health(screen)
        # self.show_ammo_count(screen)
        # self.show_weapon_mode(screen)

        if self.weapon.ammo_count > 0:
            if not self.weapon.can_shoot():
                self.show_reload_weapon_timer(screen, s.PLAYER_COLOR_RELOAD_BAR,
                                            self.weapon.last_shot_time, self.weapon.cooldown)
        else:
            if (t.time() - self.weapon.last_shot_time < self.weapon.reload_time
                    and self.weapon.stock_ammo > 0):
                self.show_reload_weapon_timer(screen, "green",
                                            self.weapon.last_shot_time, self.weapon.reload_time)

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

    def show_reload_weapon_timer(self, screen, color, last_time, time):
        zoom = self.game.world_graph.get_group()._map_layer.zoom
        bar_width = 13 * zoom
        bar_height = 3 * zoom
        rect = pg.Rect(0, 0, bar_width, bar_height)

        cam = self.game.world_graph.get_group()._map_layer
        rect.center = cam.translate_point((self.rect.centerx, self.rect.centery - 20))

        pg.draw.rect(screen, (0, 0, 0), rect)
        pg.draw.rect(screen, color, (rect.x, rect.y, rect.width * (((t.time() - last_time) % time) / time), rect.height))
        # pg.draw.rect(screen, (255, 255, 255), rect, 1)
