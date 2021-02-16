import pygame
import os
import sys
import random
import arrow
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QSpinBox, QLabel
from settings import Ui_SettingsWindow
from levelsettings import Ui_LevelSettings

WIDTH = 500
HEIGHT = 500
FPS = 60
LEFT_WALL_x = 50
RIGHT_WALL_X = WIDTH - 50
SLIDER_SPEED = 12
NAME_OF_MUSIC = "intro.mp3"
MUSIC_VOLUME = 0.05
START_SCREEN_PICT = 'fon.jpg'
SETTINGS_BUT_PICT = "settings_button.png"
LEVEL_BUT_PICT = 'levelbutton.png'
ENDLINE_PICT = 'endline.png'
SLIDER_PICT = 'slider.png'
BALL_PICT = "ball.png"
ANTIBUGS_WALLS_PICT = 'antibugs_wall.png'
ANIMATED_PICT = "support_colors.png"

dragons_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
endline_sprites = pygame.sprite.Group()
sliders_sprites = pygame.sprite.Group()
ball_sprites = pygame.sprite.Group()
settings_sprites = pygame.sprite.Group()

pygame.init()
screen_size = WIDTH, HEIGHT
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('АЭРОХОККЕЙ x ПИН-ПОНГ')

running = True
clock = pygame.time.Clock()


# загрузка изображения
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


def terminate():
    pygame.quit()
    sys.exit()


