import pygame._view
import pygame
import os
from pygame.locals import FULLSCREEN, DOUBLEBUF
from math import cos, sin, radians, floor, atan2, pi, degrees
from random import randint, random, getrandbits

# Game files
CURRENT_DIR = os.getcwd()
SPRITE_DIR = os.path.join(CURRENT_DIR, 'sprites')

# Game window dimensions
WINDOW_X = 16 * 80  # Game window width
WINDOW_Y = 9 * 80  # Game window height

# Color tuples for Pygame
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 50, 100)

# Defaults
MISSILE_SIZE = 20
MISSILE_SPEED = 3
MISSILE_TURN_SENSITIVITY = radians(2)
MISSILE_SPAWN_TIMER = 1000

PLAYER_X_SIZE = 50
PLAYER_Y_SIZE = 80
PLAYER_SPEED = 5
PLAYER_TURN_SENSITIVITY = radians(5)
INTERCEPTOR_SPEED = 7
INTERCEPTOR_SIZE = 10
FPS = 60

# Pygame initialization
pygame.init()
window = pygame.display.set_mode((WINDOW_X, WINDOW_Y), FULLSCREEN | DOUBLEBUF)
pygame.display.set_caption("Missiles")
clock = pygame.time.Clock()  # Framerate controller
pygame.key.set_repeat(100, 100)


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        temp = pygame.image.load(image_file).convert()
        self.image = pygame.transform.smoothscale(temp, (WINDOW_X, WINDOW_Y))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

    def render(self):
        window.blit(self.image, self.rect)


class Missiles:
    def __init__(self, list_missiles):
        self.list_missiles = list_missiles
        self.last_spawn = 0

    def add_missile(self):
        spawn_up, spawn_left = getrandbits(1), getrandbits(1)
        if spawn_up:
            rand_x = randint(-200, 0)
        else:
            rand_x = randint(WINDOW_X, WINDOW_X + 200)
        if spawn_left:
            rand_y = randint(-200, 0)
        else:
            rand_y = randint(WINDOW_Y, WINDOW_Y + 200)
        self.list_missiles.append(
            Missile(rand_x, rand_y, MISSILE_SIZE, (randint(20, 255), randint(20, 255), randint(20, 255))))

    def move(self, player_x, player_y):
        for missile in self.list_missiles:
            missile.move(player_x, player_y)

    def get_list(self):
        return self.list_missiles

    def spawn(self, milliseconds):
        self.last_spawn += milliseconds
        if self.last_spawn > MISSILE_SPAWN_TIMER:
            self.add_missile()
            self.last_spawn = 0

    def render(self):
        for missile in self.list_missiles:
            missile.render()


