import settings as s
from .base import Interactable
import pygame as pg
from .portal import Portal
from .terminal import Terminal

"""
Ce fichier contient la classe Key, pour les clés.
"""

# ==== Key ====
class Key(Interactable):
    def __init__(self, game, x, y, w, h, name="", connected_item_id=""):
        super().__init__(game, x, y, w, h)
        self.game = game
        self.collision = False
        self.name = name
        self.connected_item_id = connected_item_id

        # print(self.name, self.connected_item_id)
        self.connected_item = None
        
        # ==== Sprite ====
        self.image = self.load_image("assets/interactables/key.png")

        # ==== Init Shadow ====
        self.shadow.__init__(self.game, self, width=18, height=6) # __init__ car pas les memes valeurs de width et height

    def get_connected_item(self):
        # print(self.game)
        for item in self.game.world_graph.get_interactables():
            if isinstance(item, (Terminal, Portal)) and item.name == self.connected_item_id:
                return item
        return None

    def update(self):
        self.shadow.sync_rects()
        
        if self.connected_item is None:
            self.connected_item = self.get_connected_item()

        if self.rect.colliderect(self.game.player.feet):
            # print("Key collected!")
            self.connected_item.get_access()  # Donne l'accès à l'item connecté (ex: ouvre un portail)
            self.game.world_graph.get_group().remove(self)
            self.kill()

            # Shadow
            self.shadow.kill()
            self.game.world_graph.get_group().remove(self.shadow)