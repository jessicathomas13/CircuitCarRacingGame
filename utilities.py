import pygame


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def rotate_image(window, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_r = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    window.blit(rotated_image, new_r.topleft)


def blit_text(window, font, text):
    render = font.render(text, 1, (255, 255, 255))
    window.blit(render, (window.get_width() / 2 - render.get_width() / 2 , window.get_height()/2 - render.get_height() / 2 -20))
