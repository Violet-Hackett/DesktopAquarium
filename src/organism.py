import pygame
from softbody import *
import random
from enum import Enum

FRAME_VERTEX_COLOR = pygame.Color(0, 255, 0)
FRAME_LINK_COLOR = pygame.Color(255, 0, 0, 175)
FRAME_INVISIBLE_LINK_COLOR = pygame.Color(70, 70, 70, 100)
FRAME_VELOCITY_COLOR = pygame.Color(0, 0, 255, 175)
BLACK = pygame.Color(0, 0, 0)

class AIStatus(Enum):
    NONE = 0
    WANDERING = 1
    FLEEING = 2

# Abstract class
class Organism:
    def __init__(self, softbody: Softbody):
        self.softbody = softbody

    def root_position(self) -> tuple[float, float]:
        return (self.softbody.vertices[0].x,
                self.softbody.vertices[0].y)

    # Abstract method
    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        raise NotImplementedError()
    
    def render_frame(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        for vertex in self.softbody.vertices:
            p1 = (int(vertex.x), int(vertex.y))
            p2 = (int(vertex.lx), int(vertex.ly))
            pygame.draw.line(surface, FRAME_VELOCITY_COLOR, p1, p2)
        
        for link in self.softbody.links:
            p1 = (int(link.v1.x), int(link.v1.y))
            p2 = (int(link.v2.x), int(link.v2.y))
            if link.flag == LinkFlag.NONE:
                pygame.draw.line(surface, FRAME_INVISIBLE_LINK_COLOR, p1, p2)
            else:
                pygame.draw.line(surface, FRAME_LINK_COLOR, p1, p2)

        for vertex in self.softbody.vertices:
            surface.set_at((int(vertex.x), int(vertex.y)), FRAME_VERTEX_COLOR)

        return surface
    
    def update(self, tank_rect: pygame.Rect):
        self.update_ai()
        self.softbody.update(tank_rect)
    
    # Abstract method
    def update_ai(self):
        raise NotImplementedError()
    
    # Abstract method
    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        raise NotImplementedError()
    
    # Abstract method
    def bubble_spawn_chance(self) -> float | None:
        return None
