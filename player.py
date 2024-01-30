import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, skin, pos, group):
        super().__init__(group)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f"data/images/{skin}.png").convert_alpha()
        # Загружаем изображение игрока
        self.rect = self.image.get_rect(center=pos)
        self.z = 7
        self.direction = pygame.math.Vector2()
        # Определяем направление движения через задание вектора
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 400
        # Устанавливаем скорость

    def movement(self):
        keys = pygame.key.get_pressed()
        # Изменяем направление вектора движения игрока, в зависимости от нажатой клавиши
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def move(self, t):
        # Перемещение игрока по полю
        self.pos += self.direction * self.speed * t
        self.rect.center = self.pos

    def update(self, t):
        self.movement()
        self.move(t)

