import pygame
from softbody import *

SCULPTURE_COLOR = pygame.Color(0, 0, 0)
class Sculpture:
    def __init__(self, vertices: list[Vertex], is_background: bool, collision_enabled: bool):
        self.vertices = vertices
        self.is_background = is_background
        self.collision_enabled = collision_enabled

    def render(self, tank_rect: pygame.Rect):
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        points = list(map(Vertex.x_y, self.vertices))
        if len(points) == 0:
            surface.set_at(get_relative_mouse_position(), SCULPTURE_COLOR)
        elif len(points) == 1:
            surface.set_at(points[0], SCULPTURE_COLOR)
        elif len(points) == 2:
            pygame.draw.line(surface, SCULPTURE_COLOR, points[0], points[1])
        else:
            pygame.draw.polygon(surface, SCULPTURE_COLOR, points)

        return surface
    
    def to_json(self) -> dict:
        vertex_ids = list(map(id, self.vertices))
        return {'vertex_ids': vertex_ids, 'is_background': self.is_background, 
                'collision_enabled': self.collision_enabled}
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        vertices = [ids_to_vertices[vertex_id] for vertex_id in json_dict['vertex_ids']]
        return Sculpture(vertices, json_dict['is_background'], json_dict['collision_enabled'])