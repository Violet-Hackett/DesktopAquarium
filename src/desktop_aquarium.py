import pygame
import win32api
import win32con
import win32gui
import sys
from tank import *
from organism import *
from seaweed import Seaweed
from goby import Goby
from runtime_resources import *

def save_and_quit():
    pygame.quit()
    sys.exit()

FPS = 15
FRAME_DELAY_MS = int(1000 / FPS)
DEBUG_INFO_FREQUENCY = 8

TRANSPARENT_COLOR_KEY = (1, 28, 44)
#TRANSPARENT_COLOR_KEY = (22, 28, 44)
pygame.init()
root = pygame.display.set_mode(WINDOW_SIZE)#, pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(
                       hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TRANSPARENT_COLOR_KEY), 0, win32con.LWA_COLORKEY)

running = True
clock = pygame.time.Clock()
frame_count = 0

organisms: list[Organism] = [Seaweed.generate_random((x, TANK_SIZE[1]-1)) for x in range(85, 125, 10)]
organisms.append(Goby.generate_random((80, 20)))
organisms.append(Goby.generate_random((80, 10)))
organisms.append(Goby.generate_random((80, 30)))
selected_tank = Tank(pygame.Rect(0, 0, TANK_SIZE[0], TANK_SIZE[1]), organisms)

while running:

    pygame.time.wait(FRAME_DELAY_MS)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_ESCAPE:  
                save_and_quit()
        if event.type == pygame.QUIT:
            save_and_quit()

    selected_tank.update()
    root.blit(selected_tank.render(SCALE, render_procedural_texture=True, overlay_frame=True), (0, 0))

    clock.tick()
    frame_count += 1
    if frame_count % DEBUG_INFO_FREQUENCY == 0:
        print("fps: ", clock.get_fps())

    pygame.display.flip()