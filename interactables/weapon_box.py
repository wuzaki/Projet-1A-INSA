import settings as s
from .base import Interactable
from utils.shadow import Shadow
import pygame as pg

from weapon import Weapon

# ==== WeaponBox ====
class WeaponBox(Interactable):
    def __init__(self, game, x, y, w, h, init_ammo=0, mode="shotgun"):
        super().__init__(game, x, y, w, h)
        self.collision = False
        self.init_ammo = int(init_ammo)
        self.mode = mode

        # ==== Sprite ====
        self.image = self.load_image(f"assets/interactables/{self.mode}.png")

        # ==== Add Shadow ====
        self.shadow = Shadow(self.game, self, width=20, height=6)

    def update(self):
        self.shadow.sync_rects()

        if self.rect.colliderect(self.game.player.feet):
            if not any(w.mode == self.mode for w in self.game.player.weapon_list):
                new_weapon = Weapon(self.game, self.game.player, self.mode, ammo_count=self.init_ammo)
                self.game.player.weapon_list.append(new_weapon)
                self.game.player.weapon = new_weapon
                self.kill()
                self.game.world_graph.get_group().remove(self)

                # Shadow
                self.shadow.kill()
                self.game.world_graph.get_group().remove(self.shadow)