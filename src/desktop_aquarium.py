import pygame
import sys
from tank import *
from organism import *
from seaweed import Seaweed
from goby import Goby
from crab import Crab
from snail import Snail
from kelpworm import KelpWorm
from resources import *
import graphics_resources
import state

def quit():
    pygame.quit()
    sys.exit()

def new_tank():
    state.selected_tank = Tank(pygame.Rect(0, 0, 165, 100), [], [])

DEBUG_INFO_FREQUENCY = 32

new_tank()

organisms: list[Organism] = []
organisms.append(KelpWorm.generate_random((60, 70)))
organisms.append(Goby.generate_random((80, 20)))
organisms.append(Goby.generate_random((80, 10)))
organisms.append(Goby.generate_random((80, 30), 5970))
organisms.append(Goby.generate_random((80, 40)))
organisms.append(Goby.generate_newborn((80, 50)))
organisms.append(Snail.generate_random((70, state.tank_height())))
organisms.append(Snail.generate_random((30, state.tank_height())))
organisms += [Seaweed.generate_random((x + random.randint(-9, 9), 
                                       state.tank_height()-1)) for x in range(0, state.tank_width(), 20)]
state.selected_tank.organisms = organisms # type: ignore

pygame.init()
root = pygame.display.set_mode(state.window_size(), pygame.NOFRAME)
pygame.display.set_window_position(state.WINDOW_POSITION)

running = True
clock = pygame.time.Clock()
while running:

    # Assign a new tank if none is selected:
    if not state.selected_tank:
        new_tank()

    # Check for user events
    for event in get_events():
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_ESCAPE:  
                quit()
        if event.type == pygame.QUIT:
            quit()

    # Render screen capture
    if state.selected_tank.paused: # type: ignore
        root.blit(graphics_resources.screen_capture_buffer, (0, 0)) # type: ignore
    else:
        root.blit(pull_screen_capture(), (0, 0))

    # Update and render tank
    state.selected_tank.update() # type: ignore
    if state.selected_tank:
        root.blit(state.selected_tank.render(state.SCALE, overlay_frame=False), (0, 0))

    state.last_win_mouse_position = win32api.GetCursorPos()
    clock.tick()
    state.frame_count += 1
    if state.frame_count % DEBUG_INFO_FREQUENCY == 0:
        print("fps: ", round(clock.get_fps(), 1))

    pygame.display.flip()
    pygame.time.wait(state.frame_delay_ms())