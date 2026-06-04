import settings as s
import pygame as pg
import math

# Couleurs HUD
C_GREEN      = (57,  255, 20)
C_GREEN_DIM  = (20,  80,  10)
C_AMBER      = (255, 176, 0)
C_AMBER_DIM  = (80,  50,  0)
C_RED        = (200, 30,  30)
C_RED_BRIGHT = (255, 60,  60)
C_BLUE       = (80,  180, 255)
C_BLUE_DIM   = (20,  50,  100)

# Palette fond HUD (inspiré screenshot)
C_HUD_BG        = (12,  10,  35)   # bleu-nuit très sombre
C_HUD_BORDER    = (60,  80,  180)  # bleu moyen (bordure)
C_HUD_GRID      = (30,  35,  90)   # grille intérieure
C_HUD_BAR_BG    = (40,  10,  10)   # fond barre HP


def pulse(t, speed=3.0):
    return 0.5 + 0.5 * math.sin(t * speed)


def draw_bar(screen, rect, value, max_val, color, bg_color, segments=20):
    x, y, w, h = rect
    ratio = max(0.0, min(1.0, value / max(1, max_val)))
    pg.draw.rect(screen, bg_color, rect)
    sw = (w - 2) / segments
    filled_f = ratio * segments
    for i in range(segments):
        sx = x + 1 + int(i * sw)
        seg_w = max(1, int(sw) - 1)
        if i < int(filled_f):
            col = color
        elif i == int(filled_f):
            frac = filled_f - int(filled_f)
            col = tuple(int(c * frac + b * (1 - frac)) for c, b in zip(color, bg_color))
        else:
            col = bg_color
        pg.draw.rect(screen, col, (sx, y + 1, seg_w, h - 2))
    pg.draw.rect(screen, "white", rect, 1)


def draw_hud_background(screen, rect):
    """
    Fond HUD style screenshot :
    - Rectangle sombre bleu-nuit
    - Grille fine à l'intérieur
    - Bordure bleue double
    """
    x, y, w, h = rect

    # Fond principal
    bg_surf = pg.Surface((w, h), pg.SRCALPHA)
    bg_surf.fill((*C_HUD_BG, 220))
    screen.blit(bg_surf, (x, y))

    # Grille intérieure (style RPG rétro)
    grid_surf = pg.Surface((w, h), pg.SRCALPHA)
    cell = 16
    for gx in range(0, w, cell):
        pg.draw.line(grid_surf, (*C_HUD_GRID, 120), (gx, 0), (gx, h))
    for gy in range(0, h, cell):
        pg.draw.line(grid_surf, (*C_HUD_GRID, 120), (0, gy), (w, gy))
    screen.blit(grid_surf, (x, y))

    # Bordure extérieure (double ligne bleue)
    pg.draw.rect(screen, C_HUD_BORDER, (x, y, w, h), 2)
    pg.draw.rect(screen, (30, 40, 100), (x + 3, y + 3, w - 6, h - 6), 1)

    # # Séparateur vertical après la zone avatar
    # avatar_zone = 70
    # pg.draw.line(screen, C_HUD_BORDER, (x + avatar_zone, y), (x + avatar_zone, y + h), 1)


