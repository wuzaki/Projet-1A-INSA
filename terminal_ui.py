import settings as s
import pygame as pg
import sys
import math
import random
import os

from interactables.portal import Portal


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

class TerminalUI:
    # Taille fixe interne du terminal — indépendante de la fenêtre hôte
    TERM_W = 1000
    TERM_H = 680
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

    def __init__(self, game, data):
        self.game = game
        game.draw()  # dessine le jeu en arrière-plan
        self.screen = game.screen # fenêtre réelle (taille quelconque)

        self.bg = self.screen.copy() # copie de l'arrière-plan pour le flouter ou le réutiliser
        # Overlay sombre par-dessus
        overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160)) # 160/255 ≈ 63% d'opacité, ajuste à ton goût
        self.bg.blit(overlay, (0, 0))

        self.data = data

        # Surface interne de taille fixe : tout est dessiné ici
        self.surf = pg.Surface((self.TERM_W, self.TERM_H))

        self.font = pg.font.SysFont("Raleway", self.FONT_SIZE)
        self.font_bold = pg.font.SysFont("Raleway", self.FONT_SIZE + 2)
        self.font_small = pg.font.SysFont("Raleway", 15)

        self.build_static_surfaces()
        self.init_state()
        self.load_node("root")

    # Centrage : blitte self.surf au centre de self.screen
    def blit_centered(self, clock):
        win_w, win_h = self.screen.get_size()
        ox = (win_w - self.TERM_W) // 2
        oy = (win_h - self.TERM_H) // 2
        self.screen.blit(self.bg, (0, 0))  # dessine la copie de l'arrière-plan
        self.screen.blit(self.surf, (ox, oy))
        s.show_fps(self.screen, clock)
        pg.display.flip()

    # Surfaces statiques (scanlines, vignette, flash)
    def build_static_surfaces(self):
        W, H = self.TERM_W, self.TERM_H

        self.scanline_surf = pg.Surface((W, H), pg.SRCALPHA)
        for y in range(0, H, 4):
            pg.draw.line(self.scanline_surf, (*self.SCANLINE, 60), (0, y), (W, y))

        self.vignette_surf = pg.Surface((W, H), pg.SRCALPHA)
        for x in range(W):
            for origin, spread in [(0, 80), (W - 1, 80)]:
                alpha = max(0, spread - abs(x - origin))
                if alpha:
                    pg.draw.line(self.vignette_surf, (0, 0, 0, alpha), (x, 0), (x, H))
        for y in range(H):
            for origin, spread in [(0, 60), (H - 1, 60)]:
                alpha = max(0, spread - abs(y - origin))
                if alpha:
                    pg.draw.line(self.vignette_surf, (0, 0, 0, alpha), (0, y), (W, y))

        self.flash_surf = pg.Surface((W, H))
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

        if node_id == "activate_portal":
            for item in self.game.world_graph.get_interactables():
                if isinstance(item, Portal) and item.name == self.data[node_id]["portal_name"]:
                    item.get_access()  # active le portail connecté à ce terminal

        if node_id == "end_level":
            # print("WIN!")
            # self.game.show_win()
            return "end_level"

        if node_id == "shutdown":
            # pg.time.set_timer(pg.USEREVENT, 2000)  # timer pour quitter après 2 secondes
            return False

    def trigger_glitch(self, count=(1, 4), height=(1, 3), duration=8):
        n = random.randint(*count)
        self.glitch_lines = [
            (random.randint(20, self.TERM_H - 20), random.randint(*height))
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
                self.quit_terminal()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return False

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
                        r = self.load_node(target)
                        if r is False:
                            return False
            else:
                pg.event.post(event)

    def quit_terminal(self):
        pg.quit()
        sys.exit()

    # ---- Drawing — tout sur self.surf (taille fixe) ----

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
        s = self.surf
        W, H = self.TERM_W, self.TERM_H
        m = 14
        pg.draw.rect(s, self.BORDER, (m, m, W - 2*m, H - 2*m), 1)
        for cx, cy in [(m, m), (W-m, m), (m, H-m), (W-m, H-m)]:
            pg.draw.circle(s, self.GLOW, (cx, cy), 3)
        title = self.font_small.render("ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM", True, self.DIM)
        s.blit(title, (W//2 - title.get_width()//2, 4))
        status = self.font_small.render("[ SECURE TERMINAL v4.2 ]", True, self.DIM)
        s.blit(status, (W//2 - status.get_width()//2, H - 12))

    def draw_text(self, y):
        s = self.surf
        partial = self.full_text[:self.displayed_chars]
        lines = partial.split("\n")
        for i, line in enumerate(lines):
            is_last = (i == len(lines) - 1) and not self.typewriter_done
            self.glow_text(s, line, (self.MARGIN, y), self.TEXT, self.font)
            if is_last and self.cursor_visible:
                cx = self.MARGIN + self.font.size(line)[0] + 2
                pg.draw.rect(s, self.CURSOR, (cx, y+2, 10, self.FONT_SIZE-2))
            y += self.LINE_HEIGHT

        if self.typewriter_done and self.cursor_visible:
            last = self.full_text.split("\n")[-1]
            cx = self.MARGIN + self.font.size(last)[0] + 2
            pg.draw.rect(s, self.CURSOR, (cx, y - self.LINE_HEIGHT + 2, 10, self.FONT_SIZE - 2))

        return y

    def draw_options(self, y):
        s = self.surf
        node = self.data[self.current_node]
        if not node["options"] or (not self.typewriter_done and self.options_alpha == 0):
            return

        t = pg.time.get_ticks()
        tmp = pg.Surface((self.TERM_W, self.TERM_H), pg.SRCALPHA)

        for i, option in enumerate(node["options"]):
            oy = y + i * (self.LINE_HEIGHT + 4) + self.options_slide_y

            if i == self.selected:
                bar = pg.Rect(self.MARGIN - 6, oy - 5, self.TERM_W - self.MARGIN*2 + 12, self.LINE_HEIGHT)
                pg.draw.rect(tmp, (*self.HIGHLIGHT_BG, self.options_alpha), bar, border_radius=3)

                arrow_x = self.MARGIN + int(math.sin(t * 0.006) * 4)
                arrow = self.font_bold.render(">", True, self.GLOW)
                arrow.set_alpha(self.options_alpha)
                tmp.blit(arrow, (arrow_x - 18, oy))

                label = self.font_bold.render(option["label"], True, self.GLOW)
            else:
                label = self.font.render(option["label"], True, self.DIM)

            label.set_alpha(self.options_alpha)
            tmp.blit(label, (self.MARGIN + 4, oy))

        s.blit(tmp, (0, 0))

    def draw_hint(self):
        node = self.data[self.current_node]
        if self.typewriter_done and node["options"]:
            text = "Up/Down -> NAVIGUER  |  ENTRÉE -> CONFIRMER  |  ESPACE -> PASSER"
        elif not self.typewriter_done:
            text = "ESPACE  —  passer l'animation"
        else:
            return
        hint = self.font_small.render(text, True, self.DIM)
        self.surf.blit(hint, (self.MARGIN, self.TERM_H - 30))

    def draw_glitch(self):
        for gy, gh in self.glitch_lines:
            if gh <= 0:
                continue
            region = self.surf.subsurface(pg.Rect(0, gy, self.TERM_W, gh)).copy()
            self.surf.blit(region, (random.randint(-20, 20), gy))
            overlay = pg.Surface((self.TERM_W, gh), pg.SRCALPHA)
            overlay.fill((255, 0, 0, 30))
            self.surf.blit(overlay, (0, gy))

    def draw(self, clock):
        s = self.surf
        W, H = self.TERM_W, self.TERM_H

        s.fill(self.BG)

        y = 38
        header = self.font_small.render(f"NODE : {self.current_node.upper()}", True, self.DIM)
        s.blit(header, (self.MARGIN, y))
        y += 22
        pg.draw.line(s, self.DIM, (self.MARGIN, y), (W - self.MARGIN, y), 1)
        y += 16

        y = self.draw_text(y)

        y += 10
        pg.draw.line(s, self.DIM, (self.MARGIN, y), (W - self.MARGIN, y), 1)
        y += 16

        self.draw_options(y)
        self.draw_hint()
        self.draw_border()
        self.draw_glitch()

        s.blit(self.scanline_surf, (0, int(self.scanline_offset)))
        s.blit(self.vignette_surf, (0, 0))

        if self.flash_active and self.flash_alpha > 0:
            self.flash_surf.set_alpha(self.flash_alpha)
            s.blit(self.flash_surf, (0, 0))

        # ← unique appel qui centre et flip
        self.blit_centered(clock)

    def run(self):
        clock = pg.time.Clock()
        while True:
            clock.tick(s.FPS)
            r = self.handle_events()
            if r is False:
                return False
            self.update()
            self.draw(clock)