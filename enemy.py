import settings as s
import pygame as pg
import math
import time as t

from weapon import Weapon
from utils.animation import AnimateSprite
from utils.shadow import Shadow

"""
Ce fichier contient la classe Enemy pour la gestion des ennemis.
"""

# ==== Enemy ====
class Enemy(AnimateSprite):
    PATH_RECALC_INTERVAL = 10 # frames entre deux recalculs
    PATH_GOAL_THRESHOLD = 1 # cellules de tolérance avant de recalculer

    def __init__(self, game, x, y):
        super().__init__("assets/player.png")
        self.game = game
        self.xy = pg.math.Vector2(x, y)
        # self.image = self.load_image("assets/player.png")
        self.image = self.images["down"][0]
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        self.angle = 0
        self.has_seen_player = False

        # Pathfinding + Weapon
        self.path = []
        self.health = 100
        self.weapon = Weapon(self.game, self, "enemy_single", ammo_count=15)
        self.last_seen_player_time = 0
        self.time_to_forget_player = 7 # temps en secondes après lequel l'ennemi oublie le joueur
        self.path_timer = 0
        # self.last_goal = None

        # ==== Add Shadow ====
        self.shadow = Shadow(self.game, self, width=20, height=6)

    def lose_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            # Shadow
            self.game.world_graph.get_group().remove(self.shadow)
            self.shadow.kill()
                    
            # Enemy
            self.game.world_graph.get_enemies().remove(self)
            self.kill()

    def load_image(self, path):
        img = pg.image.load(path).convert_alpha().subsurface((0, 0, 32, 32))
        return img
    
    # def goal_changed(self, goal):
    #     """Retourne True si le goal a suffisamment bougé pour recalculer."""
    #     if self.last_goal is None:
    #         return True
    #     dx = abs(goal[0] - self.last_goal[0])
    #     dy = abs(goal[1] - self.last_goal[1])
    #     return dx > self.PATH_GOAL_THRESHOLD or dy > self.PATH_GOAL_THRESHOLD

    # def refresh_path(self):
    #     """Recalcule le chemin si nécessaire (timer OU goal déplacé)."""
    #     self.path_timer += 1
    #     if self.path_timer < self.PATH_RECALC_INTERVAL:
    #         return

    #     goal = s.world_to_grid(self.game.player.feet.center)
    #     if not self.goal_changed(goal):
    #         # Le joueur n'a pas bougé de cellule → on repart sans recalculer
    #         self.path_timer = 0
    #         return

    #     start = s.world_to_grid(self.feet.center)
    #     self.path = self.game.pathfinding.find_path(start, goal)
    #     self.last_goal = goal
    #     self.path_timer = 0

    def refresh_path(self):
        self.path_timer += 1

        if self.path_timer >= self.PATH_RECALC_INTERVAL:
            start = s.world_to_grid(self.feet.center)
            goal = s.world_to_grid(self.game.player.feet.center)

            self.path = self.game.pathfinding.find_path(start, goal)

            self.path_timer = 0

    def move(self):
        self.refresh_path()
        # start = s.world_to_grid(self.feet.center)
        # goal = s.world_to_grid(self.game.player.feet.center)
        # self.path = self.game.pathfinding.find_path(start, goal)

        if not self.path:
            return
        
        target_cell = self.path[0]
        cell_world = s.grid_to_world(target_cell)
        target_pos = pg.math.Vector2(
            cell_world[0] + s.TILE_SIZE // 2,
            cell_world[1] + s.TILE_SIZE // 2
        )

        direction = target_pos - self.xy
        distance = direction.length()

        if distance < 4:
            self.xy = target_pos
            self.path.pop(0)
            return

        angle = math.atan2(direction.y, direction.x)

        # Animation du sprite
        if angle >= -math.pi / 4 and angle < math.pi / 4:
            self.switch_animation("right")
        elif angle >= math.pi / 4 and angle < 3 * math.pi / 4:
            self.switch_animation("down")
        elif angle >= 3 * math.pi / 4 or angle < -3 * math.pi / 4:
            self.switch_animation("left")
        else:
            self.switch_animation("up")

        move_vec = pg.math.Vector2(math.cos(angle), math.sin(angle))
        self.xy += move_vec * s.ENEMY_SPEED * self.game.dt

    def reload_ammo(self):
        if t.time() - self.weapon.last_shot_time >= 3:  # délai de rechargement
            self.weapon.ammo_count = 10

    def can_move(self):
        if self.ray_cast_player():
            self.has_seen_player = True
            self.last_seen_player_time = t.time()
            return True
        elif self.has_seen_player:
            if t.time() - self.last_seen_player_time <= self.time_to_forget_player:
                return True
            else:
                self.has_seen_player = False
                return False

    def shoot(self):
        if not self.can_shoot():
            return

    def run_logic(self):
        if self.weapon.ammo_count <= 0:
            self.reload_ammo()

        if self.can_move():
            direction = self.game.player.xy - self.xy
            if direction.length() > s.ENEMY_MOVE_MIN_DIST:
                self.move()
            if direction.length() <= s.ENEMY_SHOOT_MAX_DIST and self.ray_cast_player():
                self.weapon.shoot()

    def ray_cast_player(self):
        player_pos = self.game.player.xy
        direction = player_pos - self.xy
        distance = direction.length()
        if distance == 0:
            return True
        direction = direction.normalize()
        step_size = s.TILE_SIZE / 4
        steps = int(distance / step_size)
        pos = pg.math.Vector2(self.xy)
        walls = self.game.world_graph.get_walls()
        w, h = self.feet.width, self.feet.height

        for _ in range(steps):
            pos += direction * step_size
            test_rect = pg.Rect(0, 0, w, h)
            test_rect.midbottom = pos
            for wall in walls:
                if test_rect.colliderect(wall):
                    return False
        return True

    def update(self):
        self.angle = s.get_angle(self.rect.center, self.game.player.rect.center)
        self.run_logic()
        self.shadow.sync_rects()
        self.rect.midbottom = self.xy
        self.feet.midbottom = self.rect.midbottom

    def draw(self, screen):
        if self.health <= 0:
            return
        self.show_health(screen)
        # self.show_enemy_name(screen)

    def show_enemy_name(self, screen):
        zoom = self.game.world_graph.get_group()._map_layer.zoom
        font_text = pg.font.Font("assets/pixel_font.ttf", 8 * zoom).render("test", True, (255, 255, 255))
        font_rect = font_text.get_rect()

        cam = self.game.world_graph.get_group()._map_layer
        font_rect.center = cam.translate_point((self.rect.centerx, self.rect.centery - 28))

        screen.blit(font_text, font_rect)

    def show_health(self, screen):
        zoom = self.game.world_graph.get_group()._map_layer.zoom
        bar_width = 23 * zoom
        bar_height = 3 * zoom
        rect = pg.Rect(0, 0, bar_width, bar_height)

        cam = self.game.world_graph.get_group()._map_layer
        rect.center = cam.translate_point((self.rect.centerx, self.rect.centery - 20))

        pg.draw.rect(screen, (0, 0, 0), rect)
        pg.draw.rect(screen, s.ENEMY_COLOR_HEALTH_BAR, (rect.x, rect.y, rect.width * (self.health / 100), rect.height))
        # pg.draw.rect(screen, (255, 255, 255), rect, 1)
