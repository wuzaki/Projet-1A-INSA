import pygame
import sys

# --- Config ---
WIDTH, HEIGHT = 500, 80
FPS = 60

# Palette (from screenshot)
BG_COLOR        = (15, 15, 45)       # dark navy
GRID_LINE       = (30, 30, 80)       # subtle blue grid
BORDER_COLOR    = (60, 60, 140)      # blue-ish border
AVATAR_BG       = (40, 20, 30)       # dark reddish behind avatar
NAME_COLOR      = (200, 220, 255)    # light blue-white
LABEL_COLOR     = (160, 180, 220)    # softer blue-white
HEALTH_BG       = (30, 10, 20)       # dark bar bg
HEALTH_FG       = (180, 30, 40)      # red health bar
HEALTH_SHINE    = (220, 60, 60)      # lighter red top strip
AMMO_COLOR      = (200, 220, 255)    # same as name

# Health stats
HEALTH_CURRENT  = 35
HEALTH_MAX      = 100
AMMO_CURRENT    = 120
AMMO_MAX        = 800


def draw_grid(surface, rect, cell=12):
    """Draw a subtle grid pattern inside rect."""
    x0, y0, w, h = rect
    for x in range(x0, x0 + w, cell):
        pygame.draw.line(surface, GRID_LINE, (x, y0), (x, y0 + h))
    for y in range(y0, y0 + h, cell):
        pygame.draw.line(surface, GRID_LINE, (x0, y), (x0 + w, y))


def draw_avatar(surface, x, y, size=64):
    """Draw a pixel-art style placeholder avatar similar to the screenshot."""
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, AVATAR_BG, rect)

    # -- Very simple pixel avatar (pink-hair anime girl silhouette) --
    # Colours
    SKIN   = (230, 170, 130)
    HAIR   = (220, 100, 140)
    DARK   = (50,  20,  30)
    EYE    = (80,  60, 120)
    SHIRT  = (60,  80, 160)

    pw = 4  # pixel width in "screen pixels"

    def px(col, row, color, w=1, h=1):
        pygame.draw.rect(surface, color,
                         (x + col * pw, y + row * pw, pw * w, pw * h))

    # Hair (top)
    for c in range(2, 14):
        px(c, 0, HAIR)
    for c in range(1, 15):
        px(c, 1, HAIR)
    for c in range(0, 15):
        px(c, 2, HAIR)
    # side hair left
    for r in range(3, 10):
        px(0, r, HAIR)
        px(1, r, HAIR)
    # side hair right
    for r in range(3, 8):
        px(14, r, HAIR)
        px(15, r, HAIR)

    # Face
    for r in range(3, 9):
        for c in range(2, 14):
            px(c, r, SKIN)

    # Eyes
    px(4, 5, EYE, 2, 1)
    px(10, 5, EYE, 2, 1)

    # Mouth
    px(6, 7, DARK)
    px(7, 7, DARK)
    px(8, 7, DARK)

    # Neck
    for r in range(9, 11):
        for c in range(6, 10):
            px(c, r, SKIN)

    # Shirt / body
    for r in range(11, 16):
        for c in range(2, 14):
            px(c, r, SHIRT)

    # Thin border
    pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def draw_health_bar(surface, x, y, w, h, current, maximum):
    """Draw a health bar with dark background and red fill."""
    bg_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, HEALTH_BG, bg_rect)
    pygame.draw.rect(surface, BORDER_COLOR, bg_rect, 1)

    fill_w = int(w * current / maximum)
    if fill_w > 0:
        fill_rect = pygame.Rect(x + 1, y + 1, fill_w - 2, h - 2)
        pygame.draw.rect(surface, HEALTH_FG, fill_rect)
        # shine strip on top
        shine_rect = pygame.Rect(x + 1, y + 1, fill_w - 2, max(1, h // 4))
        pygame.draw.rect(surface, HEALTH_SHINE, shine_rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Agent Woods HUD")
    clock = pygame.time.Clock()

    # Fonts – use pygame default (monospace-ish) scaled
    font_large  = pygame.font.SysFont("Courier New", 18, bold=True)
    font_medium = pygame.font.SysFont("Courier New", 14, bold=True)
    font_small  = pygame.font.SysFont("Courier New", 13, bold=False)

    AVATAR_SIZE = HEIGHT  # square avatar fills full height

    screen.fill(BG_COLOR)
    draw_grid(screen, (0, 0, WIDTH, HEIGHT), cell=12)

        # # Outer border
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, HEIGHT), 2)

    pygame.image.save(screen, "test.png")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # --- Background ---
        screen.fill(BG_COLOR)
        draw_grid(screen, (0, 0, WIDTH, HEIGHT), cell=12)

        # # Outer border
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, HEIGHT), 2)

        # # Vertical separator after avatar
        # pygame.draw.line(screen, BORDER_COLOR,
        #                   (AVATAR_SIZE, 0), (AVATAR_SIZE, HEIGHT), 1)

        # # --- Avatar ---
        draw_avatar(screen, 0, 0, AVATAR_SIZE)

        # # --- Right panel ---
        # panel_x = AVATAR_SIZE + 8
        # panel_w = WIDTH - AVATAR_SIZE - 16

        # # Name
        # name_surf = font_large.render("Agent Woods", True, NAME_COLOR)
        # screen.blit(name_surf, (panel_x, 6))

        # # Weapon (top-right)
        # weapon_text = "Weapon: SimpleGun"
        # weapon_surf = font_medium.render(weapon_text, True, NAME_COLOR)
        # screen.blit(weapon_surf,
        #             (WIDTH - weapon_surf.get_width() - 6, 6))

        # # Health label + bar
        # health_label = font_small.render("Health:", True, LABEL_COLOR)
        # screen.blit(health_label, (panel_x, HEIGHT // 2 + 2))

        # bar_x = panel_x + health_label.get_width() + 6
        # bar_y = HEIGHT // 2 + 4
        # bar_w = WIDTH // 2 - bar_x + panel_x - 4
        # bar_h = 14
        # draw_health_bar(screen, bar_x, bar_y, bar_w, bar_h,
        #                 HEALTH_CURRENT, HEALTH_MAX)

        # # Ammo (bottom-right)
        # ammo_text = f"Ammo: {AMMO_CURRENT}/{AMMO_MAX}"
        # ammo_surf = font_small.render(ammo_text, True, AMMO_COLOR)
        # screen.blit(ammo_surf,
        #             (WIDTH - ammo_surf.get_width() - 6,
        #              HEIGHT // 2 + 4))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
