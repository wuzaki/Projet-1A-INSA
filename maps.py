import settings as s
import pygame as pg
import pytmx
import pyscroll
from dataclasses import dataclass
import math

from interactables import Interactable, Portal, Terminal, Ammo
from enemy import Enemy

"""
Ce fichier contient la classe WorldGraph, pour la gestion des maps et de leurs objets.
"""

# ==== Map ====
@dataclass
class Map:
    name : str
    tmx_data : pytmx.TiledMap
    group : pyscroll.PyscrollGroup
    walls : list[pg.Rect]
    interactables : list[Interactable]
    enemies : list[pg.sprite.Sprite]


# ==== WorldGraph ====
class WorldGraph:
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.current_map = "map_test"
        self.maps = dict()
        self.tile_maps = dict() # Matrice de 0 et 1 pour l'algorithme A*

        self.load_map("map_test", zoom=1.9)
        self.spawn_player("player")

    def spawn_player(self, name):
        spawn_point = self.get_object_by_name(name)
        self.player.xy = pg.math.Vector2(spawn_point.x, spawn_point.y)

    def load_map(self, name, zoom=2, default_layer=8):
        # Load Map Data
        tmx_data = pytmx.util_pygame.load_pygame(f"assets/maps/{name}/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, (s.WIDTH, s.HEIGHT))
        map_layer.zoom = zoom

        # Get Walls
        walls = []
        interactables = []
        enemies = []
        for obj in tmx_data.objects:
            if obj.type == "collision":
                walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "portal":
                interactables.append(Portal(self.game, obj.x, obj.y, obj.width, obj.height, name, obj.name))
            elif obj.type == "terminal":
                interactables.append(Terminal(self.game, obj.x, obj.y, obj.width, obj.height, name, obj.name))
            elif obj.type == "ammo":
                interactables.append(Ammo(self.game, obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "enemy":
                enemies.append(Enemy(self.game, obj.x, obj.y))

        self.add_interactable_collision(walls, interactables)  # Ajouter les collisions des interactables aux murs

        # Dessiner les différents calques
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=default_layer, sort=True)
        [group.add(interactable) for interactable in interactables]
        [group.add(enemy) for enemy in enemies]
        group.add(self.player)

        self.maps[name] = Map(name, tmx_data, group, walls, interactables, enemies)
        self.tile_maps[name] = self.generate_tile_map(tmx_data, tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight, s.TILE_SIZE)

    def add_interactable_collision(self, walls, interactables):
        [walls.append(interactable.get_rect_collision()) for interactable in interactables if interactable.collision]

    def get_map(self):
        return self.maps[self.current_map]

    def get_walls(self):
        return self.get_map().walls
    
    def get_interactables(self):
        return self.get_map().interactables
    
    def get_enemies(self):
        return self.get_map().enemies
    
    def get_tile_map(self):
        return self.tile_maps[self.current_map]

    def get_group(self):
        return self.get_map().group
    
    def get_object_by_name(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)

    def process(self):
        self.get_group().update()
        # [enemy.move() for enemy in self.get_enemies() if enemy.has_seen_player]

    def draw(self, screen):
        group = self.get_group()
        group.center(self.player.rect.center)
        group.draw(screen)

        # ==== Angle Visualizer ====
        # cam = group._map_layer  # caméra pyscroll
        # length = 15
        
        # start_world = self.player.feet.center
        # end_world = (
        #     start_world[0] + length * math.cos(self.player.angle),
        #     start_world[1] + length * math.sin(self.player.angle)
        # )

        # start_screen = cam.translate_point(start_world)
        # end_screen = cam.translate_point(end_world)

        # pg.draw.line(screen, (220, 220, 220, 10), start_screen, end_screen, 2)

    def generate_tile_map(self, tmx_data, width, height, tile_size):
        cols = width // tile_size
        rows = height // tile_size
        grid = [[0 for _ in range(cols)] for _ in range(rows)]

        # Marquer les murs
        for obj in tmx_data.objects:
            if obj.type == "collision":
                start_x = int(obj.x // tile_size)
                start_y = int(obj.y // tile_size)
                end_x = int((obj.x + obj.width - 1) // tile_size)
                end_y = int((obj.y + obj.height - 1) // tile_size)
                
                for y in range(start_y, end_y+1):
                    for x in range(start_x, end_x+1):
                        if 0 <= x < cols and 0 <= y < rows:
                            grid[y][x] = 1  # 1 = mur
        
        for interactable in self.get_map().interactables:
            if interactable.collision:
                rect = interactable.get_rect_collision()

                start_x = int(rect.x // tile_size)
                start_y = int(rect.y // tile_size)
                end_x = int((rect.x + rect.width - 1) // tile_size)
                end_y = int((rect.y + rect.height - 1) // tile_size)

                for y in range(start_y, end_y + 1):
                    for x in range(start_x, end_x + 1):
                        if 0 <= x < cols and 0 <= y < rows:
                            grid[y][x] = 1

        return grid