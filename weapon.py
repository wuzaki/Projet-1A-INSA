import settings as s
import pygame as pg
import time as t
import math
import random as rd

"""
Ce fichier contient la classe Weapon pour la gestion des armes et des projectiles.
"""

# ==== Weapon ====
class Weapon:
    def __init__(self, game, owner, mode, ammo_count=10):
        self.game = game
        self.owner = owner
        self.cooldown = s.WEAPONS_DATA.get(mode, {"cooldown": 0.5})["cooldown"]  # secondes entre deux tirs
        self.last_shot_time = 0
        self.mode = mode  # ou "single" ou "shotgun"
        self.ammo_count = ammo_count  # pour les armes à munitions limitées
        self.stock_ammo = 0 # s.WEAPONS_DATA.get(mode, {"max_ammo": 10})["max_ammo"]  # pour les armes à munitions limitées
        self.max_ammo = s.WEAPONS_DATA.get(mode, {"max_ammo": 10})["max_ammo"]

        # === ShotGun Specific ===
        self.pellets = 5
        self.spread_angle = math.radians(10)  # écart total entre les pellets

    def can_shoot(self):
        return t.time() - self.last_shot_time >= self.cooldown and self.ammo_count > 0
    
    def reload_ammo(self):
        if self.ammo_count >= self.max_ammo:
            return  # chargeur déjà plein

        if self.stock_ammo <= 0:
            return  # plus de munitions en réserve

        needed = self.max_ammo - self.ammo_count
        to_reload = min(needed, self.stock_ammo)

        self.ammo_count += to_reload
        self.stock_ammo -= to_reload

    def shoot(self):
        if not self.can_shoot():
            return
        
        if self.mode == "knife":
            # Attaque de mêlée : on vérifie les ennemis proches
            for enemy in self.game.world_graph.get_enemies():
                hitbox = enemy.rect.inflate(20, 20)
                if self.owner.rect.colliderect(hitbox):
                    enemy.lose_health(s.WEAPONS_DATA.get(self.mode, {"damage": 50})["damage"])

        elif self.mode in ["single", "enemy_single"]:
            # 0.12 = environ 7 degre
            ecart = 0 # 0.3
            spread = rd.uniform(-ecart, ecart) if self.mode == "enemy_single" else 0
            projectile = Projectile(self.game, self.owner, self.owner.rect.center, self.owner.angle + spread, damage=s.WEAPONS_DATA.get(self.mode, {"damage": 25})["damage"])
            self.game.world_graph.get_group().add(projectile)
        
        # elif self.mode in ["single", "enemy_single"]:
        #     projectile = Projectile(self.game, self.owner, self.owner.rect.center, self.owner.angle, damage=s.WEAPONS_DATA.get(self.mode, {"damage": 25})["damage"])
        #     self.game.world_graph.get_group().add(projectile)

        elif self.mode in ["shotgun", "enemy_shotgun"]:
            for i in range(self.pellets):
                angle = self.owner.angle + (i - (self.pellets - 1) / 2) * self.spread_angle
                projectile = Projectile(self.game, self.owner, self.owner.rect.center, angle, damage=s.WEAPONS_DATA.get(self.mode, {"damage": 10})["damage"])
                self.game.world_graph.get_group().add(projectile)

        self.last_shot_time = t.time()

        # Loss Ammo Player
        if self.mode != "knife":
            if self.mode == "shotgun":
                self.ammo_count -= self.pellets
            else:
                self.ammo_count -= 1

    def update(self):
        mouse = pg.mouse.get_pressed()
        if mouse[0]:
            self.shoot()


# ==== Projectiles =====
class Projectile(pg.sprite.Sprite):
    def __init__(self, game, owner, pos, angle, damage=25):
        super().__init__()
        self.game = game
        self.owner = owner
        self._layer = 10  # plus petit que le joueur
        self.damage = damage

        self.xy = pg.math.Vector2(pos)
        self.angle = angle
        self.speed = s.PROJECTILE_SPEED

        self.image = pg.Surface((8, 4), pg.SRCALPHA) # self.load_img("assets/bullet.png")
        pg.draw.rect(self.image, (255, 255, 0), (0, 0, 8, 4))
        self.image = pg.transform.rotate(self.image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=self.xy)

    def load_img(self, path):
        img = pg.image.load(path).convert_alpha()
        return pg.transform.scale(img, (14, 6))

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
                if self.game.player.weapon.mode != "knife":
                    hitbox = enemy.rect
                else:
                    hitbox = enemy.feet # Collision restreinte pour plus de réaliste

                if self.rect.colliderect(hitbox):
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
