import heapq
import pygame as pg
import settings as s
import time as t
import math
from collections import deque

class Enemy(pg.sprite.Sprite):
    PATH_RECALC_DELAY = 0.2 # Augmenté pour l'optimisation

    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.xy = pg.math.Vector2(x, y)
        self.image = self.load_image("assets/player.png")
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

        self.path = []
        self.last_path_calc = t.time()
        self.has_seen_player = False
        self.angle = 0

    def load_image(self, path):
        # Utilise convert_alpha() UNE SEULE FOIS au chargement global, pas par ennemi
        img = pg.image.load(path).convert_alpha().subsurface((0,0,32,32))
        return img

    def update(self):
        # Logique de vision simplifiée
        if not self.has_seen_player:
            if self.ray_cast_player():
                self.has_seen_player = True
        
        if self.has_seen_player:
            self.move()

        self.rect.midbottom = self.xy
        self.feet.midbottom = self.rect.midbottom

    def move(self):
        now = t.time()
        tile_size = s.TILE_SIZE
        player = self.game.player

        # ==== 1. Recalcul du chemin (optimisé) ====
        if now - self.last_path_calc > self.PATH_RECALC_DELAY:
            start = s.world_to_grid(self.rect.center, tile_size)
            raw_goal = s.world_to_grid(player.rect.center, tile_size)
            goal = get_nearest_free_cell(self.game.world_graph.get_tile_map(), raw_goal)
            self.path = self.game.pathfinding.find_path(start, goal)
            self.last_path_calc = now

        # ==== 2. Aucun chemin → rien à faire ====
        if not self.path:
            return

        # ==== 3. Cible actuelle ====
        target_cell = self.path[0]
        cell_world = s.grid_to_world(target_cell, tile_size)
        target_pos = pg.math.Vector2(cell_world[0] + tile_size//2, cell_world[1] + tile_size//2)

        current_pos = pg.math.Vector2(self.rect.center)
        direction = target_pos - current_pos
        distance = direction.length()
        if distance < 4:
            self.xy = target_pos
            self.path.pop(0)
            return

        # ==== 4. Angle vers la cible ====
        target_angle = math.atan2(direction.y, direction.x)  # radians
        # rotation fluide
        angle_diff = (target_angle - self.angle + math.pi) % (2*math.pi) - math.pi
        max_turn = 3.0 * self.game.dt  # rad/s, ajuste la vitesse de rotation
        if abs(angle_diff) > max_turn:
            angle_diff = max_turn if angle_diff > 0 else -max_turn
        self.angle += angle_diff

        # ==== 5. Mouvement selon l'angle ====
        move_vec = pg.math.Vector2(math.cos(self.angle), math.sin(self.angle))
        self.xy += move_vec * s.ENEMY_SPEED * self.game.dt

    def ray_cast_player(self):
        player_pos = self.game.player.xy
        direction = player_pos - self.xy
        distance = direction.length()
        if distance == 0: 
            return True
        direction = direction.normalize()
        steps = int(distance/(s.TILE_SIZE/4))
        pos = pg.math.Vector2(self.xy)
        walls = self.game.world_graph.get_walls()
        for _ in range(steps):
            pos += direction*(s.TILE_SIZE/4)
            test_rect = pg.Rect(0,0,self.feet.width,self.feet.height)
            test_rect.midbottom = pos
            for wall in walls:
                if test_rect.colliderect(wall):
                    return False
        return True

def get_nearest_free_cell(grid, goal):
    x, y = goal
    rows = len(grid)
    cols = len(grid[0])
    if grid[y][x] == 0:
        return goal  # déjà libre

    # BFS simple pour trouver la cellule libre la plus proche
    visited = set()
    queue = deque([goal])

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))

        if 0 <= cx < cols and 0 <= cy < rows and grid[cy][cx] == 0:
            return (cx, cy)

        # voisins 4 directions
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                queue.append((nx, ny))

    # fallback : retourne le goal original si rien de libre (extrême)
    return goal