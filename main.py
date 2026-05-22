import settings as s
import pygame as pg

from maps import WorldGraph
from player import Player

from pathfinding import PathFinding

"""
Ce fichier contient la classe Game pour la gestion principale du jeu
"""

# ==== Game ====
class Game:
    def __init__(self, w, h):
        self.screen = pg.display.set_mode((w, h), pg.NOFRAME)
        self.dt = 1

        # Classes
        self.player = Player(self, 0, 0)
        self.world_graph = WorldGraph(self)
        self.pathfinding = PathFinding(self.world_graph.get_tile_map())

    def process(self):
        self.screen.fill((0, 0, 0))
        self.world_graph.process()

    def draw(self):
        self.world_graph.draw(self.screen)
        self.player.draw(self.screen)
        [enemy.draw(self.screen) for enemy in self.world_graph.get_enemies()]

    def run(self):
        clock = pg.time.Clock()
        while True:
            # Event Loop
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # clic gauche
                        self.player.weapon.shoot()
                    
            # ==== Update ====
            self.dt = min(clock.tick(s.FPS) / 1000, 0.05)
            self.process()
            self.draw()
            s.show_fps(self.screen, clock)
            pg.display.flip()


# ==== Main ====
if __name__ == "__main__":
    pg.init()
    Game(s.WIDTH, s.HEIGHT).run()
    pg.quit()