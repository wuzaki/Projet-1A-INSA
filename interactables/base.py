import settings as s
import pygame as pg

from utils.shadow import Shadow


# ==== Interactable ====
class Interactable(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, collision=False):
        super().__init__()
        self.game = game
        self.image = pg.Surface((w, h), pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collision = collision
        self._layer = 10  # plus petit que le joueur

        # ==== Add Shadow ====
        self.shadow = Shadow(self.game, self, width=20, height=6)

    def load_image(self, path):
        image = pg.image.load(path).convert_alpha()
        return pg.transform.scale(image, (self.rect.width, self.rect.height))
    
    def get_rect_collision(self):
        return pg.Rect(self.rect.x+5, self.rect.y+5, self.rect.width-10, self.rect.height-10) # pour éviter les collisions trop précises sur les bords  