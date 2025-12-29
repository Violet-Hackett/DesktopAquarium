import pygame
import state
import math

AMBIENT_BUBBLE_FREQUENCY = 15 # Frames to wait between spawning bubbles
BUBBLE_DENSITY = 0.5
BUBBLE_COLOR = (255, 255, 255)
BUBBLE_ALPHA = 10
MAX_BUBBLE_SIZE = 3
class Bubble:
    def __init__(self, radius: float, x: float, y: float):
        self.radius = radius
        self.x = x
        self.y = y

    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    def update(self):
        self.y -= (1/BUBBLE_DENSITY)*state.GRAVITY

    def render_onto(self, surface: pygame.Surface):
        # Bubble interior
        pygame.draw.circle(surface, (*BUBBLE_COLOR, BUBBLE_ALPHA), self.position(), self.radius)
        # Bubble outline
        pygame.draw.circle(surface, (*BUBBLE_COLOR, min(255, BUBBLE_ALPHA*2)), self.position(), self.radius, 1)

GODRAY_FREQUENCY = 1 # Frames to wait between spawning godrays
GODRAY_LIFESPAN = 15
GODRAY_BRIGHTNESS = 0.03
GODRAY_BLUR = 2
class Godray:
    def __init__(self, size: float, slope: float, light_source: tuple[int, int] | None = None):
        self.size = size
        self.slope = slope
        self.age: int = 0
        self.buffer: pygame.Surface = pygame.Surface(state.tank_size(), pygame.SRCALPHA)
        if not light_source:
            self.light_source = (state.tank_width()/3, -state.tank_height()*2)
        else:
            self.light_source = light_source
        self.init_buffer()

    def init_buffer(self):
        bottom_edge_x_value = self.light_source[0] - (state.tank_height()-self.light_source[1])*self.slope
        bottom_edge_width = (state.tank_height()-self.light_source[1])*self.size
        pygame.draw.polygon(self.buffer, pygame.Color(255, 255, 255), [
            self.light_source,
            (bottom_edge_x_value - bottom_edge_width/2, state.tank_height()),
            (bottom_edge_x_value + bottom_edge_width/2, state.tank_height())
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