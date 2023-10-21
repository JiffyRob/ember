# import ez_profile

import time
import inspect
import enum

start_time = time.time()
import pygame

print(f"Pygame import took {time.time()-start_time:.2f}s")

import logging

# log = logging.getLogger("ember.size")
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.FileHandler("log.log", "w+"))

import os
import sys

os.chdir(__file__.replace("pixel.py", ""))

start_time = time.time()
try:
    try:
        path = os.getcwd().replace(f"examples", "src")
        sys.path.append(path)
        import ember  # noqa
    except ModuleNotFoundError:
        path = os.path.join(os.getcwd(), "src")
        sys.path.append(str(path))
        import ember  # noqa
except RuntimeError as e:
    raise e.__cause__

from ember.style import pixel_dark as ui

print(f"Ember import took {time.time()-start_time:.2f}s")
pygame.init()

WIDTH = 801
HEIGHT = 600
ZOOM = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))

display = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()

ember.init()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

with ember.View() as view:
    with ember.VStack(spacing=6):
        ui.Button("1", h=13)
        ui.Button("2", h=13)
        ui.Button("3", h=13)
        ui.Divider()
        with ember.HStack(w=ember.FILL):
            for _ in range(3):
                ui.Switch()
        bar = ui.Slider(value=0.2)

is_running = True

while is_running:
    _mouse = pygame.mouse.get_pos()
    mouse_pos = (_mouse[0] // ZOOM, _mouse[1] // ZOOM)

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with ember.animation.EaseInOut(0.1):
                    bar.w = 150
            
            elif event.key == pygame.K_a:
                with ember.animation.EaseInOut(0.1):
                    bar.w = 100

            elif event.key == pygame.K_y:
                with ember.animation.EaseInOut(0.3):
                    button.w.value = 50 if button.w.value == 100 else 100
                
            elif event.key == pygame.K_u:
                bar.axis = 1 if bar.axis == 0 else 0

    display.fill(ui.background_color)
    view.update(display)
    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(120)
    pygame.display.flip()

pygame.quit()
