import settings as s
import pygame as pg
import time as t
import math

"""
Ce fichier contient la classe Weapon pour la gestion des armes et des projectiles.
"""

# ==== Weapon ====
class Weapon:
    COOLDOWN = {
        "single": 0.1, 
        "shotgun": 0.5
    }

    def __init__(self, game, owner, mode):
        self.game = game
        self.owner = owner
        self.cooldown = self.COOLDOWN.get(mode, 0.5)  # secondes entre deux tirs
        self.last_shot_time = 0
        self.mode = mode  # ou "single" ou "shotgun"

        # === ShotGun Specific ===
        self.pellets = 5
        self.spread_angle = math.radians(5)  # écart total entre les pellets

    def can_shoot(self):
        return t.time() - self.last_shot_time >= self.cooldown

    def shoot(self):
        if not self.can_shoot():
            return
        
        if self.mode == "single":
            projectile = Projectile(self.game, self.owner, self.owner.rect.center, self.owner.angle)
            self.game.world_graph.get_group().add(projectile)

        elif self.mode == "shotgun":
            for i in range(self.pellets):
                angle = self.owner.angle + (i - (self.pellets - 1) / 2) * self.spread_angle
                projectile = Projectile(self.game, self.owner, self.owner.rect.center, angle)
                self.game.world_graph.get_group().add(projectile)

        self.last_shot_time = t.time()


# ==== Projectiles =====
class Projectile(pg.sprite.Sprite):
    def __init__(self, game, owner, pos, angle):
        super().__init__()
        self.game = game
        self.owner = owner
        self._layer = 11  # plus petit que le joueur

        self.xy = pg.math.Vector2(pos)
        self.angle = angle
        self.speed = 400

        self.image = pg.Surface((8, 4), pg.SRCALPHA)
        pg.draw.rect(self.image, (255, 255, 0), (0, 0, 8, 4))
        self.image = pg.transform.rotate(self.image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=self.xy)

    def kill(self):
        super().kill()

    def update(self):
        dt = self.game.dt
        direction = pg.math.Vector2(math.cos(self.angle), math.sin(self.angle))
        self.xy += direction * self.speed * dt
        self.rect.center = self.xy

        # Check Walls
        if self.rect.collidelist(self.game.world_graph.get_walls()) != -1:
            self.kill()
            return

        if isinstance(self.owner, self.game.player.__class__):
            # Le joueur tire → on touche les ennemis
            for enemy in self.game.world_graph.get_enemies():
                if self.rect.colliderect(enemy.rect):
                    enemy.lose_health(25)
                    self.kill()
                    return
        else:
            # Un ennemi tire → on touche le joueur
            if self.rect.colliderect(self.game.player.rect):
                self.game.player.lose_health(10)
                self.kill()
