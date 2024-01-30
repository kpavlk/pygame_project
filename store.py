import pygame
from config_file.config_game import *


class Shop:
    def __init__(self, pos):
        self.pos = pos
        self.font = ARIAL_50
        self.surface = pygame.display.get_surface()
        self.open_flag = False
        self.clock = pygame.time.Clock()

    def handle_collide(self, player_pos):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            print(self.check_distance(player_pos))
            if self.check_distance(player_pos):
                self.open_flag = not self.open_flag
        if self.open_flag:
            return True
        else:
            return False

    def check_distance(self, player_pos):
        if ((player_pos[0] - self.pos[0]) ** 2 + (player_pos[1] - self.pos[0]) ** 2) ** 0.5 >= 200:
            return False
        else:
            return True

    def show_menu(self):
        pygame.draw.rect(self.surface, (255, 0, 0), pygame.Rect(200, 200, 400, 200))
        print(self.open_flag)
        pygame.display.flip()
