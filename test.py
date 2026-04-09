import pygame
import json
import sys

pygame.init()

# ==== Settings ====
WIDTH, HEIGHT = 800, 600
FONT_SIZE = 20
LINE_HEIGHT = FONT_SIZE + 5
BG_COLOR = (10, 10, 30)
TEXT_COLOR = (0, 255, 0)
HIGHLIGHT_COLOR = (0, 100, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Terminal Fallout")
font = pygame.font.SysFont("Monospace", FONT_SIZE, "bold")

# ==== Example JSON Tree ====
terminal_data = {
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
        "text": "Le terminal va s'éteindre. Fin de session.",
        "options": []
    }
}

current_node = "root"
selected_option = 0

def draw_node(node_id):
    screen.fill(BG_COLOR)
    node = terminal_data[node_id]

    # Draw text
    y = 20
    for line in node["text"].split("\n"):
        rendered_line = font.render(line, True, TEXT_COLOR)
        screen.blit(rendered_line, (20, y))
        y += LINE_HEIGHT

    # Draw options
    y += 20
    for i, option in enumerate(node["options"]):
        color = HIGHLIGHT_COLOR if i == selected_option else TEXT_COLOR
        rendered_option = font.render(f"> {option['label']}", True, color)
        screen.blit(rendered_option, (40, y))
        y += LINE_HEIGHT

def main():
    global current_node, selected_option
    clock = pygame.time.Clock()

    while True:
        draw_node(current_node)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                node = terminal_data[current_node]
                options_count = len(node["options"])

                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % options_count
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % options_count
                elif event.key == pygame.K_RETURN:
                    if options_count > 0:
                        current_node = node["options"][selected_option]["target"]
                        selected_option = 0

if __name__ == "__main__":
    main()