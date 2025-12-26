from pathlib import Path
from enum import Enum

# Element sizes
TANK_SIZE: tuple[int, int] = (200, 100)
SCALE: int = 6
UI_HEIGHT: int = 11
WINDOW_SIZE: tuple[int, int] = (TANK_SIZE[0] * SCALE, (TANK_SIZE[1] + UI_HEIGHT) * SCALE)
WINDOW_POSITION: tuple[int, int] = (0, 0)

# Filepaths
DESKTOP_AQUARIUM_FP = Path(__file__).resolve().parent.parent
TEXTURES_FP = str(DESKTOP_AQUARIUM_FP) + "\\bin\\textures"

# Framerate control
FPS: int = 15
FRAME_DELAY_MS = int(1000 / FPS)
frame_count: int = 0

# Buffer update scheduling
class BufferKey(Enum):
    BACKGROUND = 0
    STATIC_ENVIORMENT = 1
    UI = 2
buffer_update_flags: list[BufferKey] = []

# Physics
GRAVITY: float = 1
vertex_grabbed = None
