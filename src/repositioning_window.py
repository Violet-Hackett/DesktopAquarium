import pygame
import win32gui, win32con, win32api
import math
import sys
import io

OG_WINDOW_POSITION = tuple(map(int, sys.argv[1:3]))
WINDOW_SIZE = tuple(map(int, sys.argv[3:5]))
SCALE = int(sys.argv[5])
OG_MOUSE_POSITION = tuple(map(int, sys.argv[6:]))

# Disable window's automatic weird scaling
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.NOFRAME)
pygame.display.set_window_position(OG_WINDOW_POSITION)

clock = pygame.time.Clock()
frame_number = 0

# Setup for a transparent window
TRANSPARENT_COLOR_KEY = (1, 2, 3)
hwnd = pygame.display.get_wm_info()["window"] 
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED) 
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TRANSPARENT_COLOR_KEY),
                                    0, win32con.LWA_COLORKEY)

# Use win32api instead of pygame for getting mouse_down because the window focus isn't consistant
def mouse_down() -> bool:
    return win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000 != 0

while mouse_down():
    screen.fill(TRANSPARENT_COLOR_KEY)

    # Border fading in and out
    scaled_down_surface = pygame.Surface((int(WINDOW_SIZE[0]/SCALE), 
                                          int(WINDOW_SIZE[1]/SCALE)), pygame.SRCALPHA)
    border_brightness = min(255, max(0, int((math.sin(frame_number/8) + 0.5) * 255)))
    pygame.draw.rect(scaled_down_surface, (border_brightness,)*3, scaled_down_surface.get_rect(), 1)
    scaled_up_surface = pygame.transform.scale_by(scaled_down_surface, SCALE)
    screen.blit(scaled_up_surface, (0, 0))

    # Update window position to follow mouse
    mouse_pos = win32api.GetCursorPos()
    pygame.display.set_window_position((OG_WINDOW_POSITION[0] + mouse_pos[0] - OG_MOUSE_POSITION[0],
                                        OG_WINDOW_POSITION[1] + mouse_pos[1] - OG_MOUSE_POSITION[1]))
    
    pygame.display.flip()
    frame_number += 1
    clock.tick(60)

final_window_x, final_window_y = pygame.display.get_window_position()
pygame.quit()
print(f"{final_window_x} {final_window_y}")