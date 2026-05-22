import settings as s
from .base import Interactable
import pygame as pg

"""
Ce fichier contient la classe Key, pour les clés.
"""

# ==== Key ====
class Key(Interactable):
    def __init__(self, game, x, y, w, h):
        super().__init__(game, x, y, w, h)
        self.collision = False

        # ==== Sprite ====
        self.image = self.load_image("assets/interactables/key.png")