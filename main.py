import settings as s
import pygame as pg

from maps import WorldGraph
from player import Player

from pathfinding import PathFinding

"""
Ce fichier contient la classe Game pour la gestion principale du jeu.
By Luc ALLEBEE
"""

# ==== Game ====
class Game:
    def __init__(self, w, h):
        self.screen = pg.display.set_mode((w, h))
        self.dt = 1

        # Classes
        self.player = Player(self, 0, 0)

        self.world_graph = WorldGraph(self)
        self.world_graph.load_map("map_test")
        self.pathfinding = PathFinding(self.world_graph.get_tile_map())
        self.world_graph.spawn_player("player")

    def process(self):
        self.screen.fill((0, 0, 0))
        self.world_graph.process()

    def show_fps(self, clock):
        font = pg.font.SysFont("Arial", 28)
        fps_text = font.render(f"FPS: {round(clock.get_fps(), 2)}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))

    def draw(self):
        self.world_graph.draw(self.screen)

    def run(self):
        clock = pg.time.Clock()
        while True:
            pg.display.set_caption(f"Projet Wuevia (Prototype) | FPS: {round(clock.get_fps(), 2)}")
            self.process()
            self.draw()
            self.show_fps(clock)
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return False
            clock.tick(s.FPS)
            self.dt = clock.get_time() / 1000  # Convert ms to seconds


# ==== Main ====
if __name__ == "__main__":
    pg.init()
    Game(s.WIDTH, s.HEIGHT).run()
    pg.quit()