# начальный экран
def start_screen():
    intro_text = ["Выберите режим игры", "1 - мультиплеер", " 0 - одиночная игра",
                  " 2 - игра c ботом",
                  "3 - режим ставка на бота",
                  "Платформы управляются с a и d ", "или стрелочками", "вправо и влево",
                  "При нажатии на шестеренку откроются настройки"]

    fon = pygame.transform.scale(load_image(START_SCREEN_PICT), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.mixer.init()
    pygame.mixer.music.load(NAME_OF_MUSIC)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.stop()
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key in range(48, 52):
                    return event.key - 48
        pygame.display.flip()
        clock.tick(FPS)


# класс кнопки для активации настройки
class SettingsButton(pygame.sprite.Sprite):

    def __init__(self, ball, slider_1, slider_2):
        super().__init__(settings_sprites)
        self.image = load_image(SETTINGS_BUT_PICT, -1)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50
        self.rect.y = 10
        self.ball = ball
        self.slider_1 = slider_1
        self.slider_2 = slider_2

    def set_coords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_coords(self):
        return self.rect.x, self.rect.y, 50 + self.rect.x, \
               50 + self.rect.y

    def start_settings(self):
        app = QApplication(sys.argv)
        ex = SettingsMenu(self.ball, self.slider_1, self.slider_2)
        ex.show()
        app.exec()

    def check_click(self, pos):
        mouse_x = pos[0]
        mouse_y = pos[1]
        coords = self.get_coords()
        if mouse_x > coords[0] and mouse_x < coords[2] and mouse_y > coords[1] and \
                mouse_y < coords[3]:
            self.start_settings()


#  класс настроек
class SettingsMenu(QMainWindow, Ui_SettingsWindow):

    def __init__(self, ball, slider_1, slider_2):
        super().__init__()
        self.setupUi(self)
        self.ball = ball
        self.slider_1 = slider_1
        self.slider_2 = slider_2

        self.init_Ui()

    def init_Ui(self):
        self.setWindowTitle('Настройки')
        self.min_speed_value.setValue(self.ball.min_speed)
        self.max_speed_value.setValue(self.ball.max_speed)
        self.bot_level.setValue(self.slider_1.bot_level)
        self.ball = ball
        self.min_speed_value.setRange(1, 18)
        self.min_speed_value.setRange(1, 20)
        self.bot_level.setRange(0, 10)
        self.apply_button.clicked.connect(self.apply_settings)
        self.min_speed_value.valueChanged.connect(self.min_speed_func)

    # применить настройки
    def apply_settings(self):
        min_speed = self.min_speed_value.value()
        max_speed = self.max_speed_value.value()
        level = self.bot_level.value()

        if min_speed > 0 and max_speed > 0 and max_speed > min_speed:
            self.ball.set_speed_range(min_speed, max_speed)
            self.slider_1.set_level(level)
            self.slider_2.set_level(level)
            self.status_label.setText('Изменения успешно подтверждены')
            self.status_label.setStyleSheet("background-color: rgb(0, 255, 0);")
        else:
            self.status_label.setText('Введите корректные значения')
            self.status_label.setStyleSheet("background-color: rgb(255, 0, 0);")

    def min_speed_func(self):
        minimum_speed = self.min_speed_value.value()
        max_speed_now = self.max_speed_value.value()
        if max_speed_now <= minimum_speed + 2:
            self.max_speed_value.setValue(minimum_speed + 2)


# класс для кнопки с выбором режимов
class LevelButton(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__(settings_sprites)
        self.image = load_image(LEVEL_BUT_PICT, -1)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 50
        self.rect.y = HEIGHT - 150

    def set_coords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_coords(self):
        return self.rect.x, self.rect.y, 50 + self.rect.x, \
               50 + self.rect.y

    def start_level(self):
        app = QApplication(sys.argv)
        ex = LevelsMenu()
        ex.show()
        app.exec()

    def check_click(self, pos):
        mouse_x = pos[0]
        mouse_y = pos[1]
        coords = self.get_coords()
        if mouse_x > coords[0] and mouse_x < coords[2] and mouse_y > coords[1] and \
                mouse_y < coords[3]:
            self.start_level()


# меню с выбором режим игры
class LevelsMenu(QMainWindow, Ui_LevelSettings):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_Ui()

    def init_Ui(self):
        self.setWindowTitle('Выберите режим игры')
        self.pushButton.clicked.connect(self.apply_settings)
        self.pushButton_4.clicked.connect(self.apply_settings)
        self.pushButton_2.clicked.connect(self.apply_settings)
        self.pushButton_3.clicked.connect(self.apply_settings)

    def apply_settings(self):
        global multiplayer
        multiplayer = int(self.sender().text().split('(')[-1][:-1])
        change_mode()


# класс линии, которая считывает голы
class EndLine(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__(endline_sprites)
        self.image = load_image(ENDLINE_PICT)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y
        self.score_x = 15
        self.score_y = 15
        self.score = 0
        self.mask = pygame.mask.from_surface(self.image)

    def set_y(self, y):
        self.rect.y = y

    def set_score_coords(self, x, y):
        self.score_x = x
        self.score_y = y

    def update_score(self, screen):
        font = pygame.font.Font(None, 30)
        text = font.render(str(self.score), True, (255, 255, 255))
        screen.blit(text, (self.score_x, self.score_y))
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (self.score_x, self.score_y))
        pygame.draw.rect(screen, (255, 255, 255), (self.score_x - 10, self.score_y - 10,
                                                   text_w + 20, text_h + 20), 2)

    def update_time(self, screen):
        time = arrow.now().format('HH:mm:ss')
        font = pygame.font.Font(None, 20)
        text = font.render(str(time), True, (255, 255, 255))
        screen.blit(text, (self.score_x, HEIGHT - self.score_y))
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (self.score_x, HEIGHT - self.score_y))
        pygame.draw.rect(screen, (255, 255, 255), (self.score_x - 10, HEIGHT - self.score_y - 10,
                                                   text_w + 20, text_h + 20), 2)


# класс платформы
class Slider(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__(sliders_sprites)
        self.image = load_image(SLIDER_PICT)
        self.image = pygame.transform.scale(self.image, (77, 3))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 5 * 2
        self.left_motion = False
        self.right_motion = False
        self.bot = False
        self.errors = 0
        self.count_errors = 0
        self.bot_level = 10

    def restart_errors(self):
        self.errors = 0
        self.count_errors = 0

    def update(self, ball):
        if self.bot:
            self.rect = self.rect.move(ball.rect.x - self.rect.x + self.errors, 0)
            self.count_errors += 1
            if self.rect.x >= WIDTH - 134:
                self.rect.x = WIDTH - 134
            if self.rect.x < 56:
                self.rect.x = 56
            if self.count_errors == 300:
                error_pix = 100 - self.bot_level * 10
                self.errors += random.randint(-error_pix, error_pix)
        else:
            if self.left_motion:
                if self.rect.x > 56:
                    self.rect = self.rect.move(-SLIDER_SPEED, 0)

            if self.right_motion:
                if self.rect.x < WIDTH - 134:
                    self.rect = self.rect.move(SLIDER_SPEED, 0)

    def set_bot(self):
        self.bot = True

    def set_player(self):
        self.bot = False

    def set_y(self, y):
        self.rect.y = y

    def set_level(self, level):
        self.errors = 0
        self.count_errors = 0
        self.bot_level = level


# класс боковых стенок
class Wall(pygame.sprite.Sprite):
    list_of_coords = []

    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
            Wall.list_of_coords.append([(x1, y1), (x2, y2)])

        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
            Wall.list_of_coords.append([(x1, y1), (x2, y2)])


# класс мячика
class Ball(pygame.sprite.Sprite):

    def __init__(self, *group):
        super().__init__(*group)
        self.image = load_image(BALL_PICT, -1)
        self.list_of_vectors = [-1, 1]
        self.vector_speed_x = 0
        self.vector_speed_y = 0
        self.min_speed = 1
        self.max_speed = 10
        self.speed_x = 0
        self.speed_y = 0
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.islive = False

    def set_speed_range(self, min_speed, max_speed):
        self.min_speed = min_speed
        self.max_speed = max_speed

    def get_status(self):
        return self.islive

    def restart(self):
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.speed_x = 0
        self.speed_y = 0
        self.islive = False

    def start(self):
        if not self.islive:
            self.vector_speed_x = self.list_of_vectors[random.randint(0, 1)]
            self.vector_speed_y = self.list_of_vectors[random.randint(0, 1)]
            self.speed_x = random.randint(self.min_speed, self.max_speed)
            self.speed_y = random.randint(self.min_speed, self.max_speed)
            self.islive = True

    def update(self, horizontal_borders, vertical_borders, sliders_sprites, endline,
               endline_2, antiwall_1, antiwall_2):
        self.rect = self.rect.move(self.vector_speed_x * self.speed_x,
                                   self.vector_speed_y * self.speed_y)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.rect = self.rect.move(-(self.speed_x * self.vector_speed_x),
                                       -(self.speed_y * self.vector_speed_y))
            self.vector_speed_y *= -1
            self.speed_x = random.randint(self.min_speed, self.max_speed)
            self.speed_y = random.randint(self.min_speed, self.max_speed)

        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.rect = self.rect.move(-(self.speed_x * self.vector_speed_x),
                                       -(self.speed_y * self.vector_speed_y))
            self.vector_speed_x *= -1
            self.speed_x = random.randint(self.min_speed, self.max_speed)
            self.speed_y = random.randint(self.min_speed, self.max_speed)

        if pygame.sprite.spritecollideany(self, sliders_sprites):
            self.rect = self.rect.move(-(self.speed_x * self.vector_speed_x),
                                       -(self.speed_y * self.vector_speed_y))
            self.vector_speed_y *= -1
            self.vector_speed_x *= -1
            self.speed_x = random.randint(self.min_speed, self.max_speed)
            self.speed_y = random.randint(self.min_speed, self.max_speed)

        if pygame.sprite.collide_mask(self, endline):
            self.restart()
            endline.score += 1

        if pygame.sprite.collide_mask(self, endline_2):
            self.restart()
            endline_2.score += 1

        if pygame.sprite.collide_mask(self, antiwall_1):
            self.restart()

        if pygame.sprite.collide_mask(self, antiwall_2):
            self.restart()


# стенки помогающие в непридвиденных ситуациях
class Antibugs_wall(pygame.sprite.Sprite):

    def __init__(self, x):
        super().__init__(horizontal_borders)
        self.image = load_image(ANTIBUGS_WALLS_PICT)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.mask = pygame.mask.from_surface(self.image)


# разместить стенки
def set_walls():
    Wall(LEFT_WALL_x, 20, LEFT_WALL_x, HEIGHT - 20)
    Wall(RIGHT_WALL_X, 20, RIGHT_WALL_X, HEIGHT - 20)


# анимированный спрайт (переливающаяся стенка)
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(dragons_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.rect.move(x, y)
        self.counts = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.counts += 1
        if self.counts % 12 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.image = pygame.transform.scale(self.image, (45, 250))


dragon_1 = AnimatedSprite(load_image(ANIMATED_PICT, 1), 32, 2, 2, 70)
dragon_2 = AnimatedSprite(load_image(ANIMATED_PICT, 1), 32, 2, WIDTH - 47, 70)

ball = Ball(ball_sprites)
slide_1 = Slider()
slide_2 = Slider()
slide_1.set_y(50)
slide_2.set_y(HEIGHT - 50)

set_walls()
endline = EndLine(0)
endline.set_score_coords(WIDTH - 30, RIGHT_WALL_X)
endline_2 = EndLine(HEIGHT - 10)
multiplayer = start_screen()
settings_button = SettingsButton(ball, slide_1, slide_2)
level_button = LevelButton()
antiwall_1 = Antibugs_wall(30)
antiwall_2 = Antibugs_wall(WIDTH - 30)


def change_mode():
    if multiplayer == 2:
        slide_1.set_bot()
        slide_2.set_player()
    elif multiplayer == 3:
        slide_1.set_bot()
        slide_2.set_bot()
    else:
        slide_1.set_player()
        slide_2.set_player()
    endline_2.score = 0
    endline.score = 0


change_mode()
while running:
    screen.fill(pygame.Color("black"))

    for i in Wall.list_of_coords:
        pygame.draw.line(screen, (255, 0, 0), i[0], i[1], 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            settings_button.check_click(event.pos)
            level_button.check_click(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not ball.get_status():
                    ball.start()
                else:
                    ball.restart()
            if multiplayer == 1:
                if event.key == pygame.K_LEFT:
                    slide_1.left_motion = True
                if event.key == pygame.K_RIGHT:
                    slide_1.right_motion = True
                if event.key == pygame.K_a:
                    slide_2.left_motion = True
                if event.key == pygame.K_d:
                    slide_2.right_motion = True
            elif multiplayer == 2:
                if event.key == pygame.K_LEFT:
                    slide_2.left_motion = True
                if event.key == pygame.K_RIGHT:
                    slide_2.right_motion = True
            elif multiplayer == 0:
                if event.key == pygame.K_LEFT:
                    slide_1.left_motion = True
                    slide_2.left_motion = True
                if event.key == pygame.K_RIGHT:
                    slide_1.right_motion = True
                    slide_2.right_motion = True
        if event.type == pygame.KEYUP:
            if multiplayer == 1:
                if event.key == pygame.K_LEFT:
                    slide_1.left_motion = False
                if event.key == pygame.K_RIGHT:
                    slide_1.right_motion = False
                if event.key == pygame.K_a:
                    slide_2.left_motion = False
                if event.key == pygame.K_d:
                    slide_2.right_motion = False
            if multiplayer == 2:
                if event.key == pygame.K_LEFT:
                    slide_2.left_motion = False
                if event.key == pygame.K_RIGHT:
                    slide_2.right_motion = False

            elif multiplayer == 0:
                if event.key == pygame.K_LEFT:
                    slide_1.left_motion = False
                    slide_2.left_motion = False
                if event.key == pygame.K_RIGHT:
                    slide_1.right_motion = False
                    slide_2.right_motion = False
    slide_1.update(ball)
    slide_2.update(ball)
    settings_sprites.draw(screen)
    ball_sprites.draw(screen)
    ball.update(horizontal_borders, vertical_borders, sliders_sprites, endline, endline_2,
                antiwall_1, antiwall_2)
    sliders_sprites.draw(screen)
    endline.update_score(screen)
    endline_2.update_time(screen)
    endline_2.update_score(screen)
    dragons_sprites.draw(screen)
    dragon_1.update()
    dragon_2.update()
    clock.tick(FPS)
    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
