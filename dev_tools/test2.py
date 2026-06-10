import pygame as pg
import sys
import math
import random
import os


TERMINAL_DATA = {
    "root": {
        "text": "Bienvenue dans le terminal sécurisé.\nChoisissez une option :",
        "options": [
            {"label": "Accéder au journal des opérations", "target": "journal_ops"},
            {"label": "Accéder aux fichiers utilisateurs", "target": "fichiers_users"},
            {"label": "Éteindre le terminal", "target": "shutdown"}
        ]
    },
    "journal_ops": {
        "text": "Journal des opérations :\n1. Mission Alpha terminée\n2. Mission Beta en cours",
        "options": [
            {"label": "Retour au menu principal", "target": "root"}
        ]
    },
    "fichiers_users": {
        "text": "Liste des utilisateurs :\n- Alice\n- Bob\n- Charlie",
        "options": [
            {"label": "Voir le profil d'Alice", "target": "alice_profile"},
            {"label": "Retour au menu principal", "target": "root"}
        ]
    },
    "alice_profile": {
        "text": "Profil d'Alice :\n- Rôle : Technicien\n- Dernière connexion : 01/04/2026",
        "options": [
            {"label": "Retour à la liste des utilisateurs", "target": "fichiers_users"}
        ]
    },
    "shutdown": {
        "text": "Le terminal va s'éteindre.\nFin de session.",
        "options": []
    }
}


