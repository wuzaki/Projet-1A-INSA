import settings as s
import pygame as pg
import math

# ==== WeaponZone ====
class WeaponZone(pg.sprite.Sprite):
    def __init__(self, game, mode):
        super().__init__()
        self.game = game
        self._layer = 0
        self.mode = mode

        self.img_list = self.load_images("assets/weapon_zone")
        self.original_image = self.img_list[self.mode] # pg.image.load(f"assets/zone_{self.mode}.png").convert_alpha()
        # self.original_image.set_alpha(150)
        self.image = self.original_image
        self.rect = self.image.get_rect()

    def load_images(self, path):
        img_list = dict()
        for name in s.WEAPONS_DATA.keys():
            if "enemy" not in name:
                img = pg.image.load(f"{path}/zone_{name}.png").convert_alpha()
                w, h = img.get_size()
                ratio = w/h
                scale = ratio/24
                img = pg.transform.smoothscale(img, (w * scale, h * scale))
                img_list[name] = img
        return img_list

    def update(self):
        angle = self.game.player.angle

        self.original_image = self.img_list[self.game.player.weapon.mode]
        
        # Le bord gauche de l'image originale = origine du joueur
        # On calcule où se trouve le centre de l'image après rotation
        if self.game.player.weapon.mode != "knife":
            self.image = pg.transform.rotozoom(self.original_image, -math.degrees(angle), 1)
            w = self.original_image.get_width()
            offset = pg.math.Vector2(w // 2, 0).rotate(math.degrees(angle))
            
            self.rect = self.image.get_rect(center=(
                self.game.player.rect.centerx + offset.x,
                self.game.player.rect.centery + offset.y  
            ))
        else:
            self.image = self.img_list["knife"]  # <-- manquant
            self.rect = self.image.get_rect(center=self.game.player.feet.midtop)
            self.rect.center = self.game.player.feet.midtop
