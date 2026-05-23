import settings as s
from .base import Interactable
from terminal_ui import TerminalUI
import pygame as pg
import json

class Terminal(Interactable):
    def __init__(self, game, x, y, w, h, map_name, name="", access=True):
        super().__init__(game, x, y, w, h)
        self.name = name
        self.map_name = map_name
        self.access = False if access == "false" else True
        self.collision = True
        self.term_data = self.load_data()
        self.image = self.load_image("assets/interactables/terminal.png")

        self.ui = None
        self.active = False

    def load_data(self):
        try:
            with open(f"assets/terminal_data/{self.name}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # print(f"Terminal data file not found for {self.name}")
            return {}

    def get_access(self):
        self.access = True

    def update(self):
        keys = pg.key.get_pressed()
        if self.access:
            if self.rect.inflate(40, 40).colliderect(self.game.player.feet) and keys[pg.K_a]:
                TerminalUI(self.game, self.term_data).run()
