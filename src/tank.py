import pygame
import organism
from runtime_resources import *
from graphics_resources import *
from enum import Enum

class BufferKey(Enum):
    BACKGROUND = 0
    STATIC_ENVIORMENT = 1
    UI = 2

MOUSE_WATER_FORCE = 2
WATER_ALPHA = 120
class Tank:
    def __init__(self, rect: pygame.Rect, organisms: list[organism.Organism]):
        self.rect = rect
        self.organisms = organisms
        self.buffers: dict[BufferKey, pygame.Surface] = {}

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

    def pull_background(self):
        if BufferKey.BACKGROUND not in self.buffers.keys():
            surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            background_image = pygame.image.load(state.TEXTURES_FP + "\\water_background.png")
            background_image = pygame.transform.scale_by(background_image, 1/state.SCALE)
            background_image.fill((255, 255, 255, WATER_ALPHA), None, pygame.BLEND_RGBA_MULT)
            background_offset = (-(background_image.get_width() - state.TANK_SIZE[0])/2,
                                 -(background_image.get_height() - state.TANK_SIZE[1])/2)
            surface.blit(background_image, background_offset)
            self.buffers[BufferKey.BACKGROUND] = surface
        return self.buffers[BufferKey.BACKGROUND]

    
    def render(self, scale: float, render_procedural_texture: bool = True, 
               overlay_frame: bool = False) -> pygame.Surface:

        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # Render background effects
        surface.blit(self.pull_background(), (0, 0))

        # Render organisms
        for organism_instance in self.organisms:
            if render_procedural_texture:
                surface.blit(organism_instance.render(self.rect), (0, 0))
            if overlay_frame:
                surface.blit(organism_instance.render_frame(self.rect), (0, 0))

         # Render foreground effects

        surface = pygame.transform.scale_by(surface, scale)
        return surface 