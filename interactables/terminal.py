import settings as s
from .base import Interactable
import pygame as pg
import json
import sys

"""
Ce fichier contient la classe Terminal, pour les terminaux d'information.
By Luc ALLEBEE
"""

# ==== Terminal ====
class Terminal(Interactable):
    def __init__(self, game, x, y, w, h, map_name, name=""):
        super().__init__(game, x, y, w, h)
        self.name = name
        self.map_name = map_name
        self.collision = True
        self.term_screen = pg.Surface((s.TERM_WIDTH, s.TERM_HEIGHT))
        self.current_node = "root"
        self.selected_option = 0
        self.term_data = self.load_data()

        # ==== Sprite ====
        self.image = self.load_image("assets/interactables/terminal.png")

    def load_data(self):
        try:
            with open(f"assets/terminal_data/{self.name}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Terminal data file not found for {self.name}")
            return {}

    def update(self):
        keys = pg.key.get_pressed()
        if self.rect.colliderect(self.game.player.feet) and keys[pg.K_e]:
            self.current_node = "root"
            self.selected_option = 0
            self.main()
            return

    def draw_node(self, node_id):
        self.term_screen.fill(s.BG_COLOR)
        node = self.term_data.get(node_id, {})

        # Draw text
        y = 20
        for line in node["text"].split("\n"):
            rendered_line = s.TERM_FONT.render(line, True, s.TEXT_COLOR)
            self.term_screen.blit(rendered_line, (20, y))
            y += s.LINE_HEIGHT

        # Draw options
        y += 20
        for i, option in enumerate(node["options"]):
            color = s.HIGHLIGHT_COLOR if i == self.selected_option else s.TEXT_COLOR
            rendered_option = s.TERM_FONT.render(f"> {option['label']}", True, color)
            self.term_screen.blit(rendered_option, (40, y))
            y += s.LINE_HEIGHT

    def main(self):
        while True:
            self.draw_node(self.current_node)
            self.game.world_graph.draw(self.game.screen)
            self.game.screen.blit(self.term_screen, ((s.WIDTH - s.TERM_WIDTH) // 2, (s.HEIGHT - s.TERM_HEIGHT) // 2))

            if self.current_node == "shutdown":
                pg.display.flip()
                pg.time.delay(1000)  # Attendre 2 secondes avant de fermer le terminal
                return
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                elif event.type == pg.KEYDOWN:
                    node = self.term_data.get(self.current_node, {})
                    options_count = len(node["options"])

                    if event.key == pg.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % options_count
                    elif event.key == pg.K_UP:
                        self.selected_option = (self.selected_option - 1) % options_count
                    elif event.key == pg.K_RETURN:
                        if options_count > 0:
                            self.current_node = node["options"][self.selected_option]["target"]
                            self.selected_option = 0
                    elif event.key == pg.K_ESCAPE:
                        return False
