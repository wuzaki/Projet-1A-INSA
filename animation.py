import settings as s
import pygame as pg

"""
Ce fichier contient la classe Animation pour la gestion des animations du jeu.
"""

# ==== Animation ====
class AnimateSprite(pg.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.sprite_sheet =  pg.image.load(path).convert_alpha()
        self.animation_index = 0
        self.clock = 0
        self.images = {
            "down": self.get_images(0),
            "left": self.get_images(32),
            "right": self.get_images(64),
            "up": self.get_images(96)
        }
        self.animation_name = "down"
        self.speed_anim = 850

    def switch_animation(self, name):
        self.animation_name = name
        self.image = self.images[name][self.animation_index]

        self.clock += self.speed_anim * self.game.dt

        if self.clock >= 100:
            self.animation_index += 1
            self.clock = 0

        self.animation_index %= len(self.images[name])
    
    def get_images(self, y):
        images = []
        for i in range(3):
            x = i * 32
            image = self.get_image(x, y)
            images.append(image)
        return images

    def get_image(self, x, y):
        image = pg.Surface([32, 32], pg.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image