class Missile:
    def __init__(self, x_coordinate, y_coordinate, size_param, color_tuple):
        self.x = x_coordinate
        self.y = y_coordinate
        self.size = size_param
        self.color = color_tuple
        self.sprite = pygame.image.load(os.path.join(SPRITE_DIR, 'missile.png')).convert_alpha()
        self.direction = 0

    def move(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        rads = atan2(dy, dx)  # Angle between the missile and the player
        rads %= 2 * pi  # Converting to Pygame coordinate system. Ex : -30 will be converted to 330
        # self.direction = rads
        if self.direction < rads:
            self.direction += MISSILE_TURN_SENSITIVITY
        elif self.direction > rads:
            self.direction -= MISSILE_TURN_SENSITIVITY
        self.direction %= 2 * pi
        self.x += MISSILE_SPEED * cos(self.direction)  # X_new = X + Speed * cos(Angle)
        self.y += MISSILE_SPEED * sin(self.direction)  # Y_new = Y + Speed * sin(Angle)

    def render(self):
        rotated_sprite = pygame.transform.rotate(self.sprite, -(degrees(self.direction) + 90))
        missile_rect = rotated_sprite.get_rect()
        missile_rect.center = (self.x, self.y)
        window.blit(rotated_sprite, missile_rect)


class Interceptor:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.sprite = pygame.image.load(os.path.join(SPRITE_DIR, 'missile.png')).convert_alpha()

    def move(self):
        self.x += INTERCEPTOR_SPEED * cos(self.direction)
        self.y += INTERCEPTOR_SPEED * sin(self.direction)

    def render(self):
        rotated_sprite = pygame.transform.rotate(self.sprite, -(degrees(self.direction) + 90))
        rect = rotated_sprite.get_rect()
        rect.center = (self.x, self.y)
        window.blit(rotated_sprite, rect)


class Interceptors:
    def __init__(self):
        self.interceptors = []

    def add_interceptor(self, x, y, direction):
        self.interceptors.append(Interceptor(x, y, direction))

    def move(self):
        for m in self.interceptors[:]:
            m.move()
            if m.x < 0 or m.x > WINDOW_X or m.y < 0 or m.y > WINDOW_Y:
                self.interceptors.remove(m)

    def render(self):
        for m in self.interceptors:
            m.render()

    def get_list(self):
        return self.interceptors

    def remove(self, interceptor):
        if interceptor in self.interceptors:
            self.interceptors.remove(interceptor)


class Player:
    def __init__(self, x_coordinate, y_coordinate, player_length, player_height, color_tuple, motion_radians):
        self.x = x_coordinate
        self.y = y_coordinate
        self.length = player_length
        self.height = player_height
        self.color = color_tuple
        self.direction = motion_radians

        # initializing sprite
        temp = pygame.image.load(os.path.join(SPRITE_DIR, 'player.png'))
        self.sprite = pygame.transform.smoothscale(temp, (PLAYER_X_SIZE, PLAYER_Y_SIZE))
        transColor = self.sprite.get_at((0, 0))
        self.sprite.set_colorkey(transColor)
        self.sprite.convert_alpha()

    def shoot(self, interceptors):
        interceptors.add_interceptor(self.x, self.y, self.direction)

    def move_forward(self):
        self.x += PLAYER_SPEED * cos(self.direction)
        self.y += PLAYER_SPEED * sin(self.direction)

    def move_backward(self):
        self.x -= PLAYER_SPEED * cos(self.direction)
        self.y -= PLAYER_SPEED * sin(self.direction)

    def turn_right(self):
        self.direction += PLAYER_TURN_SENSITIVITY

    def turn_left(self):
        self.direction -= PLAYER_TURN_SENSITIVITY

    def render(self):
        self.direction %= 2 * pi
        rotated_sprite = pygame.transform.rotate(self.sprite, -(degrees(self.direction) + 90))
        player_rect = rotated_sprite.get_rect()
        player_rect.center = (self.x, self.y)
        window.blit(rotated_sprite, player_rect)


class EndText:
    @staticmethod
    def render(run_time):
        basicFont = pygame.font.SysFont(None, 48)

        text = basicFont.render("You lasted " + str(run_time / 1000) + " seconds.", True, WHITE)
        paper = pygame.Surface((text.get_width(), text.get_height()))
        paper.fill(DARK_BLUE)
        paper.set_alpha(120)
        textRect = text.get_rect()
        textRect.centerx = window.get_rect().centerx
        textRect.centery = window.get_rect().centery
        text = text.convert_alpha()
        window.blit(paper, textRect)
        window.blit(text, textRect)

        text2 = basicFont.render("Press ESC to Exit or Space to Continue.", True, WHITE)
        paper2 = pygame.Surface((text2.get_width(), text2.get_height()))
        paper2.fill(DARK_BLUE)
        paper2.set_alpha(120)
        textRect2 = text2.get_rect()
        textRect2.centerx = window.get_rect().centerx
        textRect2.centery = window.get_rect().centery + 40
        text2 = text2.convert_alpha()
        window.blit(paper2, textRect2)
        window.blit(text2, textRect2)


def check_lose(x, y, missiles):
    for missile in missiles.get_list():
        if ((missile.x <= x <= missile.x + 20 and missile.y <= y <= missile.y + 20) or
                (missile.x <= x + 10 <= missile.x + 20 and missile.y <= y <= missile.y + 20) or
                (missile.x <= x <= missile.x + 20 and missile.y <= y + 10 <= missile.y + 20) or
                (missile.x <= x + 10 <= missile.x + 20 and missile.y <= y + 10 <= missile.y + 20) or
                (x < 0) or (x + 10 > WINDOW_X) or (y < 0) or (y + 10 > WINDOW_Y)):
            return True  # Returns True when any of the missile collides with the player or player touches boundary


def game_loop():
    # Initializing resources
    background = Background(os.path.join(SPRITE_DIR, 'background.jpg'), [0, 0])
    missiles = Missiles([Missile(0, 0, MISSILE_SIZE, RED),
                         Missile(WINDOW_X - MISSILE_SIZE, WINDOW_Y - MISSILE_SIZE, MISSILE_SIZE, GREEN),
                         Missile(WINDOW_X - MISSILE_SIZE, 0, MISSILE_SIZE, BLUE),
                         Missile(0, WINDOW_Y - MISSILE_SIZE, MISSILE_SIZE, YELLOW)])
    interceptors = Interceptors()
    player = Player(floor(WINDOW_X / 2), floor(WINDOW_Y / 2), PLAYER_X_SIZE, PLAYER_Y_SIZE, WHITE, radians(270))

    exit_flag = False
    run_time = 0
    # GAME LOOP
    while not exit_flag:
        milliseconds = clock.tick(FPS)
        run_time += milliseconds

        # Input process
        events = pygame.event.get()
        key_presses = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot(interceptors)
        if key_presses[pygame.K_UP]:
            player.move_forward()
        if key_presses[pygame.K_RIGHT]:
            player.turn_right()
        if key_presses[pygame.K_DOWN]:
            player.move_backward()
        if key_presses[pygame.K_LEFT]:
            player.turn_left()
        if key_presses[pygame.K_ESCAPE]:
            return True

        # Update NPCs
        missiles.move(player.x, player.y)
        missiles.spawn(milliseconds)
        interceptors.move()

        # Collision detection between interceptors and missiles
        for interceptor in interceptors.get_list()[:]:
            for missile in missiles.get_list()[:]:
                if (abs(interceptor.x - missile.x) < MISSILE_SIZE and
                        abs(interceptor.y - missile.y) < MISSILE_SIZE):
                    interceptors.remove(interceptor)
                    missiles.get_list().remove(missile)
                    break

        # Screen rendering
        window.fill(WHITE)
        background.render()
        player.render()
        missiles.render()
        interceptors.render()

        # Check game event
        if check_lose(player.x, player.y, missiles):
            exit_flag = True

        pygame.display.flip()
    EndText().render(run_time)
    pygame.display.update()
    while not (key_presses[pygame.K_ESCAPE] or key_presses[pygame.K_SPACE]):
        pygame.event.wait()
        events = pygame.event.get()
        key_presses = pygame.key.get_pressed()
        if key_presses[pygame.K_ESCAPE]:
            return True
        if key_presses[pygame.K_SPACE]:
            return False


exit_game = False
while not exit_game:
    exit_game = game_loop()
pygame.quit()
