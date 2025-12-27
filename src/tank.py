import pygame
import organism
from resources import *
from graphics_resources import *
from enum import Enum
from effects import *
import random
import subprocess
from types import MethodType
from state import BufferKey
import win32api

WATER_ALPHA = 120
TANK_BORDER_COLOR = (255, 255, 255, 50)
UI_BASE_COLOR = (17, 17, 17)
UI_HIGHLIGHT_COLOR = (30, 30, 30)
UI_SHADOW_COLOR = (0, 0, 0)
UI_INSET_COLOR = (10, 10, 10)
class Tank:
    def __init__(self, rect: pygame.Rect, organisms: list[organism.Organism]):
        self.rect = rect
        self.organisms = organisms
        self.buffers: dict[BufferKey, pygame.Surface] = {}
        self.godrays: list[Godray] = []
        self.bubbles: list[Bubble] = []
        self.ui_elements: dict[UIElementKey, UIElement] = {}
        self.paused = False

    def check_buffer_update_status(self, buffer_key: BufferKey):
        is_in_buffers = buffer_key in self.buffers.keys()
        flagged_for_update = buffer_key in state.buffer_update_flags
        return (not is_in_buffers) or flagged_for_update

    def update(self):
        if not self.paused:
            for organism_instance in self.organisms:
                organism_instance.update()
        self.update_ui()
        state.buffer_update_flags = []
    
    def render(self, scale: float, overlay_frame: bool = False) -> pygame.Surface:

        # Return what's in the buffer if the tank is paused
        if self.paused and BufferKey.RENDERED_FRAME in self.buffers.keys():
            return self.buffers[BufferKey.RENDERED_FRAME]

        ui_surface_rect = (state.TANK_SIZE[0], state.TANK_SIZE[1] + state.UI_HEIGHT)
        surface = pygame.Surface(ui_surface_rect, pygame.SRCALPHA)

        # Render background
        surface.blit(self.render_background(), (0, 0))

        # Render organisms
        surface.blit(self.render_organisms(overlay_frame), (0, 0))

        # Render foreground effects
        surface.blit(self.render_bubbles(), (0, 0))
        surface.blit(self.render_godrays(), (0, 0))
        surface.blit(self.render_ui(), (0, 0))

        surface = pygame.transform.scale_by(surface, scale)
        self.buffers[BufferKey.RENDERED_FRAME] = surface
        return surface 
    
    def render_background(self):
        if self.check_buffer_update_status(BufferKey.BACKGROUND):

            surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            background_image = pygame.image.load(state.TEXTURES_FP + "\\water_background.png")
            background_image = pygame.transform.scale_by(background_image, 1/state.SCALE)
            background_image.fill((255, 255, 255, WATER_ALPHA), None, pygame.BLEND_RGBA_MULT)
            background_offset = (-(background_image.get_width() - state.TANK_SIZE[0])/2,
                                 -(background_image.get_height() - state.TANK_SIZE[1])/2)
            surface.blit(background_image, background_offset)

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
            ui_surface_rect = (state.TANK_SIZE[0], state.TANK_SIZE[1] + state.UI_HEIGHT)
            surface = pygame.Surface(ui_surface_rect, pygame.SRCALPHA)

            # Tank border
            tank_border_rect= (0, 0, state.TANK_SIZE[0], state.TANK_SIZE[1] + 1)
            pygame.draw.rect(surface, TANK_BORDER_COLOR, tank_border_rect, 1)

            # UI Base and border
            ui_base_rect = (0, state.TANK_SIZE[1], state.TANK_SIZE[0], state.UI_HEIGHT)
            pygame.draw.rect(surface, UI_BASE_COLOR, ui_base_rect)
            pygame.draw.rect(surface, UI_SHADOW_COLOR, ui_base_rect, 1)
            pygame.draw.line(surface, UI_HIGHLIGHT_COLOR, (0, state.TANK_SIZE[1]), state.TANK_SIZE)

            # UI Grip
            ui_grip_width = max(23, min(111, state.TANK_SIZE[0] / 2)) # Clamp grip width to [23-111]
            ui_grip_rect = pygame.Rect(state.TANK_SIZE[0]/2 - ui_grip_width/2, state.TANK_SIZE[1] + 2,
                            ui_grip_width, 7)
            self.ui_grip_rect = ui_grip_rect
            pygame.draw.rect(surface, UI_INSET_COLOR, ui_grip_rect, border_radius=2)
            pygame.draw.rect(surface, UI_SHADOW_COLOR, ui_grip_rect, border_radius=2, width=1)
            pygame.draw.line(surface, UI_HIGHLIGHT_COLOR, (ui_grip_rect.x+1, ui_grip_rect.bottom-1),
                             (ui_grip_rect.right-2, ui_grip_rect.bottom-1))
            carry_label = pygame.image.load(state.TEXTURES_FP + "\\carry_label.png").convert_alpha()
            carry_label.fill(UI_BASE_COLOR, special_flags=pygame.BLEND_RGB_ADD)
            carry_label_position = (state.TANK_SIZE[0]/2 - carry_label.width/2, state.TANK_SIZE[1] + 3)
            surface.blit(carry_label, carry_label_position)

            # Add the UI grip as an active UI element
            self.ui_elements[UIElementKey.GRIP] = UIElement(ui_grip_rect, self.drag_window, release_function=self.unpause_tank)

            self.buffers[BufferKey.UI] = surface

        return self.buffers[BufferKey.UI]
    
    def pause_tank(self):
        state.fps = 60
        self.paused = True

    def unpause_tank(self):
        state.fps = state.DEFAULT_FPS
        self.paused = False
    
    def drag_window(self):
        self.pause_tank()
        # Update window position to follow mouse
        mouse_pos = win32api.GetCursorPos()
        new_window_position = (state.WINDOW_POSITION[0] + mouse_pos[0] - state.last_win_mouse_position[0], 
                               state.WINDOW_POSITION[1] + mouse_pos[1] - state.last_win_mouse_position[1])
        state.WINDOW_POSITION = new_window_position
        state.last_win_mouse_position = mouse_pos
        pygame.display.set_window_position(new_window_position)

    def update_ui(self):
        mouse_pressed = get_mouse_presses()[0]
        for ui_element in self.ui_elements.values():
            ui_element.apply(mouse_pressed)

        
class UIElementKey(Enum):
    GRIP = 0

class UIElement:
    def __init__(self, hitbox: pygame.Rect, function_reference: MethodType, is_button: bool = False, 
                 flags_ui_update: bool = False, release_function: MethodType | None = None):
        self.hitbox = hitbox
        self.function_reference = function_reference
        self.is_button = is_button
        self.flags_ui_update = flags_ui_update
        self.last_frame_pressed = 0
        self.release_function = release_function
    
    def apply(self, mouse_pressed: bool):
        return_value = None
        colliding = self.mouse_collision()

        # Apply the release function if it exists and 2 frames have elapsed since activated
        if self.release_function and state.frame_count == self.last_frame_pressed + 2:
                return_value = self.release_function.__call__()

        if mouse_pressed and colliding:
            if self.is_button:
                # Check to see if more than one frame as elapsed since the button was being pressed
                if state.frame_count > self.last_frame_pressed + 1:
                    return_value = self.function_reference.__call__()
            else:
                return_value = self.function_reference.__call__()

            # Schedule UI to be updated if the UI Element specifies to do so
            if self.flags_ui_update:
                state.buffer_update_flags.append(BufferKey.UI)

            self.last_frame_pressed = state.frame_count

        return return_value
    
    def mouse_collision(self):
        return self.hitbox.collidepoint(get_relative_mouse_position())