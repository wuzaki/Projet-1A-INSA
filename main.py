import settings as s
import pygame as pg

from maps import WorldGraph
from player import Player
from utils.weapon_zone import WeaponZone
from pathfinding import PathFinding
from utils.hud import PlayerHUD

"""
Ce fichier contient la classe Game pour la gestion principale du jeu.
"""

# ==== Game ====
class Game:
    def __init__(self, w, h):
        self.screen = pg.display.set_mode((w, h), pg.NOFRAME)
        self.dt = 1
        pg.mouse.set_visible(False)
        self.cursor_img = pg.image.load("assets/cursor.png").convert_alpha()
        self.cursor_img = pg.transform.scale(self.cursor_img, (42, 42))
        cursor = pg.Cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
        pg.mouse.set_cursor(cursor)

        # Classes
        self.player = Player(self, 0, 0)
        self.world_graph = WorldGraph(self)
        self.pathfinding = PathFinding(self.world_graph.get_tile_map())

        self.hud = PlayerHUD(self)

    def new_game(self):
        self.player = Player(self, 0, 0)
        self.world_graph = WorldGraph(self)
        self.pathfinding = PathFinding(self.world_graph.get_tile_map())

    def process(self):
        self.screen.fill((0, 0, 0))
        self.world_graph.process()

        # Truc rapide pour Gam'INSA
        if self.world_graph.current_map == "beta" and len(self.world_graph.get_enemies()) <= 0:
            self.new_game()

    def draw(self):
        self.world_graph.draw(self.screen)
        self.player.draw(self.screen)
        [enemy.draw(self.screen) for enemy in self.world_graph.get_enemies()]

        # Curseur
        mouse_pos = pg.mouse.get_pos()
        self.screen.blit(self.cursor_img, self.cursor_img.get_rect(center=mouse_pos))

        self.hud.draw(self.screen)

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
                    # if event.button == 1:  # clic gauche
                    #     self.player.weapon.shoot()
                    if event.button == 3:  # clic droit
                        self.player.weapon.reload_ammo()
                
                # Switch d'armes
                elif event.type == pg.MOUSEWHEEL:
                    idx = self.player.weapon_list.index(self.player.weapon)
                    idx = (idx + event.y) % len(self.player.weapon_list)
                    self.player.weapon = self.player.weapon_list[idx]
                    
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