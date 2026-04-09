import settings as s
import pygame as pg
import math

"""
Ce fichier contient la classe Enemy pour la gestion des ennemis.
By Luc ALLEBEE
"""

# ==== Enemy ====
class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.xy = pg.math.Vector2(x, y)
        self.image = self.load_image("assets/player.png")
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        self.angle = 0
        self.has_seen_player = False

    def load_image(self, path):
        img = pg.image.load(path).convert_alpha().subsurface((0,0,32,32))
        return img
    
    def move(self):
        start = s.world_to_grid(self.feet.center, s.TILE_SIZE)
        goal = s.world_to_grid(self.game.player.feet.center, s.TILE_SIZE)
        path = self.game.pathfinding.find_path(start, goal)

        if not path:
            return
        
        target_cell = path[0]
        cell_world = s.grid_to_world(target_cell, s.TILE_SIZE)
        target_pos = pg.math.Vector2(cell_world[0] + s.TILE_SIZE//2, cell_world[1] + s.TILE_SIZE//2)
        
        direction = target_pos - self.xy
        angle = math.atan2(direction.y, direction.x)
        distance = direction.length()
        if distance < 4:
            self.xy = target_pos
            self.path.pop(0)
            return
       
        move_vec = pg.math.Vector2(math.cos(angle), math.sin(angle))
        self.xy += move_vec * s.ENEMY_SPEED

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

    def update(self):
        self.has_seen_player = self.ray_cast_player()
        self.rect.midbottom = self.xy
        self.feet.midbottom = self.rect.midbottom