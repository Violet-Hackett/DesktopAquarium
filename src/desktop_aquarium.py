import pygame
import sys
from tank import *
from organism import *
from seaweed import Seaweed
from goby import Goby
from crab import Crab
from snail import Snail
from resources import *
from graphics_resources import *
import state

def save_and_quit():
    pygame.quit()
    sys.exit()

DEBUG_INFO_FREQUENCY = 8

pygame.init()
root = pygame.display.set_mode(state.WINDOW_SIZE, pygame.NOFRAME)
pygame.display.set_window_position(state.WINDOW_POSITION)

running = True
clock = pygame.time.Clock()

organisms: list[Organism] = []
organisms.append(Goby.generate_random((80, 20)))
organisms.append(Goby.generate_random((80, 10)))
organisms.append(Goby.generate_random((80, 30)))
organisms.append(Snail.generate_random((50, 100)))
organisms.append(Snail.generate_random((30, 100)))
organisms += [Seaweed.generate_random((x, state.TANK_SIZE[1]-1)) for x in range(85, 125, 10)]
selected_tank = Tank(pygame.Rect(0, 0, state.TANK_SIZE[0], state.TANK_SIZE[1]), organisms)

while running:

    pygame.time.wait(state.FRAME_DELAY_MS)

    # Check for user events
    for event in get_events():
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_ESCAPE:  
                save_and_quit()
        if event.type == pygame.QUIT:
            save_and_quit()

    # Render screen capture
    root.blit(pull_screen_capture(), (0, 0))

    # Update and render tank
    selected_tank.update()
    root.blit(selected_tank.render(state.SCALE, overlay_frame=False), (0, 0))

    #pygame.image.save(selected_tank.render(1, overlay_frame=False), "capture.png")

    clock.tick()
    state.frame_count += 1
    if state.frame_count % DEBUG_INFO_FREQUENCY == 0:
        print("fps: ", round(clock.get_fps(), 1))

    pygame.display.flip()