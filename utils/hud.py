import settings as s
import pygame as pg

"""
Ce fichier contient la classe PlayerHUD() pour l'affichage des données du joueur (health, munitions, arme...)
"""

# ==== HUD =====
class PlayerHUD:
    def __init__(self, game):
        self.game = game
        self.keys_info_move_text = s.get_text_surf("Move : QSDZ", s.FONTS["raleway"][28])
        self.keys_info_shoot_text = s.get_text_surf("Shoot : Right Click", s.FONTS["raleway"][28])
        self.keys_info_term_text = s.get_text_surf("Terminal : A", s.FONTS["raleway"][28])
        self.keys_info_weapons_text = s.get_text_surf("Switch Weapons : Molette", s.FONTS["raleway"][28])

    def show_health(self, screen):
        health = self.game.player.health
        temp = s.get_text_surf(f"Health: {health}", s.FONTS["raleway"][28])
        s.show_basic_text(screen, temp, (10, 40))

    def show_ammo_count(self, screen):
        ammo_count = self.game.player.weapon.ammo_count
        stock_ammo = self.game.player.weapon.stock_ammo
        temp = s.get_text_surf(f"Ammo: {ammo_count}/{stock_ammo}", s.FONTS["raleway"][28])
        s.show_basic_text(screen, temp, (10, 60))

    def show_weapon_mode(self, screen):
        mode = self.game.player.weapon.mode
        temp = s.get_text_surf(f"Mode: {mode}", s.FONTS["raleway"][28])
        s.show_basic_text(screen, temp, (10, 80))

    def draw(self, screen):
        # Player Data
        self.show_health(screen)
        self.show_ammo_count(screen)
        self.show_weapon_mode(screen)

        # Use Protocol
        s.show_basic_text(screen, self.keys_info_move_text, (10, 120))
        s.show_basic_text(screen, self.keys_info_shoot_text, (10, 140))
        s.show_basic_text(screen, self.keys_info_term_text, (10, 160))
        s.show_basic_text(screen, self.keys_info_weapons_text, (10, 180))
