import pygame as pg
import math

pg.init()

def create_shoot_zones(tile_size=32):
    """
    Retourne un dict avec 3 surfaces pygame représentant les zones de tir.
    Chaque surface est en SRCALPHA (transparence complète).
    """
    zones = {}

    # SINGLE
    # Rectangle fin (hauteur = 0.6 tile) et long (5 tiles)
    W, H = tile_size * 2, int(tile_size * 0.4)
    surf = pg.Surface((W, H), pg.SRCALPHA)

    for x in range(W):
        # Dégradé horizontal : fort à gauche, transparent à droite
        alpha = int(120 * (1 - x / W))
        pg.draw.line(surf, (255, 255, 255, alpha), (x, 0), (x, H))

    # Bordure visible sur les bords (haut/bas/droite)
    pg.draw.line(surf, (255, 255, 255, 180), (0, 0), (W, 0), 1)
    pg.draw.line(surf, (255, 255, 255, 180), (0, H - 1), (W, H - 1), 1)
    pg.draw.line(surf, (255, 255, 255, 180), (W - 1, 0), (W - 1, H - 1), 1)

    zones["single"] = surf

    # SHOTGUN
    # Cône arrondi : angle d'ouverture ~70°, longueur 4 tiles
    length = tile_size * 4
    half_angle = math.radians(35)
    # Surface carrée englobante
    SIZE = length + tile_size
    surf = pg.Surface((SIZE, SIZE), pg.SRCALPHA)
    cx, cy = 0, SIZE // 2  # origine du cône = bord gauche, milieu

    # Dessin pixel par pixel dans le cône
    for x in range(SIZE):
        for y in range(SIZE):
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy)
            if dist == 0 or dist > length:
                continue
            angle = math.atan2(abs(dy), dx)
            if angle > half_angle:
                continue
            # Dégradé radial (fort à l'origine, transparent à l'extrémité)
            t = dist / length
            # Dégradé angulaire (fort au centre, transparent aux bords du cône)
            a_t = angle / half_angle
            alpha = int(130 * (1 - t) * (1 - a_t ** 2))
            surf.set_at((x, y), (255, 255, 255, alpha))

    # Bordure du cône (2 lignes + arc approché)
    end_top = (
        cx + int(length * math.cos(-half_angle)),
        cy + int(length * math.sin(-half_angle))
    )
    end_bot = (
        cx + int(length * math.cos(half_angle)),
        cy + int(length * math.sin(half_angle))
    )
    pg.draw.line(surf, (255, 255, 255, 180), (cx, cy), end_top, 2)
    pg.draw.line(surf, (255, 255, 255, 180), (cx, cy), end_bot, 2)

    # Arc de fermeture (approximé par des segments)
    arc_steps = 20
    prev = end_top
    for i in range(1, arc_steps + 1):
        frac = i / arc_steps
        a = -half_angle + frac * 2 * half_angle
        pt = (cx + int(length * math.cos(a)), cy + int(length * math.sin(a)))
        pg.draw.line(surf, (255, 255, 255, 180), prev, pt, 2)
        prev = pt

    zones["shotgun"] = surf

    # KNIFE
    # Cercle autour du joueur : rayon 2 tiles, dégradé en anneau
    radius = tile_size * 2
    SIZE = radius * 2 + 4
    surf = pg.Surface((SIZE, SIZE), pg.SRCALPHA)
    center = SIZE // 2

    for x in range(SIZE):
        for y in range(SIZE):
            dist = math.hypot(x - center, y - center)
            if dist > radius:
                continue
            # Dégradé en anneau : max à ~80% du rayon, nul au centre et au bord
            t = dist / radius
            # Courbe en cloche centrée sur 0.75
            alpha = int(110 * math.exp(-((t - 0.75) ** 2) / 0.04))
            surf.set_at((x, y), (255, 255, 255, alpha))

    # Bordure circulaire
    pg.draw.circle(surf, (255, 255, 255, 180), (center, center), radius, 2)

    zones["knife"] = surf

    return zones

screen = pg.display.set_mode((800, 600))
shoot_zones = create_shoot_zones()

zones = create_shoot_zones(tile_size=16)

for name, surf in zones.items():
    pg.image.save(surf, f"assets/zone_{name}.png")

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

    screen.fill((30, 30, 30))

    # Affichage des zones de tir pour test
    screen.blit(shoot_zones["single"], (50, 50))
    screen.blit(shoot_zones["shotgun"], (50, 150))
    screen.blit(shoot_zones["knife"], (50, 300))

    pg.display.flip()