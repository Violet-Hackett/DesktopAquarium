import pygame
from enum import Enum
import state
from runtime_resources import *
import math

class VertexFlag(Enum):
    NONE = 0
    # Seaweed
    SEAWEED_BLADDER = 1
    SEAWEED_BLADE = 2
    # Goby
    GOBY_HEAD = 3
    GOBY_ABDOMEN = 4
    GOBY_TAILFIN = 5
    # Crab
    CRAB_BODY = 6
    CRAB_JOINT = 7
    CRAB_CLAWTIP = 8
    # Snail
    SNAIL_BODY = 9
    SNAIL_SHELL_CENTER = 10
    SNAIL_EYE = 11

class LinkFlag(Enum):
    NONE = 0
    # Seaweed
    SEAWEED_STIPE = 1
    # Goby
    GOBY_NECK = 2
    GOBY_TAIL = 3
    # Crab
    CRAB_SHELL = 4
    CRAB_LIMB = 5
    # Snail
    SNAIL_FLESH = 6
    SNAIL_SHELL = 7

GROUND_BOUNCE = 0.5
DRAG = 0.1
LINK_TENSION = 2.0
MOUSE_GRAB_RADIUS = 3
MOUSE_WATER_FORCE = 1
CONSTRAINT_ITERATIONS = 3

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
        distance = max((dx**2 + dy**2)**(1/2), 1e-6)
        fraction = ((self.length - distance) / distance) * self.tension
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

        self.v1.constrain_bounds()
        self.v2.constrain_bounds()

class Vertex:
    def __init__(self, x: float, y: float, density: float, links: list[Link], 
                 flag: VertexFlag = VertexFlag.NONE, anchor: bool = False, 
                 boundary: pygame.Rect = pygame.Rect(0, 0, *state.TANK_SIZE)):
        self.x = x
        self.y = y
        self.lx = x
        self.ly = y
        self.density = density
        self.links = links
        self.flag = flag
        self.anchor = anchor
        self.boundary = boundary
        self.gravity: tuple[float, float] = (0, state.GRAVITY)

    def x_y(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    def get_dx(self) -> float:
        return (self.x - self.lx) * DRAG
    
    def get_dy(self) -> float:
        return (self.y - self.ly) * DRAG
    
    def get_speed(self) -> float:
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

        gravity_force_x = self.gravity[0] * self.density
        gravity_force_y = self.gravity[1] * self.density
        self.x += gravity_force_x
        self.y += gravity_force_y

        self.apply_water_force()

    def constrain_bounds(self):
        if self.anchor:
            return

        if(self.x < self.boundary.x):
            self.x = self.boundary.x
            self.lx = self.boundary.x - self.get_dx() * GROUND_BOUNCE
        elif(self.x > self.boundary.x + self.boundary.width):
            self.x = self.boundary.x + self.boundary.width
            self.lx = self.boundary.x + self.boundary.width - self.get_dx() * GROUND_BOUNCE
        if(self.y < self.boundary.y):
            self.y = self.boundary.y
            self.ly = self.boundary.y - self.get_dy() * GROUND_BOUNCE
        elif(self.y > self.boundary.y + self.boundary.height):
            self.y = self.boundary.y + self.boundary.height
            self.ly = self.boundary.y + self.boundary.height - self.get_dy() * GROUND_BOUNCE

class AngleConstraint:
    def __init__(self, vertex_a, vertex_b, vertex_c, rest_angle: int, stiffness: float):
        self.a = vertex_a
        self.b = vertex_b
        self.c = vertex_c
        self.rest_angle = rest_angle
        self.stiffness = stiffness

    def apply(self):
        rest_angle_radians = math.radians(self.rest_angle)
        abx, aby = self.a.x - self.b.x, self.a.y - self.b.y
        cbx, cby = self.c.x - self.b.x, self.c.y - self.b.y

        dot = abx * cbx + aby * cby
        mag = (abx*abx + aby*aby)**0.5 * (cbx*cbx + cby*cby)**0.5
        if mag < 1e-6:
            return

        angle = math.acos(max(-1, min(1, dot / mag)))
        diff = angle - rest_angle_radians

        correction = diff * self.stiffness
        self.a.x -= cbx * correction
        self.a.y -= cby * correction
        self.c.x -= abx * correction
        self.c.y -= aby * correction

class Softbody:
    def __init__(self, vertices: list[Vertex], links: list[Link], angles: list[AngleConstraint] = []):
        self.vertices = vertices
        self.links = links
        self.angles = angles

    def update(self):
        for i in range(CONSTRAINT_ITERATIONS):
            for vertex in self.vertices:
                vertex.update_independently()
                vertex.constrain_bounds()
            for link in self.links:
                link.constrain_distance()
            for angle in self.angles:
                angle.apply()
