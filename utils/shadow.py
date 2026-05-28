import settings as s
import pygame as pg

# ==== Shadow ====
class Shadow(pg.sprite.Sprite):
    def __init__(self, game, target, width, height):
        super().__init__()
        self.game = game
        self.target = target
        self._layer = 9  # juste sous le joueur (layer 12)

        self.image = pg.Surface((width, height), pg.SRCALPHA)
        pg.draw.ellipse(self.image, (0, 0, 0, 120), self.image.get_rect())
        self.rect = self.image.get_rect()

    def sync_rects(self):
        # Suit les pieds du joueur
        self.rect.center = self.target.rect.midbottom