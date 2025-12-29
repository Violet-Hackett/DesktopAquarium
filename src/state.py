from pathlib import Path
from enum import Enum
import win32api

selected_tank = None

# Measurements
SCALE: int = 8
UI_HEIGHT: int = 11
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

# Filepaths
DESKTOP_AQUARIUM_FP = Path(__file__).resolve().parent.parent
TEXTURES_FP = str(DESKTOP_AQUARIUM_FP) + "\\bin\\textures"

# Framerate control
DEFAULT_FPS = 15
fps: int = DEFAULT_FPS
frame_count: int = 0
def frame_delay_ms() -> int:
    return int(1000 / fps)

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
    if not selected_tank:
        raise BufferError("Cannot load tank: no tank assigned")
    selected_tank = selected_tank.load() 

def unassign_selected_tank():
    global selected_tank
    selected_tank = None