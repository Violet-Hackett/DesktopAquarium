import pygame
import organism
from resources import *
from graphics_resources import *
from effects import *
import random
from state import BufferKey
import win32api
from sculpture import Sculpture
from ui import *
from softbody import *
import json
from supported_organisms import SUPPORTED_ORGANISM_TYPES, SPAWNABLE_ORGANISM_TYPES

WATER_ALPHA = 80
BACKGROUND_BRIGHTNESS = 0.8
SCULPTURE_SIMPLIFY_RADIUS = 0.5
class Tank:
    def __init__(self, rect: pygame.Rect, organisms: list[organism.Organism], 
                 sculptures: list[Sculpture], filepath: str | None = None):
        self.rect = rect
        self.organisms = organisms
        self.buffers: dict[BufferKey, pygame.Surface] = {}
        self.godrays: list[Godray] = []
        self.bubbles: list[Bubble] = []
        self.paused = False
        self.ui: UI = UI()
        self.sculptures: list[Sculpture] = sculptures
        self.selected_sculpture: Sculpture | None = None
        self.filepath = filepath

        state.verify_tank_dimensions(self.rect.size)

    def check_buffer_update_status(self, buffer_key: BufferKey):
        is_in_buffers = buffer_key in self.buffers.keys()
        flagged_for_update = buffer_key in state.buffer_update_flags
        return (not is_in_buffers) or flagged_for_update
    
    def spawn_organism(self):
        mouse_pos = get_relative_mouse_position()
        spawn_pos = (mouse_pos[0] - 1e-6, mouse_pos[1])
        organism_type = SPAWNABLE_ORGANISM_TYPES[self.ui.spawn_selection]
        self.organisms.append(organism_type.generate_random(spawn_pos))

    def get_collision_sculptures(self) -> list[Sculpture]:
        sculptures = []
        for sculpture in self.sculptures:
            if not sculpture.is_background:
                sculptures.append(sculpture)
        return sculptures

    def get_collision_links(self) -> list[Link]:
        links = []
        for sculpture in self.get_collision_sculptures():
            links += sculpture.links
        return links

    def update(self):
        state.buffer_update_flags = []
        
        # Spawn selected organism if enter is pressed
        for event in get_events():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: 
                self.spawn_organism()

        collision_links = self.get_collision_links()
        collision_sculptures = self.get_collision_sculptures()
        for link in collision_links:
            link.compute_aabb()
        if not self.paused:
            for organism_instance in self.organisms:
                organism_instance.update(self, collision_links, collision_sculptures)
        self.ui.update()
    
    def render(self, scale: float, overlay_frame: bool = False) -> pygame.Surface:

        # Return what's in the buffer if the tank is paused
        if self.paused and BufferKey.RENDERED_FRAME in self.buffers.keys():
            return self.buffers[BufferKey.RENDERED_FRAME]

        ui_surface_rect = (self.rect.width, self.rect.height + state.UI_HEIGHT)
        surface = pygame.Surface(ui_surface_rect, pygame.SRCALPHA)

        # Render background sculptures
        surface.blit(self.render_background_sculptures(), (0, 0))

        # Render background
        surface.blit(self.render_background(), (0, 0))

        # Render organisms
        surface.blit(self.render_organisms(overlay_frame), (0, 0))

        # Render foreground effects
        surface.blit(self.render_bubbles(), (0, 0))
        surface.blit(self.render_godrays(), (0, 0))

        # Render background sculptures
        surface.blit(self.render_foreground_sculptures(overlay_frame), (0, 0))

        # Render UI
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
            background_offset = (-(background_image.get_width() - self.rect.width)/2,
                                 -(background_image.get_height() - self.rect.height)/2)
            surface.blit(background_image, background_offset)
            surface.fill((int(255*BACKGROUND_BRIGHTNESS),)*3, special_flags=pygame.BLEND_RGB_MULT)

            self.buffers[BufferKey.BACKGROUND] = surface
        return self.buffers[BufferKey.BACKGROUND]
    
    def render_background_sculptures(self):
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for sculpture in self.sculptures:
            if sculpture.is_background:
                surface.blit(sculpture.render(self.rect))
        return surface

    def render_foreground_sculptures(self, overlay_frame: bool = False):
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for sculpture in self.sculptures:
            if not sculpture.is_background:
                surface.blit(sculpture.render(self.rect, overlay_frame))
        return surface

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
                                       random.randint(0, self.rect.width), 
                                       self.rect.height+MAX_BUBBLE_SIZE))
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
            self.buffers[BufferKey.UI] = self.ui.render(self)
        return self.buffers[BufferKey.UI]
    
    def pause_tank(self):
        state.fps = 60
        self.paused = True

    def unpause_tank(self):
        state.fps = state.DEFAULT_FPS
        self.paused = False

    def new_sculpture(self):
        # Simplify the current sculpture if one exists
        if self.selected_sculpture:
            self.selected_sculpture.simplify(SCULPTURE_SIMPLIFY_RADIUS)


        # Create a new sculpture
        background = self.ui.sculpt_swich_state == SculptSwitchState.BACKGROUND
        new_sculpture = Sculpture([], background)
        self.selected_sculpture = new_sculpture
        self.sculptures.append(new_sculpture)

    def sculpt(self):

        # Return if swich is off
        if self.ui.sculpt_swich_state == SculptSwitchState.OFF:
            return

        # Create a new structure if none is selected
        if not self.selected_sculpture:
            self.new_sculpture()

        # Update sculpture SculptSwitchState 
        self.selected_sculpture.is_background = self.ui.sculpt_swich_state == SculptSwitchState.BACKGROUND # type: ignore

        self.selected_sculpture.add_vertex(Vertex(*get_relative_mouse_position(), 0, [], # type: ignore
                                                       VertexFlag.SCULPTURE)) 
    
    def drag_window(self):
        self.pause_tank()
        # Update window position to follow mouse
        mouse_pos = win32api.GetCursorPos()
        new_window_position = (state.WINDOW_POSITION[0] + mouse_pos[0] - state.last_win_mouse_position[0], 
                               state.WINDOW_POSITION[1] + mouse_pos[1] - state.last_win_mouse_position[1])
        state.WINDOW_POSITION = new_window_position
        state.last_win_mouse_position = mouse_pos
        pygame.display.set_window_position(new_window_position)

    def get_vertices(self) -> list[Vertex]:
        vertices = []
        for organism in self.organisms:
            vertices += organism.softbody.vertices
        for sculpture in self.sculptures:
            vertices += sculpture.vertices
        return vertices

    def save(self):
        tank_fp = prompt_for_save_tank(self.filepath)
        if tank_fp == '':
            return
        with open(tank_fp, "w") as tank_file:
            tank_file.write(self.to_json())

    def load(self):
        tank_fp = prompt_for_load_tank()
        if tank_fp == '':
            return
        with open(tank_fp) as tank_file:
            loaded_tank = Tank.from_json(json.load(tank_file))
            loaded_tank.filepath = tank_fp
            return loaded_tank

    def to_json(self) -> str:
        vertices = [dict(vertex.to_json(), **{'id': id(vertex)}) for vertex in self.get_vertices()]
        rect = (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        organisms = [organism.to_json() for organism in self.organisms]
        sculptures = [sculpture.to_json() for sculpture in self.sculptures]
        json_dict = {'vertices': vertices, 'rect': rect, 'organisms': organisms, 'sculptures': sculptures,
                     'filepath': self.filepath}
        return json.dumps(json_dict)

    @staticmethod
    def from_json(json_dict: dict):
        ids_to_vertices = dict([(vertex_json['id'], Vertex.from_json(vertex_json)) 
                           for vertex_json in json_dict['vertices']])
        rect = pygame.Rect(json_dict['rect'])
        organisms = [SUPPORTED_ORGANISM_TYPES[organism_json['type']].from_json(organism_json, ids_to_vertices)
                     for organism_json in json_dict['organisms']]
        sculptures = [Sculpture.from_json(sculpture_json, ids_to_vertices) 
                      for sculpture_json in json_dict['sculptures']]
        filepath = json_dict['filepath']
        
        links: list[Link] = []
        for organism in organisms:
            links += organism.softbody.links
        for sculpture in sculptures:
            links += sculpture.links
        for link in links:
            link.v1.links.append(link)

        return Tank(rect, organisms, sculptures, filepath)