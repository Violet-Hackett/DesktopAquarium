import pygame
import state
import random
from enum import Enum
import os

def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    x1, y1 = p1
    x2, y2 = p2
    return ((x2-x1)**2 + (y2-y1)**2)**(1/2)

def get_relative_mouse_position() -> tuple[float, float]:
    x, y = pygame.mouse.get_pos()
    return (x/state.SCALE, y/state.SCALE)

def biased_random_beta(toward=0.5, strength=5.0):
    a = 1 + toward * strength
    b = 1 + (1 - toward) * strength
    return random.betavariate(a, b)

event_cache: list[pygame.Event] = []
events_last_updated = 0
def get_events() -> list[pygame.Event]:
    global event_cache
    global events_last_updated
    if events_last_updated != state.frame_count:
        event_cache = pygame.event.get()
        events_last_updated = state.frame_count
    return event_cache

mouse_press_cache: tuple[bool, bool, bool] = (False, False, False)
mouse_press_cache_last_updated = 0
def get_mouse_presses() -> tuple[bool, bool, bool]:
    global mouse_press_cache
    global mouse_press_cache_last_updated
    if mouse_press_cache_last_updated != state.frame_count:
        mouse_press_cache = pygame.mouse.get_pressed()
        mouse_press_cache_last_updated = state.frame_count
    return mouse_press_cache

mouse_velocity: tuple[int, int] = (0, 0)
mouse_velocity_last_updated = 0
def get_mouse_velocity() -> tuple[int, int]:
    global mouse_velocity
    global mouse_velocity_last_updated
    if mouse_velocity_last_updated != state.frame_count:
        mouse_velocity = pygame.mouse.get_rel()
        mouse_velocity_last_updated = state.frame_count
    return mouse_velocity

class Wall(Enum):
    RIGHT = 0
    LEFT = 1
    TOP = 2
    BOTTOM = 3

def wall_to_direction(wall: Wall) -> tuple[float, float]:
    match wall:
        case Wall.RIGHT:
            return (0, -1)
        case Wall.LEFT:
            return (0, 1)
        case Wall.TOP:
            return (-1, 0)
        case Wall.BOTTOM:
            return (1, 0)
        
def direction_vector(p1, p2):
    return normalize((p2[0] - p1[0], p2[1] - p1[1]))

def normalize(vector: tuple[float, float]):
    magnitude = distance((0, 0), vector)
    return (vector[0]/magnitude, vector[1]/magnitude)

def graduate_value_towards(current_value: float, target_value: float, rate: float) -> float:
        return (current_value - target_value) / (1 + rate) + target_value