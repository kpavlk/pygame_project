import sys

from def_and_class import Keyboard, generate

import pygame
from config_file.config_game import *
from world import World
import sqlite3


class Game:
    def __init__(self):
        pygame.init()
        self.con = sqlite3.connect('data/game.sqlite3')
        self.cur = self.con.cursor()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        # Задаём параметры экрана
        self.clock = pygame.time.Clock()
        self.enemy_sprites = pygame.sprite.Group()
        pygame.display.set_caption("Game")
        self.state = "menu"
        self.night = self.cur.execute('SELECT night FROM player_stats').fetchone()[0]
        # Устанавливаем текущее состояние для показа нужной сцены
        self.world = World()

    def draw_start_menu(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont('arial', 40)
        title = font.render('Игра', True, (255, 255, 255))
        start_button = font.render('Начать - [пробел]', True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, SCREEN_HEIGHT / 2 - title.get_height() / 2))
        self.screen.blit(start_button, (
            SCREEN_WIDTH / 2 - start_button.get_width() / 2, SCREEN_HEIGHT / 2 + start_button.get_height() / 2))
        pygame.display.update()

    def draw_home(self):
        if self.settings:
            self.world.player_in_room.pos = (960, 802.8)
            self.settings = False
        self.screen.fill((0, 0, 0))
        background = pygame.image.load("data/images/room.jpg")
        self.screen.blit(background, (0, 0))
        self.world.room_sprites.draw(self.screen)
        if self.world.shop.handle_collide(self.world.player_in_room.pos):
            self.world.shop.show_menu()
        pygame.display.update()
        pygame.display.flip()


    def x(self, q):
        global activ, act_word
        activ = True
        act_word = q

    def generate_enemies(self):
        if self.gen:
            for sprite in self.enemy_sprites:
                sprite.kill()
            self.enemy_sprites.add(generate(5, 5, 5))
            self.gen = False

    def start_game(self):
        keyboard = Keyboard()
        data = []
        activ = True
        act_word = ""

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.con.commit()
                    self.con.close()
                    pygame.quit()
                    sys.exit()
            # Изменение времени в цикле
            t = self.clock.tick() / 1000
            # Переключение сцен
            if self.state == "menu":
                self.draw_start_menu()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.state = "home"
                    self.settings = True
                    game_over = False

            if self.state == "home":
                self.draw_home()
                if 260 <= self.world.player_in_room.pos[0] and self.world.player_in_room.pos[1] == 802.8:
                    self.world.player_in_room.update(t)
                else:
                    self.world.player_in_room.pos[0] += 2
                    self.world.player_in_room.pos[1] = 802.8

                if self.world.player_in_room.pos[0] <= 1659.6 and self.world.player_in_room.pos[1] == 802.8:
                    self.world.player.update(t)
                else:
                    self.world.player_in_room.pos[0] -= 2
                    self.world.player_in_room.pos[1] = 802.8

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    self.state = "game"
                    self.world.timer = 15
                    self.world.player.pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    self.night += 1
                    self.gen = True
                    print("Ночь номер:", self.night)
                    game_over = False

            if self.state == "game":
                # Создание мира, отрисовка спрайтов и карты
                self.world.create(t)
                self.generate_enemies()
                if pygame.mouse.get_focused():
                    self.enemy_sprites.update(self.world.player.pos, act_word)
                if activ:
                    activ = False
                    self.enemy_sprites.update(self.world.player.pos, act_word)
                    act_word = ""
                    data = []
                    for i in self.enemy_sprites.sprites():
                        data.append((i.name, i.distance, self.x))
                    keyboard.set_active_words(data)
                self.enemy_sprites.draw(self.screen)
                if self.world.timer <= 0:
                    self.state = "home"
            pygame.display.flip()
            pygame.display.update()