class Terminal:
    WIDTH = 1000
    HEIGHT = 680
    FPS = 60
    MARGIN = 36
    FONT_SIZE = 24
    LINE_HEIGHT = FONT_SIZE + 8

    BG = (6, 10, 22)
    TEXT = (0, 230, 80)
    DIM = (0, 110, 40)
    HIGHLIGHT_BG = (0, 50, 20)
    CURSOR = (0, 255, 100)
    GLOW = (0, 255, 80)
    BORDER = (0, 160, 50)
    SCANLINE = (0, 20, 8)

    CURSOR_BLINK = 25
    GLITCH_INTERVAL = 180
    CHARS_PER_TICK = 2

    def __init__(self, data):
        pg.init()
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        pg.display.set_caption("Terminal Fallout")

        self.clock = pg.time.Clock()
        self.data = data

        self.font = pg.font.SysFont("Raleway", self.FONT_SIZE)
        self.font_bold = pg.font.SysFont("Raleway", self.FONT_SIZE + 2)
        self.font_small = pg.font.SysFont("Raleway", 15)

        self.build_static_surfaces()
        self.init_state()
        self.load_node("root")

    def build_static_surfaces(self):
        self.scanline_surf = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        for y in range(0, self.HEIGHT, 4):
            pg.draw.line(self.scanline_surf, (*self.SCANLINE, 60), (0, y), (self.WIDTH, y))

        self.vignette_surf = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        for x in range(self.WIDTH):
            for origin, spread in [(0, 80), (self.WIDTH - 1, 80)]:
                alpha = max(0, spread - abs(x - origin))
                if alpha:
                    pg.draw.line(self.vignette_surf, (0, 0, 0, alpha), (x, 0), (x, self.HEIGHT))
        for y in range(self.HEIGHT):
            for origin, spread in [(0, 60), (self.HEIGHT - 1, 60)]:
                alpha = max(0, spread - abs(y - origin))
                if alpha:
                    pg.draw.line(self.vignette_surf, (0, 0, 0, alpha), (0, y), (self.WIDTH, y))

        self.flash_surf = pg.Surface((self.WIDTH, self.HEIGHT))
        self.flash_surf.fill(self.GLOW)

    def init_state(self):
        self.current_node = None
        self.selected = 0

        self.full_text = ""
        self.displayed_chars = 0
        self.typewriter_done = False

        self.flash_alpha = 0
        self.flash_active = False

        self.glitch_lines = []
        self.glitch_timer = 0

        self.options_slide_y = 0
        self.options_alpha = 0
        self.options_ready = False

        self.cursor_visible = True
        self.cursor_timer = 0

        self.scanline_offset = 0.0

    def load_node(self, node_id):
        self.current_node = node_id
        self.selected = 0
        self.full_text = self.data[node_id]["text"]
        self.displayed_chars = 0
        self.typewriter_done = False
        self.options_slide_y = 40
        self.options_alpha = 0
        self.options_ready = False
        self.flash_alpha = 180
        self.flash_active = True
        self.trigger_glitch(count=(4, 10), height=(2, 8), duration=18)

    def trigger_glitch(self, count=(1, 4), height=(1, 3), duration=8):
        n = random.randint(*count)
        self.glitch_lines = [
            (random.randint(20, self.HEIGHT - 20), random.randint(*height))
            for _ in range(n)
        ]
        self.glitch_timer = duration

    def update(self):
        if not self.typewriter_done:
            self.displayed_chars = min(
                self.displayed_chars + self.CHARS_PER_TICK,
                len(self.full_text)
            )
            if self.displayed_chars >= len(self.full_text):
                self.typewriter_done = True

        if self.typewriter_done and not self.options_ready:
            self.options_slide_y = max(0, self.options_slide_y - 4)
            self.options_alpha = min(255, self.options_alpha + 20)
            if self.options_slide_y == 0 and self.options_alpha == 255:
                self.options_ready = True

        if self.flash_active:
            self.flash_alpha -= 18
            if self.flash_alpha <= 0:
                self.flash_alpha = 0
                self.flash_active = False

        if self.glitch_timer > 0:
            self.glitch_timer -= 1
        else:
            self.glitch_lines = []

        if random.randint(0, self.GLITCH_INTERVAL) == 0:
            self.trigger_glitch()

        self.cursor_timer += 1
        if self.cursor_timer >= self.CURSOR_BLINK:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

        self.scanline_offset = (self.scanline_offset + 0.3) % 4

    def handle_events(self):
        node = self.data[self.current_node]
        n = len(node["options"])

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit_terminal()

                elif not self.typewriter_done and event.key == pg.K_SPACE:
                    self.displayed_chars = len(self.full_text)
                    self.typewriter_done = True

                elif self.typewriter_done:
                    if event.key == pg.K_DOWN and n:
                        self.selected = (self.selected + 1) % n
                        self.trigger_glitch(count=(3, 3), height=(1, 4), duration=6)
                    elif event.key == pg.K_UP and n:
                        self.selected = (self.selected - 1) % n
                        self.trigger_glitch(count=(3, 3), height=(1, 4), duration=6)
                    elif event.key == pg.K_RETURN and n:
                        target = node["options"][self.selected]["target"]
                        if target == "shutdown":
                            self.quit_terminal()
                        self.load_node(target)

    def quit_terminal(self):
        pg.quit()
        sys.exit()

    # ---- Drawing ----

    def glow_text(self, surf, text, pos, color, font, alpha=120):
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0)]
        tmp = pg.Surface(font.size(text), pg.SRCALPHA)
        for ox, oy in offsets:
            s = font.render(text, True, color)
            s.set_alpha(alpha // 2)
            tmp.blit(s, (ox, oy))
        tmp.blit(font.render(text, True, color), (0, 0))
        surf.blit(tmp, pos)

    def draw_border(self):
        m = 14
        pg.draw.rect(self.screen, self.BORDER, (m, m, self.WIDTH - 2*m, self.HEIGHT - 2*m), 1)
        for cx, cy in [(m, m), (self.WIDTH-m, m), (m, self.HEIGHT-m), (self.WIDTH-m, self.HEIGHT-m)]:
            pg.draw.circle(self.screen, self.GLOW, (cx, cy), 3)
        title = self.font_small.render("ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM", True, self.DIM)
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 4))
        status = self.font_small.render("[ SECURE TERMINAL v4.2 ]", True, self.DIM)
        self.screen.blit(status, (self.WIDTH//2 - status.get_width()//2, self.HEIGHT - 12))

    def draw_text(self, y):
        partial = self.full_text[:self.displayed_chars]
        lines = partial.split("\n")
        for i, line in enumerate(lines):
            is_last = (i == len(lines) - 1) and not self.typewriter_done
            self.glow_text(self.screen, line, (self.MARGIN, y), self.TEXT, self.font)
            if is_last and self.cursor_visible:
                cx = self.MARGIN + self.font.size(line)[0] + 2
                pg.draw.rect(self.screen, self.CURSOR, (cx, y+2, 10, self.FONT_SIZE-2))
            y += self.LINE_HEIGHT

        if self.typewriter_done and self.cursor_visible:
            last = self.full_text.split("\n")[-1]
            cx = self.MARGIN + self.font.size(last)[0] + 2
            pg.draw.rect(self.screen, self.CURSOR, (cx, y - self.LINE_HEIGHT + 2, 10, self.FONT_SIZE - 2))

        return y

    def draw_options(self, y):
        node = self.data[self.current_node]
        if not node["options"] or (not self.typewriter_done and self.options_alpha == 0):
            return

        t = pg.time.get_ticks()
        surf = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)

        for i, option in enumerate(node["options"]):
            oy = y + i * (self.LINE_HEIGHT + 4) + self.options_slide_y

            if i == self.selected:
                bar = pg.Rect(self.MARGIN - 6, oy - 5, self.WIDTH - self.MARGIN*2 + 12, self.LINE_HEIGHT)
                pg.draw.rect(surf, (*self.HIGHLIGHT_BG, self.options_alpha), bar, border_radius=3)

                arrow_x = self.MARGIN + int(math.sin(t * 0.006) * 4)
                arrow = self.font_bold.render(">", True, self.GLOW)
                arrow.set_alpha(self.options_alpha)
                surf.blit(arrow, (arrow_x - 18, oy))

                label = self.font_bold.render(option["label"], True, self.GLOW)
            else:
                label = self.font.render(option["label"], True, self.DIM)

            label.set_alpha(self.options_alpha)
            surf.blit(label, (self.MARGIN + 4, oy))

        self.screen.blit(surf, (0, 0))

    def draw_hint(self):
        node = self.data[self.current_node]
        if self.typewriter_done and node["options"]:
            text = "↑↓  NAVIGUER     ENTRÉE  CONFIRMER     ESPACE  PASSER"
        elif not self.typewriter_done:
            text = "ESPACE  —  passer l'animation"
        else:
            return
        hint = self.font_small.render(text, True, self.DIM)
        self.screen.blit(hint, (self.MARGIN, self.HEIGHT - 30))

    def draw_glitch(self):
        for gy, gh in self.glitch_lines:
            if gh <= 0:
                continue
            region = self.screen.subsurface(pg.Rect(0, gy, self.WIDTH, gh)).copy()
            self.screen.blit(region, (random.randint(-20, 20), gy))
            overlay = pg.Surface((self.WIDTH, gh), pg.SRCALPHA)
            overlay.fill((255, 0, 0, 30))
            self.screen.blit(overlay, (0, gy))

    def draw(self):
        self.screen.fill(self.BG)

        y = 38
        header = self.font_small.render(f"NODE : {self.current_node.upper()}", True, self.DIM)
        self.screen.blit(header, (self.MARGIN, y))
        y += 22
        pg.draw.line(self.screen, self.DIM, (self.MARGIN, y), (self.WIDTH - self.MARGIN, y), 1)
        y += 16

        y = self.draw_text(y)

        y += 10
        pg.draw.line(self.screen, self.DIM, (self.MARGIN, y), (self.WIDTH - self.MARGIN, y), 1)
        y += 16

        self.draw_options(y)
        self.draw_hint()
        self.draw_border()
        self.draw_glitch()

        self.screen.blit(self.scanline_surf, (0, int(self.scanline_offset)))
        self.screen.blit(self.vignette_surf, (0, 0))

        if self.flash_active and self.flash_alpha > 0:
            self.flash_surf.set_alpha(self.flash_alpha)
            self.screen.blit(self.flash_surf, (0, 0))

        pg.display.flip()

    def run(self):
        while True:
            self.clock.tick(self.FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Terminal(TERMINAL_DATA).run()