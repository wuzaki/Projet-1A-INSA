import settings as s
from .base import Interactable
import pygame as pg

"""
Ce fichier contient la classe Health, pour la santé.
"""

# ==== Health ====
class Health(Interactable):
    def __init__(self, game, x, y, w, h, amount=25):
        super().__init__(game, x, y, w, h)
        self.collision = False
        self.amount = int(amount)

        # ==== Sprite ====
        self.image = self.load_image("assets/interactables/health.png")

    def update(self):
        self.shadow.sync_rects()

        if self.rect.colliderect(self.game.player.feet):
            # print("Health collected!")
            self.game.player.lose_health(-self.amount)  # ou une autre quantité selon le type de munition
            self.kill()
            self.game.world_graph.get_group().remove(self)

            # Shadow
            self.shadow.kill()
            self.game.world_graph.get_group().remove(self.shadow)