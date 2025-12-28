from pathlib import Path
from enum import Enum
import win32api

selected_tank = None

# Element sizes
TANK_SIZE: tuple[int, int] = (200, 100)
SCALE: int = 6
UI_HEIGHT: int = 11
WINDOW_SIZE: tuple[int, int] = (TANK_SIZE[0] * SCALE, (TANK_SIZE[1] + UI_HEIGHT) * SCALE)
WINDOW_POSITION: tuple[int, int] = (0, 0)
last_win_mouse_position = win32api.GetCursorPos()

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
