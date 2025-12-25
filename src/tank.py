import pygame
import organism
from runtime_resources import *

WATER_COLOR = pygame.Color(22, 28, 44)
MOUSE_WATER_FORCE = 2
class Tank:
    def __init__(self, rect: pygame.Rect, organisms: list[organism.Organism]):
        self.rect = rect
        self.organisms = organisms

    def update(self):
        self.apply_mouse_water_forces()
        for organism_instance in self.organisms:
            organism_instance.update(self.rect)

    def apply_mouse_water_forces(self):
        vx, vy = pygame.mouse.get_rel()
        for organism_instance in self.organisms:
            for vertex in organism_instance.softbody.vertices:
                if vertex.anchored:
                    continue
                mouse_distance = distance(get_relative_mouse_position(), (vertex.x, vertex.y))
                MWF = MOUSE_WATER_FORCE
                vertex.x += max(-MWF, min(MWF, vx * MWF / mouse_distance**2))
                vertex.y += max(-MWF, min(MWF, vy * MWF / mouse_distance**2))
    
    def render(self, scale: float, render_procedural_texture: bool = True, 
               overlay_frame: bool = False) -> pygame.Surface:

        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # Render background
        surface.fill(WATER_COLOR)  

        # Render organisms
        for organism_instance in self.organisms:
            if render_procedural_texture:
                surface.blit(organism_instance.render(self.rect), (0, 0))
            if overlay_frame:
                surface.blit(organism_instance.render_frame(self.rect), (0, 0))

         # Render effects

        surface = pygame.transform.scale_by(surface, scale)
        return surface 