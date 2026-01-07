import pygame
import sys
from tank import *
from organism import *
from resources import *
import graphics_resources
import state
import time

DEBUG = False
DEBUG_PRINT_INFO_FREQUENCY = 60
def quit():
    pygame.quit()
    sys.exit()

def new_tank():
    state.selected_tank = Tank(pygame.Rect(0, 0, *state.DEFAULT_TANK_SIZE), [], [])

new_tank()

# Load twin rocks as the initial tank (if it exists in saves)
try:
    initial_tank_fp = f"{state.SAVES_FP}\\Twin Rocks.tank"
    state.selected_tank = state.selected_tank.load(initial_tank_fp) # type: ignore
    state.selected_tank.filepath = initial_tank_fp
except:
    pass

pygame.init()
root = pygame.display.set_mode(state.window_size(), pygame.NOFRAME)
pygame.display.set_window_position(state.WINDOW_POSITION)
pygame.display.set_caption('Desktop Aquarium')
pygame.display.set_icon(load_texture('goby_icon', True))

running = True
next_frame = time.perf_counter()
while running:
    frame_start_time = time.perf_counter()

    # Assign a new tank if none is selected:
    if not state.selected_tank:
        new_tank()

    if state.frame_count == 50:
        for sculpture in state.selected_tank.sculptures: # type:ignore
            sculpture.simplify(0.5)

    # Check for user events
    for event in get_events():
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_ESCAPE:  
                running= False
        if event.type == pygame.QUIT:
            running= False

    # Render screen capture
    if state.selected_tank.paused: # type: ignore
        root.blit(graphics_resources.screen_capture_buffer, (0, 0)) # type: ignore
    else:
        root.blit(pull_screen_capture(), (0, 0))

    # Update and render tank
    state.selected_tank.update() # type: ignore
    if state.selected_tank:
        root.blit(state.selected_tank.render(state.SCALE, overlay_frame=DEBUG), (0, 0))

    state.last_win_mouse_position = win32api.GetCursorPos()
    state.frame_count += 1

    pygame.display.flip()
    
    time_elapsed = time.perf_counter() - frame_start_time
    time.sleep(max(0, state.frame_delay() - time_elapsed))

    if DEBUG and state.frame_count % DEBUG_PRINT_INFO_FREQUENCY == 0:
        print(f"load: {round(time_elapsed/state.frame_delay()*100, 2)} %")

quit()