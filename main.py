import settings as s
import pygame as pg
import time as t

from maps import WorldGraph
from player import Player
from utils.weapon_zone import WeaponZone
from pathfinding import PathFinding
from utils.hud import PlayerHUD
from utils.sounds import Sounds

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
        self.sounds = Sounds(self)

        self.hud = PlayerHUD(self)

    def new_game(self):
        self.player = Player(self, 0, 0)
        self.world_graph = WorldGraph(self)
        self.pathfinding = PathFinding(self.world_graph.get_tile_map())

    def show_death(self):
        pg.draw.rect(self.screen, "black", self.screen.get_rect())
        temp_surf = s.get_text_surf("You died!", s.FONTS["pixel"][32])
        temp_rect = temp_surf.get_rect()
        temp_rect.center = self.screen.get_rect().center
        self.screen.blit(temp_surf, temp_rect)
        pg.display.flip()
        t.sleep(3)
        self.new_game()
        self.sounds.music_test.stop()
        self.sounds.play_map()

    def show_win(self):
        pg.draw.rect(self.screen, "black", self.screen.get_rect())
        temp_surf = s.get_text_surf("You win! Good job!", s.FONTS["pixel"][32])
        temp_rect = temp_surf.get_rect()
        temp_rect.center = self.screen.get_rect().center
        self.screen.blit(temp_surf, temp_rect)
        pg.display.flip()
        t.sleep(3)
        self.new_game()
        self.sounds.music_test.stop()
        self.sounds.play_map()

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
        self.sounds.play_map()
        while True:
            # Event Loop
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return False
                    if event.key == pg.K_r:
                        self.player.weapon.reload_ammo()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # if event.button == 1:  # clic gauche
                    #     self.player.weapon.shoot()
                    # if event.button == 3:  # clic droit
                    #     self.player.weapon.reload_ammo()
                    if event.button == 3:  # clic droit
                        idx = self.player.weapon_list.index(self.player.weapon) + 1 
                        idx %= len(self.player.weapon_list)
                        self.player.weapon = self.player.weapon_list[idx]
                
                # Switch d'armes
                # elif event.type == pg.MOUSEWHEEL:
                #     idx = self.player.weapon_list.index(self.player.weapon)
                #     idx = (idx + event.y) % len(self.player.weapon_list)
                #     self.player.weapon = self.player.weapon_list[idx]
                    
            # ==== Update ====
            self.dt = min(clock.tick(s.FPS) / 1000, 0.05)
            self.process()
            self.draw()
            s.show_fps(self.screen, clock)
            pg.display.flip()


# ==== Main ====
if __name__ == "__main__":
    pg.init()
    game = Game(s.WIDTH, s.HEIGHT)
    game.run()
    pg.quit()