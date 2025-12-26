import pygame
from enum import Enum
import state
from runtime_resources import *

class VertexFlag(Enum):
    NONE = 0
    # Seaweed
    SEAWEED_BLADDER = 1
    SEAWEED_BLADE = 2
    # Goby
    GOBY_HEAD = 3
    GOBY_ABDOMEN = 4
    GOBY_TAILFIN = 5

class LinkFlag(Enum):
    NONE = 0
    # Seaweed
    SEAWEED_STIPE = 1
    # Goby
    GOBY_NECK = 2
    GOBY_TAIL = 3

GROUND_BOUNCE = 0.5
DRAG = 0.1
LINK_TENSION = 2.0
MOUSE_GRAB_RADIUS = 3
MOUSE_WATER_FORCE = 1

class Link:
    def __init__(self, v1, v2, length: float, tension: float = LINK_TENSION, flag: LinkFlag = LinkFlag.NONE):
        self.v1 = v1
        self.v2 = v2
        self.length = length
        self.tension = tension
        self.flag = flag

    def constrain_distance(self):
        dx = self.v2.x - self.v1.x
        dy = self.v2.y - self.v1.y
        distance = (dx**2 + dy**2)**(1/2)
        fraction = ((self.length - distance) / distance) / self.tension
        dx *= fraction
        dy *= fraction

        if self.v1.anchor:
            self.v2.x += dx*2
            self.v2.y += dy*2
        elif self.v2.anchor:
            self.v1.x -= dx*2
            self.v1.y -= dy*2
        else:
            self.v1.x -= dx
            self.v1.y -= dy
            self.v2.x += dx
            self.v2.y += dy

class Vertex:
    def __init__(self, x: float, y: float, density: float, 
                 links: list[Link], flag: VertexFlag = VertexFlag.NONE, anchor: bool = False):
        self.x = x
        self.y = y
        self.lx = x
        self.ly = y
        self.density = density
        self.links = links
        self.flag = flag
        self.anchor = anchor
    
    def get_dx(self):
        return (self.x - self.lx) * DRAG
    
    def get_dy(self):
        return (self.y - self.ly) * DRAG
    
    def get_speed(self):
        return (self.get_dx()**2 + self.get_dy()**2)**(1/2)
    
    def apply_water_force(self):
        vx, vy = get_mouse_velocity()
        mouse_distance = distance(get_relative_mouse_position(), (self.x, self.y))
        MWF = MOUSE_WATER_FORCE
        self.x += max(-MWF, min(MWF, vx * MWF / (mouse_distance**2 + .1)))
        self.y += max(-MWF, min(MWF, vy * MWF / (mouse_distance**2 + .1)))

    def update_independently(self):
        mouse_pressed = get_mouse_presses()[0]
        mouse_pos = get_relative_mouse_position()

        # Grab vertex if mouse is down and no vertex is grabbed
        if mouse_pressed and not state.vertex_grabbed:
            if distance((self.x, self.y), mouse_pos) < MOUSE_GRAB_RADIUS:
                state.vertex_grabbed = self

        # Snap grabbed vertex to mouse position
        if state.vertex_grabbed == self:
            if mouse_pressed:
                self.x, self.y = mouse_pos
            else:
                state.vertex_grabbed = None
        
        if self.anchor:
            return

        self.lx = self.x
        self.ly = self.y
        self.x += self.get_dx()
        self.y += self.get_dy()
        self.y += state.GRAVITY * self.density

        self.apply_water_force()

    def constrain_bounds(self, boundary: pygame.Rect):
        if self.anchor:
            return

        if(self.x < boundary.x):
            self.x = boundary.x
            self.lx = boundary.x - self.get_dx() * GROUND_BOUNCE
            self.ly += (self.get_dx() / self.get_speed()) * self.get_dy()
        elif(self.x > boundary.x + boundary.width):
            self.x = boundary.x + boundary.width
            self.lx = boundary.x + boundary.width + self.get_dx() * GROUND_BOUNCE
            self.ly += (self.get_dx() / self.get_speed()) * self.get_dy()
        if(self.y < boundary.y):
            self.y = boundary.y
            self.ly = boundary.y - self.get_dy() * GROUND_BOUNCE
            self.lx += (self.get_dy() / self.get_speed()) * self.get_dx()
        elif(self.y > boundary.y + boundary.height):
            self.y = boundary.y + boundary.height
            self.ly = boundary.y + boundary.height + self.get_dy() * GROUND_BOUNCE
            self.lx += (self.get_dy() / self.get_speed()) * self.get_dx()

class Softbody:
    def __init__(self, vertices: list[Vertex], links: list[Link]):
        self.vertices = vertices
        self.links = links

    def update(self, boundary: pygame.Rect):
        for vertex in self.vertices:
            vertex.update_independently()
            vertex.constrain_bounds(boundary)
        for link in self.links:
            link.constrain_distance()