from config_file.config_game import *

from pynput.keyboard import Listener
import pygame
import os
import sys
import random
import sqlite3

con = sqlite3.connect('data/game.sqlite3')
cur = con.cursor()

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
sprite = pygame.sprite.Sprite()
pygame.init()
screen.fill(pygame.Color("white"))
font = pygame.font.Font(None, 20)


def str_key(key):
    return str(key)[1]


def change_score(delta_score):
    score = list(cur.execute('SELECT * FROM player_stats').fetchone())
    score[0] += delta_score
    cur.execute('Delete from player_stats')
    cur.execute('Insert into player_stats (score, money) values (?, ?)', score)


def change_money(delta_money):
    money = list(cur.execute('SELECT * FROM player_stats').fetchone())
    money[1] += delta_money
    cur.execute('Delete from player_stats')
    cur.execute('Insert into player_stats (score, money) values (?, ?)', money)


class Keyboard:
    current_word = ()
    completed_length = 0
    active_words = []

    def __init__(self):
        self.reset_word()
        self.start_listener()

    def start_listener(self):
        listener = Listener(on_press=self.on_press)
        listener.start()

    def choose_active_word(self, key):
        for pair in self.active_words:
            word = pair[0]
            if word[0] == str_key(key):
                self.current_word = pair
                self.completed_length = 0
                print(f'{word} was chosen')
                return word

    def on_press(self, key):
        word = self.current_word[0]
        if not word:
            word = self.choose_active_word(key)
            if not word:
                return

        if str_key(key) == word[self.completed_length]:
            self.completed_length += 1
            print(f"{word[:self.completed_length]}")
            if self.completed_length == len(word):
                print("complete")
                self.current_word[-1](word)
                self.reset_word()

    def reset_word(self):
        if self.current_word:
            self.active_words.remove(self.current_word)
        self.current_word = ('', 0, None)
        self.completed_length = 0

    def set_active_words(self, words_and_distance):
        # (word, distance_from_player_to_enemy, event)
        self.active_words = sorted(words_and_distance, key=lambda a: a[1])


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos, name, speed, image_name, score, money, *group):
        super().__init__(*group)
        self.image = load_image(image_name)
        self.speed = speed
        self.name = name
        self.score = score
        self.money = money
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([random.randint(-200, 0), random.randint(width, width + 200)])
        self.rect.y = random.choice([random.randint(-200, 0), random.randint(height, height + 200)])
        self.string_rendered = font.render(self.name, False, (0, 0, 0))
        self.textrect = self.string_rendered.get_rect(center=(self.image.get_rect().center[0],
                                                              self.image.get_rect().center[1] + 30))
        self.image.blit(self.string_rendered, self.textrect)
        self.distance = ((self.rect.x - player_pos[0]) ** 2 + (self.rect.y - player_pos[0]) ** 2) ** 0.5

    def update(self, player_pos, activ_word):
        if abs(self.rect.x - player_pos[0]) > 50 or abs(self.rect.y - player_pos[1]) > 50:
            k_x = (abs(self.rect.x - player_pos[0]) /
                   ((abs(self.rect.x - player_pos[0]) + abs(self.rect.y - player_pos[1])) / 2))
            k_y = (abs(self.rect.y - player_pos[1]) /
                   ((abs(self.rect.x - player_pos[0]) + abs(self.rect.y - player_pos[1])) / 2))
            if self.rect.x > player_pos[0] and self.rect.y > player_pos[1]:
                self.rect.x -= self.speed * k_x
                self.rect.y -= self.speed * k_y
            elif self.rect.x > player_pos[0] and self.rect.y < player_pos[1]:
                self.rect.x -= self.speed * k_x
                self.rect.y += self.speed * k_y
            elif self.rect.x < player_pos[0] and self.rect.y > player_pos[1]:
                self.rect.x += self.speed * k_x
                self.rect.y -= self.speed * k_y
            else:
                self.rect.x += self.speed * k_x
                self.rect.y += self.speed * k_y
            self.distance = ((self.rect.x - player_pos[0]) ** 2 + (self.rect.y - player_pos[0]) ** 2) ** 0.5
        if activ_word == self.name:
            self.kill()
            change_score(self.score)
            change_money(self.money)


def generate(n_s, n_m, n_l):
    new_enemy = all_sprites
    for _ in range(n_s):
        Enemy((960, 540), random.choice(word_s), 1,
              "enemy/m_type_s.png", 30, 15,  new_enemy)
    for _ in range(n_m):
        Enemy((960, 540), random.choice(word_m), 1,
              "enemy/m_type_m.png", 60, 30, new_enemy)
    for _ in range(n_l):
        Enemy((960, 540), random.choice(word_l), 1,
              "enemy/m_type_l.png", 100, 50, new_enemy)
    return new_enemy
