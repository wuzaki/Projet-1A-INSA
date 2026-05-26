import settings as s
import pygame as pg
import time as t
import math

"""
Ce fichier contient la classe Weapon pour la gestion des armes et des projectiles.
"""

# ==== Weapon ====
class Weapon:
    def __init__(self, game, owner, mode, ammo_count=10):
        self.game = game
        self.owner = owner
        self.cooldown = s.COOLDOWN.get(mode, {"cooldown": 0.5})["cooldown"]  # secondes entre deux tirs
        self.last_shot_time = 0
        self.mode = mode  # ou "single" ou "shotgun"
        self.ammo_count = ammo_count  # pour les armes à munitions limitées
        self.max_ammo = s.COOLDOWN.get(mode, {"max_ammo": 10})["max_ammo"]  # pour les armes à munitions limitées

        # === ShotGun Specific ===
        self.pellets = 5
        self.spread_angle = math.radians(5)  # écart total entre les pellets

    def can_shoot(self):
        return t.time() - self.last_shot_time >= self.cooldown and self.ammo_count > 0

    def shoot(self):

        if not self.can_shoot():
            return
        
        if self.mode == "kniffe":
            # Attaque de mêlée : on vérifie les ennemis proches
            for enemy in self.game.world_graph.get_enemies():
                hitbox = enemy.rect.inflate(20, 20)
                if self.owner.rect.colliderect(hitbox):
                    enemy.lose_health(s.COOLDOWN.get(self.mode, {"damage": 50})["damage"])
        
        elif self.mode in ["single", "enemy_single"]:
            projectile = Projectile(self.game, self.owner, self.owner.rect.center, self.owner.angle, damage=s.COOLDOWN.get(self.mode, {"damage": 25})["damage"])
            self.game.world_graph.get_group().add(projectile)

        elif self.mode in ["shotgun", "enemy_shotgun"]:
            for i in range(self.pellets):
                angle = self.owner.angle + (i - (self.pellets - 1) / 2) * self.spread_angle
                projectile = Projectile(self.game, self.owner, self.owner.rect.center, angle, damage=s.COOLDOWN.get(self.mode, {"damage": 10})["damage"])
                self.game.world_graph.get_group().add(projectile)

        self.last_shot_time = t.time()

        if self.mode != "kniffe":
            self.ammo_count -= 1


# ==== Projectiles =====
class Projectile(pg.sprite.Sprite):
    def __init__(self, game, owner, pos, angle, damage=25):
        super().__init__()
        self.game = game
        self.owner = owner
        self._layer = 11  # plus petit que le joueur
        self.damage = damage

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
                    enemy.lose_health(self.damage)
                    self.kill()
                    return
        else:
            # Un ennemi tire → on touche le joueur
            hitbox = self.game.player.rect.copy()
            hitbox.size = (
                hitbox.width // 1.5,
                hitbox.height // 1.5
            )
            if self.rect.colliderect(hitbox):
                self.game.player.lose_health(self.damage)
                self.kill()
