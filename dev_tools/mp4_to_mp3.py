import os
import sys
from moviepy import VideoFileClip

def convert_mp4_to_mp3(dossier="."):
    """Convertit tous les fichiers .mp4 d'un dossier en .mp3."""

    fichiers_mp4 = [f for f in os.listdir(dossier) if f.endswith(".mp4")]

    if not fichiers_mp4:
        print("Aucun fichier .mp4 trouvé dans le dossier.")
        return

    print(f"{len(fichiers_mp4)} fichier(s) .mp4 trouvé(s).\n")

    for fichier in sorted(fichiers_mp4):
        entree = os.path.join(dossier, fichier)
        sortie = os.path.join(dossier, fichier.replace(".mp4", ".mp3"))

        print(f"Conversion : {fichier} → {fichier.replace('.mp4', '.mp3')}")

        try:
            with VideoFileClip(entree) as video:
                video.audio.write_audiofile(sortie, logger=None)
            print(f"  ✓ Succès")
        except Exception as e:
            print(f"  ✗ Échec : {e}")

    print("\nConversion terminée !")


if __name__ == "__main__":
    dossier = "C:/Users/luxal/Desktop/Coding/Python/Projet 1A (INSA)/assets/sounds/enemy_hurt" # sys.argv[1] if len(sys.argv) > 1 else "."
    convert_mp4_to_mp3(dossier)