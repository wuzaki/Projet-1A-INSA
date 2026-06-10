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

    def play_map(self):
        self.music_test.play(0)
