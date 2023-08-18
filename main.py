import pygame
import time
import math
from utilities import scale_image, rotate_image, blit_text
pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
RACETRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
BORDER_MASK = pygame.mask.from_surface(BORDER)
FINISH_LINE = pygame.image.load("imgs/finish.png")
FINISH_POSITION = (113, 230)
FINISH_MASK = pygame.mask.from_surface(FINISH_LINE)
PLAYER = scale_image(pygame.image.load("imgs/red-car.png"), 0.51)
COMPUTER = scale_image(pygame.image.load("imgs/gold-car.png"), 0.51)

WIDTH, HEIGHT = RACETRACK.get_width(), RACETRACK.get_height()
window = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Mister Pixel 16 pt - Regular", 35)
FPS = 60
PATH = [(153, 115), (83, 66), (48, 130), (57, 411), (296, 648), (382, 459), (485, 428), (532, 498), (570, 649),
        (661, 564), (634, 338), (465, 315), (350, 282), (453, 222), (637, 224), (637, 80), (387, 55), (260, 74),
        (244, 228), (247, 347), (165, 336), (156, 239)]

pygame.display.set_caption("Car Racing Game")


class GameInfo:
    LEVELS = 2

    def __init__(self, level=1):
        self.FONT = pygame.font.SysFont("Mister Pixel 16 pt - Regular", 35)
        self.level = level
        self.start = False
        self.level_time = 0

    def next_level(self):
        self.level += 1
        self.start = False

    def reset(self):
        self.level = 1
        self.start = False
        self.level_time = 0

    def game_over(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.start = True
        self.level_time = time.time()

    def get_level_time(self):
        if not self.start:
            return 0
        return round(time.time() - self.level_time)


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
    START_POSITION = (160, 180)

    def reduce_speed(self):
        self.velocity = max(self.velocity - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.velocity = -self.velocity
        self.move()

    def reset(self):
        self.x, self.y = self.START_POSITION
        self.angle = 0
        self.velocity = 0


class ComputerCar(AbstractCar):
    IMAGE = COMPUTER
    START_POSITION = (130, 180)

    def __init__(self, max_velocity, rotation_velocity, path=[]):
        super().__init__(max_velocity, rotation_velocity)
        self.path = path
        self.current = 0
        self.velocity = max_velocity

    def draw_points(self, window):
        for p in self.path:
            pygame.draw.circle(window, (255, 0, 0), p, 5)

    def draw(self, window):
        super().draw(window)
        "self.draw_points(window)"

    def calculate_angle(self):
        target_x, target_y = self.path[self.current]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            new_angle = math.pi / 2
        else:
            new_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            new_angle += math.pi
        diff_angle = self.angle - math.degrees(new_angle)
        if diff_angle >= 180:
            diff_angle -= 360
        if diff_angle > 0:
            self.angle -= min(self.rotation_velocity, abs(diff_angle))
        else:
            self.angle += min(self.rotation_velocity, abs(diff_angle))

    def update_point(self):
        target = self.path[self.current]
        rectangle = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if rectangle.collidepoint(*target):
            self.current += 1

    def move(self):
        if self.current >= len(self.path):
            return

        self.calculate_angle()
        self.update_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.velocity = self.max_velocity + (level - 1)*0.2
        self.current = 0

    def reset(self):
        self.x, self.y = self.START_POSITION
        self.angle = 0
        self.velocity = self.max_velocity
        self.current = 0


def draw(window, images, player_car, computer_car, game_info):
    for image, position in images:
        window.blit(image, position)

    level_text = FONT.render(f"Level {game_info.level}", 1, (0,0,0))
    window.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))
    time_text = FONT.render(f"Time: {game_info.get_level_time()}s", 1, (0,0,0))
    window.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))
    velocity_text = FONT.render(f"Velocity: {round(player_car.velocity, 1)}px/s", 1, (0,0,0))
    window.blit(velocity_text, (10, HEIGHT - velocity_text.get_height() - 10))

    player_car.draw(window)
    computer_car.draw(window)
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


def handle_collision(player_car, computer_car, game_info):
    if player_car.collision(BORDER_MASK) is not None:
        player_car.bounce()
    computer_finish_poi = computer_car.collision(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi is not None:
        blit_text(window, FONT, "YOU LOSE!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        print("Computer Wins!")
        player_car.reset()
        computer_car.reset()

    player_finish_poi = player_car.collision(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi is not None:
        if player_finish_poi[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)
            print("You Win!")


images = [(GRASS, (0, 0)), (RACETRACK, (0, 0)), (FINISH_LINE, FINISH_POSITION), (BORDER, (0, 0))]
run = True
clock = pygame.time.Clock()
player_car = PlayerCar(3, 3)
computer_car = ComputerCar(0.9, 2, PATH)
game_info = GameInfo()
while run:
    clock.tick(FPS)

    draw(window, images, player_car, computer_car, game_info)

    while not game_info.start:
        blit_text(window, FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)
    computer_car.move()
    handle_collision(player_car, computer_car, game_info)

    if game_info.game_over():
        blit_text(window, FONT, "YOU WON!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()


pygame.quit()
