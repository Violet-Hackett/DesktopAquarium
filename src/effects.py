import pygame
import state
import math

LIGHT_SOURCE = (state.TANK_SIZE[0]/3, -state.TANK_SIZE[1]*2)
GODRAY_FREQUENCY = 1 # Frames to wait between spawning godrays
GODRAY_LIFESPAN = 15
GODRAY_BRIGHTNESS = 0.03
GODRAY_BLUR = 2
class Godray:
    def __init__(self, size: float, slope: float):
        self.size = size
        self.slope = slope
        self.age: int = 0
        self.buffer: pygame.Surface = pygame.Surface(state.TANK_SIZE, pygame.SRCALPHA)
        self.init_buffer()

    def init_buffer(self):
        bottom_edge_x_value = LIGHT_SOURCE[0] - (state.TANK_SIZE[1]-LIGHT_SOURCE[1])*self.slope
        bottom_edge_width = (state.TANK_SIZE[1]-LIGHT_SOURCE[1])*self.size
        pygame.draw.polygon(self.buffer, pygame.Color(255, 255, 255), [
            LIGHT_SOURCE,
            (bottom_edge_x_value - bottom_edge_width/2, state.TANK_SIZE[1]),
            (bottom_edge_x_value + bottom_edge_width/2, state.TANK_SIZE[1])
        ])
    
    def update(self):
        self.age += 1

    def calculate_alpha(self) -> int:
        t = min(self.age / GODRAY_LIFESPAN, 1.0)
        fade = 0.5 - 0.5 * math.cos(t * math.pi * 2)
        alpha = int(fade * 255 * GODRAY_BRIGHTNESS)
        alpha = max(0, min(255, alpha))
        return alpha

    def render(self) -> pygame.Surface:
        surface = self.buffer.copy()
        surface.fill((255, 255, 255, self.calculate_alpha()), special_flags=pygame.BLEND_RGBA_MULT)
        return surface