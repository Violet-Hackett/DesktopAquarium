from pathlib import Path
import pygame

TANK_SIZE = (200, 100)
WINDOW_SIZE = (1200, 600)
SCALE = WINDOW_SIZE[0] / TANK_SIZE[0]

frame_count: int = 0

DESKTOP_AQUARIUM_FP = Path(__file__).resolve().parent.parent
TEXTURES_FP = str(DESKTOP_AQUARIUM_FP) + "\\bin\\textures"

FPS = 15
FRAME_DELAY_MS = int(1000 / FPS)

GRAVITY = 1

vertex_grabbed = None