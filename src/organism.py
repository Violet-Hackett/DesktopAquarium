import pygame
from softbody import *
import random
from enum import Enum

FRAME_VERTEX_COLOR = pygame.Color(0, 255, 0)
FRAME_LINK_COLOR = pygame.Color(255, 0, 0, 175)
FRAME_INVISIBLE_LINK_COLOR = pygame.Color(70, 70, 70, 100)
FRAME_VELOCITY_COLOR = pygame.Color(0, 0, 255, 175)

class AIStatus(Enum):
    NONE = 0
    WANDERING = 1
    FLEEING = 2
    HIDING = 3
    IDLE = 4
    HUNTING = 5
    DIGESTING = 6

# Abstract class
class Organism:
    def __init__(self, softbody: Softbody, age: int = 0, ai_status: AIStatus = AIStatus.NONE, 
                 alive: bool = True):
        self.softbody = softbody
        self.age = age
        self.ai_status = ai_status
        self.alive = alive

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
    
    def update(self, tank, collision_links: list[Link] = [], collision_sculptures: list = []):
        if self.alive:
            self.update_ai(tank)
        self.softbody.update(collision_links, collision_sculptures, self.get_do_collision())
        self.age += 1
    
    # Abstract method
    def update_ai(self, tank):
        raise NotImplementedError()
    
    # Abstract method
    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        raise NotImplementedError()
    
    # Abstract method
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        raise NotImplementedError()
    
    # Abstract method
    def bubble_spawn_chance(self) -> float | None:
        return None

    def to_json(self) -> dict:
        softbody = self.softbody.to_json()
        return {'softbody': softbody, 'age': self.age, 'ai_status': self.ai_status.value,
                'alive': self.alive}
    
    # Abstract method
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        raise NotImplementedError()
    
    # Abstract method
    @staticmethod
    def get_do_collision() -> bool:
        raise NotImplementedError()