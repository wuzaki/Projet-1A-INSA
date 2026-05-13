import settings as s
import pygame as pg
import math

"""
Ce fichier contient la classe Enemy pour la gestion des ennemis.
"""

# ==== Enemy ====
class Enemy(pg.sprite.Sprite):
    PATH_RECALC_INTERVAL = 20   # frames entre deux recalculs
    PATH_GOAL_THRESHOLD  = 1    # cellules de tolérance avant de recalculer

    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.xy = pg.math.Vector2(x, y)
        self.image = self.load_image("assets/player.png")
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        self.angle = 0
        self.has_seen_player = True

        # ---- cache pathfinding ----
        self.path = []
        # self.path_timer = 0
        # self.last_goal = None

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

    def move(self):
        # self.refresh_path()
        start = s.world_to_grid(self.feet.center)
        goal = s.world_to_grid(self.game.player.feet.center)
        self.path = self.game.pathfinding.find_path(start, goal)

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
        move_vec = pg.math.Vector2(math.cos(angle), math.sin(angle))
        self.xy += move_vec * s.ENEMY_SPEED * self.game.dt

    def update(self):
        self.move()
        self.rect.midbottom = self.xy
        self.feet.midbottom = self.rect.midbottom
