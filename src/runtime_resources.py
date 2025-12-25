import pygame
import state

def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    x1, y1 = p1
    x2, y2 = p2
    return ((x2-x1)**2 + (y2-y1)**2)**(1/2)

def get_relative_mouse_position() -> tuple[float, float]:
    x, y = pygame.mouse.get_pos()
    return (x/state.SCALE, y/state.SCALE)