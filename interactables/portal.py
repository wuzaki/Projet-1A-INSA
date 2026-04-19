from .base import Interactable
from pathfinding import PathFinding

"""
Ce fichier contient la classe Portal, pour les portails de téléportation.
By Luc ALLEBEE
"""

# ==== Portal ====
class Portal(Interactable):
    def __init__(self, game, x, y, w, h, from_map=None, target=None):
        super().__init__(game, x, y, w, h)
        self.from_map = from_map
        self.target = target

    def update(self):
        world = self.game.world_graph

        if self.rect.colliderect(self.game.player.feet):
            if self.target not in world.maps:
                world.load_map(self.target)

            world.current_map = self.target
            self.pathfinding = PathFinding(self.game.world_graph.get_tile_map())
            world.spawn_player(self.from_map)  # place le joueur sur le point de spawn correct
            # print("Current map:", world.current_map, "Spawn:", self.from_map)