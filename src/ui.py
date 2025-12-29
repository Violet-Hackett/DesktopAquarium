import pygame
import state
from enum import Enum
from types import MethodType, FunctionType
from resources import *

class SculptSwitchState(Enum):
    OFF = 0
    FOREGROUND = 1
    BACKGROUND = 2

TANK_BORDER_COLOR = (255, 255, 255, 50)
UI_BASE_COLOR = (17, 17, 17)
UI_HIGHLIGHT_COLOR = (30, 30, 30)
UI_SHADOW_COLOR = (0, 0, 0)
UI_INSET_COLOR = (10, 10, 10)
class UI:
    def __init__(self):
        self.sculpt_swich_state: SculptSwitchState = SculptSwitchState.OFF
        self.elements: dict[UIElementKey, UIElement] = {}

    def render(self, tank) -> pygame.Surface:
        ui_surface_rect = (state.tank_width(), state.tank_height() + state.UI_HEIGHT)
        surface = pygame.Surface(ui_surface_rect, pygame.SRCALPHA)

        # Tank border

        tank_border_rect= (0, 0, state.tank_width(), state.tank_height() + 1)
        pygame.draw.rect(surface, TANK_BORDER_COLOR, tank_border_rect, 1)

        # UI Base and border

        ui_base_rect = (0, state.tank_height(), state.tank_width(), state.UI_HEIGHT)
        pygame.draw.rect(surface, UI_BASE_COLOR, ui_base_rect)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, ui_base_rect, 1)
        pygame.draw.line(surface, UI_HIGHLIGHT_COLOR, (0, state.tank_height()), state.tank_size())

        # Sculpt label

        sculpt_swich_y = state.tank_height() + 2
        sculpt_label = load_label_texture('sculpt_label', UI_HIGHLIGHT_COLOR)
        surface.blit(sculpt_label, (4, sculpt_swich_y+2))

        sculpt_mode_label = load_label_texture(f"{self.sculpt_swich_state.name.lower()}_label",
                                               UI_HIGHLIGHT_COLOR)
        surface.blit(sculpt_mode_label, (6 + sculpt_label.width, sculpt_swich_y + 2))

        # New sculpture button

        new_sculpture_x = 18 + sculpt_label.width
        new_sculpture_rect = pygame.Rect(new_sculpture_x, sculpt_swich_y, 7, 7)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, new_sculpture_rect, border_radius=2, width=1)
        plus_label = load_label_texture('plus_label', UI_HIGHLIGHT_COLOR)
        surface.blit(plus_label, (new_sculpture_x+1, sculpt_swich_y+1))
        self.elements[UIElementKey.NEW_SCULPTURE] = UIElement(new_sculpture_rect, tank.new_sculpture, 
                                                             is_button=True)

        # Sculpt mode swich

        sculpt_swich_x = 3 + new_sculpture_rect.right
        thumb_width = 5
        sculpt_swich_rect = pygame.Rect(sculpt_swich_x, sculpt_swich_y, 17, 7)
        pygame.draw.rect(surface, UI_INSET_COLOR, sculpt_swich_rect, border_radius=3)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, sculpt_swich_rect, border_radius=3, width=1)
        # Draw highlight line <---

        sculpt_off_rect = pygame.Rect(sculpt_swich_x + 1, sculpt_swich_y+1, 
                                      thumb_width, thumb_width)
        sculpt_fg_rect = pygame.Rect(sculpt_swich_x + 1 + thumb_width, sculpt_swich_y+1, 
                                     thumb_width, thumb_width)
        sculpt_bg_rect = pygame.Rect(sculpt_swich_x + 1 + thumb_width*2, sculpt_swich_y+1, 
                                     thumb_width, thumb_width)
        if self.sculpt_swich_state == SculptSwitchState.OFF:
            sculpt_thumb_rect = sculpt_off_rect
        elif self.sculpt_swich_state == SculptSwitchState.FOREGROUND:
            sculpt_thumb_rect = sculpt_fg_rect
        else:
            sculpt_thumb_rect = sculpt_bg_rect
        surface.set_at((sculpt_swich_x + 3, sculpt_swich_y+3), UI_HIGHLIGHT_COLOR)
        surface.set_at((sculpt_swich_x + 3 + thumb_width, sculpt_swich_y+3), UI_HIGHLIGHT_COLOR)
        surface.set_at((sculpt_swich_x + 3 + thumb_width*2, sculpt_swich_y+3), UI_HIGHLIGHT_COLOR)
        pygame.draw.rect(surface, UI_BASE_COLOR, sculpt_thumb_rect, border_radius=2)
        pygame.draw.rect(surface, UI_HIGHLIGHT_COLOR, sculpt_thumb_rect, border_radius=2, width=1)
        
        self.elements[UIElementKey.SCULPT_MODE_OFF] = UIElement(sculpt_off_rect, self.set_sculpt_mode_off, 
                                                             is_button=True)
        self.elements[UIElementKey.SCULPT_MODE_FG] = UIElement(sculpt_fg_rect, self.set_sculpt_mode_fg, 
                                                             is_button=True)
        self.elements[UIElementKey.SCULPT_MODE_BG] = UIElement(sculpt_bg_rect, self.set_sculpt_mode_bg, 
                                                             is_button=True)
        
        # UI Grip

        ui_grip_width = state.tank_width() - 140
        ui_grip_rect = pygame.Rect(sculpt_swich_rect.right + 3, state.tank_height() + 2,
                        ui_grip_width, 7)
        self.ui_grip_rect = ui_grip_rect
        pygame.draw.rect(surface, UI_INSET_COLOR, ui_grip_rect, border_radius=2)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, ui_grip_rect, border_radius=2, width=1)
        pygame.draw.line(surface, UI_HIGHLIGHT_COLOR, (ui_grip_rect.x+1, ui_grip_rect.bottom-1),
                            (ui_grip_rect.right-2, ui_grip_rect.bottom-1))
        carry_label = load_label_texture('carry_label', UI_HIGHLIGHT_COLOR)
        carry_label_position = (state.tank_width()/2 - carry_label.width/2-1, state.tank_height() + 3)
        surface.blit(carry_label, carry_label_position)
        self.elements[UIElementKey.GRIP] = UIElement(ui_grip_rect, tank.drag_window, 
                                                     release_function=tank.unpause_tank, 
                                                     flags_ui_update=False)
        
        # Save button
        save_button_rect = pygame.Rect(ui_grip_rect.right+3, sculpt_swich_y, 20, 7)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, save_button_rect, border_radius=2, width=1)
        save_label = load_label_texture('save_label', UI_HIGHLIGHT_COLOR)
        surface.blit(save_label, (save_button_rect.left+3, save_button_rect.top+2))
        self.elements[UIElementKey.SAVE_BUTTON] = UIElement(save_button_rect, tank.save, 
                                                             is_button=True)

        # Load button
        load_button_rect = pygame.Rect(save_button_rect.right+2, sculpt_swich_y, 20, 7)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, load_button_rect, border_radius=2, width=1)
        load_label = load_label_texture('load_label', UI_HIGHLIGHT_COLOR)
        surface.blit(load_label, (load_button_rect.left+3, load_button_rect.top+2))
        self.elements[UIElementKey.LOAD_BUTTON] = UIElement(load_button_rect, state.load_tank, 
                                                             is_button=True)
        
        # New tank button
        new_tank_button_rect = pygame.Rect(load_button_rect.right+2, sculpt_swich_y, 20, 7)
        pygame.draw.rect(surface, UI_SHADOW_COLOR, new_tank_button_rect, border_radius=2, width=1)
        new_tank_label = load_label_texture('new_label', UI_HIGHLIGHT_COLOR)
        surface.blit(new_tank_label, (new_tank_button_rect.left+3, new_tank_button_rect.top+2))
        self.elements[UIElementKey.NEW_TANK_BUTTON] = UIElement(new_tank_button_rect, state.unassign_selected_tank, 
                                                             is_button=True)
        
        # Tank interactive surface (for sculpting)
        self.elements[UIElementKey.TANK] = UIElement(pygame.Rect(0, 0, *state.tank_size()), tank.sculpt, 
                                                     is_button=True)

        return surface
    
    def set_sculpt_mode_off(self):
        self.sculpt_swich_state = SculptSwitchState.OFF
        state.buffer_update_flags.append(state.BufferKey.UI)

    def set_sculpt_mode_fg(self):
        self.sculpt_swich_state = SculptSwitchState.FOREGROUND
        state.buffer_update_flags.append(state.BufferKey.UI)

    def set_sculpt_mode_bg(self):
        self.sculpt_swich_state = SculptSwitchState.BACKGROUND
        state.buffer_update_flags.append(state.BufferKey.UI)
    
    def update(self):
        mouse_pressed = get_mouse_presses()[0]
        for ui_element in self.elements.values():
            ui_element.apply(mouse_pressed)

class UIElementKey(Enum):
    GRIP = 0
    TANK = 1
    SCULPT_MODE_OFF = 2
    SCULPT_MODE_FG = 3
    SCULPT_MODE_BG = 4
    NEW_SCULPTURE = 5
    SAVE_BUTTON = 6
    LOAD_BUTTON = 7
    NEW_TANK_BUTTON = 8

class UIElement:
    def __init__(self, hitbox: pygame.Rect, function_reference: MethodType | FunctionType, is_button: bool = False, 
                 flags_ui_update: bool = True, release_function: MethodType | FunctionType | None = None):
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
                state.buffer_update_flags.append(state.BufferKey.UI)

            self.last_frame_pressed = state.frame_count

        return return_value
    
    def mouse_collision(self):
        return self.hitbox.collidepoint(get_relative_mouse_position())
    