import pygame
import time
import math
from utilities import scale_image, rotate_image

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
RACETRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
BORDER_MASK = pygame.mask.from_surface(BORDER)
FINISH_LINE = pygame.image.load("imgs/finish.png")
PLAYER = scale_image(pygame.image.load("imgs/purple-car.png"), 0.52)
COMPUTER = scale_image(pygame.image.load("imgs/red-car.png"), 0.52)

WIDTH, HEIGHT = RACETRACK.get_width(), RACETRACK.get_height()
window = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
pygame.display.set_caption("Car Racing Game")


class AbstractCar:

    def __init__(self, max_velocity, rotation_velocity):
        self.image = self.IMAGE
        self.max_velocity = max_velocity
        self.velocity = 0
        self.rotation_velocity = rotation_velocity
        self.angle = 0
        self.x, self.y = self.START_POSITION
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_velocity
        elif right:
            self.angle -= self.rotation_velocity

    def draw(self, window):
        rotate_image(window, self.image, (self.x, self.y), self.angle)

    def forward(self):
        self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        self.move()

    def backward(self):
        self.velocity = max(self.velocity - self.acceleration, -self.max_velocity / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.velocity
        horizontal = math.sin(radians) * self.velocity
        self.y -= vertical
        self.x -= horizontal

    def collision(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.image)
        offset = (int(self.x - x), int(self.y - y))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

class PlayerCar(AbstractCar):
    IMAGE = PLAYER
    START_POSITION = (160, 200)

    def reduce_speed(self):
        self.velocity = max(self.velocity - self.acceleration / 2, 0)
        self.move()
    def bounce(self):
        self.velocity = -self.velocity
        self.move()

def draw(window, images, player_car):
    for image, position in images:
        window.blit(image, position)
    player_car.draw(window)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.backward()

    if not moved:
        player_car.reduce_speed()


images = [(GRASS, (0, 0)), (RACETRACK, (0, 0))]
run = True
clock = pygame.time.Clock()
player_car = PlayerCar(4, 4)
while run:
    clock.tick(FPS)

    draw(window, images, player_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    move_player(player_car)

    if player_car.collision(BORDER_MASK) != None:
        player_car.bounce()

pygame.quit()
