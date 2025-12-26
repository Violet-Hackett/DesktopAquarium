import pygame
import organism
from runtime_resources import *
from graphics_resources import *
from enum import Enum
from effects import *
import random

class BufferKey(Enum):
    BACKGROUND = 0
    STATIC_ENVIORMENT = 1
    UI = 2

WATER_ALPHA = 120
TANK_BORDER_COLOR = (255, 255, 255, 50)
class Tank:
    def __init__(self, rect: pygame.Rect, organisms: list[organism.Organism]):
        self.rect = rect
        self.organisms = organisms
        self.buffers: dict[BufferKey, pygame.Surface] = {}
        self.buffer_update_flags: list[BufferKey] = []
        self.godrays: list[Godray] = []
        self.bubbles: list[Bubble] = []

    def check_buffer_update_status(self, buffer_key: BufferKey):
        is_in_buffers = buffer_key in self.buffers.keys()
        flagged_for_update = buffer_key in self.buffer_update_flags
        return (not is_in_buffers) or flagged_for_update

    def update(self):
        for organism_instance in self.organisms:
            organism_instance.update(self.rect)

    def render_background(self):
        if self.check_buffer_update_status(BufferKey.BACKGROUND):

            surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            background_image = pygame.image.load(state.TEXTURES_FP + "\\water_background.png")
            background_image = pygame.transform.scale_by(background_image, 1/state.SCALE)
            background_image.fill((255, 255, 255, WATER_ALPHA), None, pygame.BLEND_RGBA_MULT)
            background_offset = (-(background_image.get_width() - state.TANK_SIZE[0])/2,
                                 -(background_image.get_height() - state.TANK_SIZE[1])/2)
            surface.blit(background_image, background_offset)

            if BufferKey.UI in self.buffer_update_flags:
                self.buffer_update_flags.remove(BufferKey.UI)
            self.buffers[BufferKey.BACKGROUND] = surface
        return self.buffers[BufferKey.BACKGROUND]
    
    def render_godrays(self):
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        if state.frame_count % GODRAY_FREQUENCY == 0:
            self.godrays.append(Godray(random.random()/10, (biased_random_beta(strength=10)-0.5)*2))

        new_godrays = []
        for godray in self.godrays:
            if godray.age <= GODRAY_LIFESPAN:
                surface.blit(godray.render(), (0, 0))
                new_godrays.append(godray)
            godray.update()
                
        self.godrays = new_godrays
        surface = pygame.transform.box_blur(surface, GODRAY_BLUR)
        return surface

    def render_bubbles(self):
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        if state.frame_count % AMBIENT_BUBBLE_FREQUENCY == 0:
            self.bubbles.append(Bubble(random.random()*MAX_BUBBLE_SIZE + 0.1, 
                                       random.randint(0, state.TANK_SIZE[0]), 
                                       state.TANK_SIZE[1]+MAX_BUBBLE_SIZE))
        new_bubbles = []
        for bubble in self.bubbles:
            if bubble.y + bubble.radius > 0:
                bubble.render_onto(surface)
                new_bubbles.append(bubble)
            bubble.update()
                    
        self.bubbles = new_bubbles
        return surface
    
    def render_organisms(self, overlay_frame: bool = False) -> pygame.Surface:
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        # Render organisms
        for organism_instance in self.organisms:
            surface.blit(organism_instance.render(self.rect), (0, 0))

            # Overlay softbody frame if enabled
            if overlay_frame:
                surface.blit(organism_instance.render_frame(self.rect), (0, 0))

            # Spawn bubbles
            bubble_chance = organism_instance.bubble_spawn_chance()
            if bubble_chance and bubble_chance > random.random():
                self.bubbles.append(Bubble(1, *organism_instance.root_position()))

        return surface
    
    def render_ui(self) -> pygame.Surface:
        if self.check_buffer_update_status(BufferKey.UI):
            surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

            # Tank border
            border_position = (0, 0, state.TANK_SIZE[0], state.TANK_SIZE[1])
            pygame.draw.rect(surface, TANK_BORDER_COLOR, border_position, 1)

            self.buffers[BufferKey.UI] = surface
            if BufferKey.UI in self.buffer_update_flags:
                self.buffer_update_flags.remove(BufferKey.UI)
        return self.buffers[BufferKey.UI]
    
    def render(self, scale: float, overlay_frame: bool = False) -> pygame.Surface:
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # Render background
        surface.blit(self.render_background(), (0, 0))

        # Render organisms
        surface.blit(self.render_organisms(), (0, 0))

        # Render foreground effects
        surface.blit(self.render_bubbles(), (0, 0))
        surface.blit(self.render_godrays(), (0, 0))
        surface.blit(self.render_ui(), (0, 0))

        surface = pygame.transform.scale_by(surface, scale)
        return surface 