import settings as s
from .base import Interactable
import pygame as pg

"""
Ce fichier contient la classe Ammo, pour les munitions.
"""

# ==== Ammo ====
class Ammo(Interactable):
    def __init__(self, game, x, y, w, h, count=10):
        super().__init__(game, x, y, w, h)
        self.collision = False
        self.count = int(count)

        # ==== Sprite ====
        self.image = self.load_image("assets/interactables/ammo.png")

    def update(self):
        if self.rect.colliderect(self.game.player.feet):
            # print("Ammo collected!")
            if self.game.player.weapon.mode != "knife":
                self.game.player.weapon.stock_ammo += self.count  # ou une autre quantité selon le type de munition
                self.kill()
                self.game.world_graph.get_group().remove(self)