# ==== HUD =====
class PlayerHUD:
    def __init__(self, game):
        self.game = game
        self.keys_info_move_text    = s.get_text_surf("Move : QSDZ",              s.FONTS["raleway"][28])
        self.keys_info_shoot_text   = s.get_text_surf("Shoot : Left Click",      s.FONTS["raleway"][28])
        self.keys_info_reload_text   = s.get_text_surf("Reload : Right Click",      s.FONTS["raleway"][28])
        self.keys_info_term_text    = s.get_text_surf("Terminal : E",             s.FONTS["raleway"][28])
        self.keys_info_weapons_text = s.get_text_surf("Switch Weapons : Molette", s.FONTS["raleway"][28])

        # Pré-calcul de la hauteur du bandeau
        self._hud_h = 72      # hauteur du bandeau en bas
        self._avatar_w = 70   # largeur réservée à l'avatar

    def show_health(self, screen):
        health = self.game.player.health
        temp = s.get_text_surf(f"Health: {health}", s.FONTS["raleway"][28])
        s.show_basic_text(screen, temp, (10, 40))

    def show_ammo_count(self, screen):
        ammo_count = self.game.player.weapon.ammo_count
        stock_ammo = self.game.player.weapon.stock_ammo

        if self.game.player.weapon.name == "knife":
            text = "inf/inf"
        else:
            text = f"Ammo: {ammo_count}/{stock_ammo}"

        temp = s.get_text_surf(text, s.FONTS["raleway"][28])
        s.show_basic_text(screen, temp, (10, 60))

    def show_weapon_mode(self, screen):
        mode = self.game.player.weapon.mode
        temp = s.get_text_surf(f"Mode: {mode}", s.FONTS["raleway"][28])
        s.show_basic_text(screen, temp, (10, 80))

    # ── Bandeau principal ────────────────────────────────────────────────────

    def draw_hud_strip(self, screen):
        """
        Bandeau HUD en bas de l'écran, style screenshot :
        [ Avatar | Nom + HP bar | Arme + Ammo ]
        """
        sw, sh = screen.get_size()
        hh = self._hud_h
        strip_rect = (0, sh - hh*1.5, int(sw // 2.5), int(hh * 1.5))

        draw_hud_background(screen, strip_rect)

        p   = self.game.player
        t   = pg.time.get_ticks() / 1000.0
        # hx  = strip_rect[0]
        # hy  = strip_rect[1]
        hx = 10
        hy = s.HEIGHT - 100
        av  = 0 # self._avatar_w

        # # ── Avatar ──────────────────────────────────────────────────────────
        # if hasattr(p, "avatar") and p.avatar is not None:
        #     av_img = pg.transform.scale(p.avatar, (av - 4, hh - 4))
        #     screen.blit(av_img, (hx + 2, hy + 2))
        # else:
        #     # Placeholder silhouette
        #     ph = pg.Surface((av - 4, hh - 4), pg.SRCALPHA)
        #     ph.fill((40, 40, 80, 180))
        #     pg.draw.rect(ph, C_HUD_BORDER, ph.get_rect(), 1)
        #     icon = s.get_text_surf("?", s.FONTS["raleway"][28])
        #     ph.blit(icon, (ph.get_width()//2 - icon.get_width()//2,
        #                    ph.get_height()//2 - icon.get_height()//2))
        #     screen.blit(ph, (hx + 2, hy + 2))

        # ── Zone centrale (nom + HP) ─────────────────────────────────────────
        cx = hx + av + 8
        cy = hy

        # Nom du joueur
        player_name = getattr(p, "name", "Health:")
        name_surf = s.get_text_surf(player_name, s.FONTS["pixel"][28])
        s.show_basic_text(screen, name_surf, (cx, cy + 15))

        # Label "Health:"
        # lbl_hp = s.get_text_surf("Health:", s.FONTS["raleway"][28])
        # s.show_basic_text(screen, lbl_hp, (cx, cy + 36))

        # Couleur barre HP
        ratio = p.health / max(1, getattr(p, "max_health", 100))
        if ratio < 0.25:
            bar_color = (int(pulse(t, 4) * 200 + 55), 20, 20)
        elif ratio < 0.5:
            bar_color = C_AMBER
        else:
            bar_color = C_RED_BRIGHT

        bar_x = 20 #  cx + lbl_hp.get_width() + 6
        bar_w = int(sw * 0.30)
        draw_bar(screen, (bar_x, cy + 55, bar_w, 14),
                 p.health, getattr(p, "max_health", 100),
                 bar_color, C_HUD_BAR_BG, segments=30)

        # ── Zone droite (arme + ammo) ────────────────────────────────────────
        rx = sw - 200

        # Séparateur vertical
        # pg.draw.line(screen, C_HUD_BORDER, (rx - 10, hy), (rx - 10, hy + hh), 1)

        weapon_name = getattr(p.weapon, "name",
                     getattr(p.weapon, "mode", "Unknown"))
        w_surf = s.get_text_surf(f"Weapon: {weapon_name.capitalize()}", s.FONTS["pixel"][28])
        temp_rect = w_surf.get_rect()
        temp_rect.bottomright = (s.WIDTH -10, cy+20)
        s.show_basic_text(screen, w_surf, temp_rect)

        ammo  = p.weapon.ammo_count
        stock = p.weapon.stock_ammo
        low   = ammo <= 5
        c_ammo = C_RED_BRIGHT if low else C_AMBER
        a_surf = s.get_text_surf(f"Ammo: {ammo}/{stock}", s.FONTS["pixel"][28])
        temp_rect = w_surf.get_rect()
        temp_rect.bottomright = (s.WIDTH - 10, cy + 55)
        s.show_basic_text(screen, a_surf, temp_rect)# (rx, cy - 36))

        # if low:
        #     warn = s.get_text_surf("!! LOW !!", s.FONTS["pixel"][28])
        #     s.show_basic_text(screen, warn, (rx, cy - 52))

    # ── draw principal ───────────────────────────────────────────────────────

    def draw(self, screen):
        # Bandeau HUD bas de l'écran
        self.draw_hud_strip(screen)

        # Raccourcis clavier (haut-gauche, inchangés)
        s.show_basic_text(screen, self.keys_info_move_text,    (10, 40))
        s.show_basic_text(screen, self.keys_info_shoot_text,   (10, 60))
        s.show_basic_text(screen, self.keys_info_reload_text,   (10, 80))
        s.show_basic_text(screen, self.keys_info_term_text,    (10, 100))
        s.show_basic_text(screen, self.keys_info_weapons_text, (10, 120))
