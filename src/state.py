from pathlib import Path
from enum import Enum
import win32api
import pygame
import sys

selected_tank = None

# Measurements
SCALE: int = 5
UI_HEIGHT: int = 19
WINDOW_POSITION: tuple[int, int] = (0, 0)
last_win_mouse_position = win32api.GetCursorPos()
def tank_size() -> tuple[int, int]:
    if not selected_tank:
        raise BufferError("Cannot get tank dimensions: no tank assigned")
    return selected_tank.rect.size
def window_size() -> tuple[int, int]:
    return (tank_size()[0] * SCALE, (tank_size()[1] + UI_HEIGHT) * SCALE)

def tank_width() -> int:
    return tank_size()[0]
def tank_height() -> int:
    return tank_size()[1]

def verify_tank_dimensions(size: tuple[int, int]):
    if size[0] < MINIMUM_TANK_WIDTH or size[1] < MINIMUM_TANK_HEIGHT:
        print(f"WARNING: Tank too small ({size} < {(MINIMUM_TANK_WIDTH, MINIMUM_TANK_HEIGHT)})! UI will be broken")
        return False
    return True

def change_mouse_position(dx: float, dy: float):
    old_x, old_y = pygame.mouse.get_pos()
    pygame.mouse.set_pos(old_x + dx * SCALE, old_y + dy * SCALE)
    
def change_tank_size(dx: int, dy: int, move_mouse: bool = False):
    global DEFAULT_TANK_SIZE

    if not selected_tank:
        raise BufferError("Cannot change tank size: no tank assigned")
    
    new_size = (selected_tank.rect.width + dx, selected_tank.rect.height + dy )
    if verify_tank_dimensions(new_size):
        selected_tank.rect = pygame.Rect(0, 0, *new_size)
        pygame.display.set_mode(window_size(), pygame.NOFRAME)
        DEFAULT_TANK_SIZE = new_size
        buffer_update_flags.append(BufferKey.BACKGROUND)

        if move_mouse:
            change_mouse_position(dx, dy)

def increment_width():
    change_tank_size(5, 0, True)
def decrement_width():
    change_tank_size(-5, 0, True)
def increment_height():
    change_tank_size(0, 5, True)
def decrement_height():
    change_tank_size(0, -5, True)

DEFAULT_TANK_SIZE = (200, 100)
MINIMUM_TANK_WIDTH = 160
MINIMUM_TANK_HEIGHT = 25

def get_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


DESKTOP_AQUARIUM_FP = get_base_path()
SAVES_FP = str(DESKTOP_AQUARIUM_FP) + "\\saves"
FONT_FP = str(DESKTOP_AQUARIUM_FP) + "\\bin\\font"
ICONS_FP = str(DESKTOP_AQUARIUM_FP) + "\\bin\\icons"
TEXTURES_FP = str(DESKTOP_AQUARIUM_FP) + "\\bin\\textures"

# Framerate control
DEFAULT_FPS = 15
fps: int = DEFAULT_FPS
frame_count: int = 0
def frame_delay() -> float:
    return 1 / fps

# Buffer update scheduling
class BufferKey(Enum):
    BACKGROUND = 0
    STATIC_ENVIORMENT = 1
    UI = 2
    RENDERED_FRAME = 3
buffer_update_flags: list[BufferKey] = []

# Physics
GRAVITY: float = 1
vertex_grabbed = None

def load_tank():
    global selected_tank
    global frame_count
    if not selected_tank:
        raise BufferError("Cannot load tank: no tank assigned")
    new_tank = selected_tank.load() 
    if new_tank:
        selected_tank = new_tank
        pygame.display.set_mode(window_size(), pygame.NOFRAME)
        frame_count = 0

def unassign_selected_tank():
    global selected_tank
    selected_tank = None