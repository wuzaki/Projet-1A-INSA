import settings as s
import pygame as pg

"""
Ce fichier contient la classe Sounds pour la gestion de la musiques et des effets sonores.
"""

# ==== Sounds ====
class Sounds:
    def __init__(self, game):
        self.game = game
        self.music_test = pg.mixer.Sound("assets/sounds/music_test.mp3")
        self.single_shoot = pg.mixer.Sound("assets/sounds/single_shoot.mp3")
        self.shotgun_shoot = pg.mixer.Sound("assets/sounds/shotgun_shoot.mp3")
        self.walk = pg.mixer.Sound("assets/sounds/walk.mp3")
        self.reload = pg.mixer.Sound("assets/sounds/reload.mp3")
        self.get_item = pg.mixer.Sound("assets/sounds/get_item.mp3")
        self.health = pg.mixer.Sound("assets/sounds/health.mp3")

        # Set Volume
        self.single_shoot.set_volume(0.15)
        self.shotgun_shoot.set_volume(0.15)
        self.walk.set_volume(0.25)
        self.reload.set_volume(0.3)
        self.get_item.set_volume(0.3)
        self.health.set_volume(0.3)

    def play_map(self):
        self.music_test.play(-1)

    def single(self):
        self.single_shoot.play(0)

    def shotgun(self):
        self.shotgun_shoot.play(0)

    def play_walk(self):
        self.walk.play(-1)

    def play_reload(self):
        self.reload.play(0)

    def play_item(self):
        self.get_item.play(0)

    def play_health(self):
        self.health.play(0)
