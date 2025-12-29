import pygame
from softbody import *

SCULPTURE_COLOR = pygame.Color(0, 0, 0)
class Sculpture:
    def __init__(self, vertices: list[Vertex], is_background: bool):
        self.vertices = vertices
        self.links: list[Link] = []
        self.generate_links()
        self.is_background = is_background

    def add_vertex(self, vertex: Vertex):
        self.vertices.append(vertex)
        self.generate_links()
                
    def generate_links(self):
        self.links = []
        for i, vertex in enumerate(self.vertices):
            if i != len(self.vertices)-1:
                self.links.append(Link(vertex, self.vertices[i+1], 
                                       distance(vertex.x_y(), self.vertices[i+1].x_y())))
            else:
                self.links.append(Link(vertex, self.vertices[0], 
                                       distance(vertex.x_y(), self.vertices[0].x_y())))

    def render(self, tank_rect: pygame.Rect):
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        points = list(map(Vertex.x_y, self.vertices))
        if len(points) == 0:
            pygame.draw.circle(surface, SCULPTURE_COLOR, get_relative_mouse_position(), VERTEX_COLLISION_RADIUS-1)
        elif len(points) == 1:
            pygame.draw.circle(surface, SCULPTURE_COLOR, points[0], VERTEX_COLLISION_RADIUS-1)
        elif len(points) == 2:
            pygame.draw.line(surface, SCULPTURE_COLOR, points[0], points[1], VERTEX_COLLISION_RADIUS*2-1)
        else:
            pygame.draw.polygon(surface, SCULPTURE_COLOR, points)
            pygame.draw.polygon(surface, SCULPTURE_COLOR, points, VERTEX_COLLISION_RADIUS*2-1)

        return surface
    
    def has_neighbors(self, vertex: Vertex, radius: float) -> bool:
        for neighbor in self.vertices:
            if neighbor != vertex and distance(vertex.x_y(), neighbor.x_y()) < radius:
                return True
        return False
    
    def simplify(self, simplify_radius: float):
        for vertex in self.vertices:
            if self.has_neighbors(vertex, simplify_radius):
                self.vertices.remove(vertex)
    
    def to_json(self) -> dict:
        vertex_ids = list(map(id, self.vertices))
        return {'vertex_ids': vertex_ids, 'is_background': self.is_background}
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        vertices = [ids_to_vertices[vertex_id] for vertex_id in json_dict['vertex_ids']]
        return Sculpture(vertices, json_dict['is_background'])