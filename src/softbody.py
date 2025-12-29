import pygame
from enum import Enum
import state
from resources import *
from pygame import Vector2

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
    # Egg
    EGG = 12
    # KelpWorm
    KELPWORM_HEAD = 13
    KELPWORM_BODY = 14
    # Sculpture
    SCULPTURE = 15

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
    # KelpWorm
    KELPWORM_NECK = 8
    KELPWORM_BODY = 9
    # Sculpture
    SCULPTURE = 10

BOUNCE_FORCE = 0.5
DRAG = 0.1
LINK_TENSION = 2.0
MOUSE_GRAB_RADIUS = 3
MOUSE_WATER_FORCE = 1
CONSTRAINT_ITERATIONS = 3
VERTEX_COLLISION_RADIUS = 3

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

        self.v1.constrain_tank_bounds()
        self.v2.constrain_tank_bounds()     

    def to_json(self):
        return {'v1_id': id(self.v1), 'v2_id': id(self.v2), 'length': self.length, 
                'tension': self.tension, 'flag': self.flag.value}
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        v1 = ids_to_vertices[json_dict['v1_id']]
        v2 = ids_to_vertices[json_dict['v2_id']]
        return Link(v1, v2, json_dict['length'], json_dict['tension'], LinkFlag(json_dict['flag']))

class Vertex:
    def __init__(self, x: float, y: float, density: float, links: list[Link], 
                 flag: VertexFlag = VertexFlag.NONE, anchor: bool = False, 
                 boundary: pygame.Rect | None = None, gravity: tuple[float, float] = (0, state.GRAVITY)):
        self.x = x
        self.y = y
        self.lx = x
        self.ly = y
        self.density = density
        self.links = links
        self.flag = flag
        self.anchor = anchor
        self.gravity = gravity
        if not boundary:
            self.boundary = pygame.Rect(0, 0, *state.tank_size())
        else:
            self.boundary = boundary

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

    def constrain_tank_bounds(self):
        if self.anchor:
            return

        if(self.x < self.boundary.x):
            self.x = self.boundary.x
            self.lx = self.boundary.x - self.get_dx() * BOUNCE_FORCE
        elif(self.x > self.boundary.x + self.boundary.width):
            self.x = self.boundary.x + self.boundary.width
            self.lx = self.boundary.x + self.boundary.width - self.get_dx() * BOUNCE_FORCE
        if(self.y < self.boundary.y):
            self.y = self.boundary.y
            self.ly = self.boundary.y - self.get_dy() * BOUNCE_FORCE
        elif(self.y > self.boundary.y + self.boundary.height):
            self.y = self.boundary.y + self.boundary.height
            self.ly = self.boundary.y + self.boundary.height - self.get_dy() * BOUNCE_FORCE

    def constrain_distance_to_static_link(self, link, vertex_radius: float = VERTEX_COLLISION_RADIUS):

        # Link endpoints
        Ax, Ay = link.v1.x, link.v1.y
        Bx, By = link.v2.x, link.v2.y

        # Vertex position
        Px, Py = self.x, self.y

        # Vector along the link
        ABx = Bx - Ax
        ABy = By - Ay
        ab_len_sq = ABx*ABx + ABy*ABy

        # Degenerate link (zero-length)
        if ab_len_sq == 0:
            return

        # Vector from link start to vertex
        APx = Px - Ax
        APy = Py - Ay

        # Projection factor (clamped to segment)
        t = max(0.0, min(1.0, (APx*ABx + APy*ABy) / ab_len_sq))

        # Closest point on segment
        Cx = Ax + ABx * t
        Cy = Ay + ABy * t

        # Vector from closest point to vertex
        dx = Px - Cx
        dy = Py - Cy
        dist = (dx*dx + dy*dy) ** 0.5

        # If inside collision radius, push out
        if dist < vertex_radius and dist > 0:
            # Normalized direction
            nx = dx / dist
            ny = dy / dist

            # Push vertex to satisfy constraint
            push_dist = vertex_radius - dist
            self.x += nx * push_dist
            self.y += ny * push_dist

        # Handle exact overlap (dist == 0) by pushing along arbitrary perpendicular
        elif dist == 0:
            # Link vector perpendicular
            nx = -ABy
            ny = ABx
            len_n = (nx*nx + ny*ny) ** 0.5
            if len_n > 0:
                nx /= len_n
                ny /= len_n
                self.x += nx * vertex_radius
                self.y += ny * vertex_radius

    def to_json(self) -> dict:
        if self.boundary:
            boundary = (self.boundary.x, self.boundary.y,
                        self.boundary.width, self.boundary.height)
        else:
            boundary = None
        return {'x': self.x, 'y': self.y, 'density': self.density, 'flag': self.flag.value, 
                'anchor': self.anchor, 'gravity': self.gravity, 'boundary': boundary}
    
    @staticmethod
    def from_json(json_dict: dict):
        if json_dict['boundary']:
            boundary = pygame.Rect(json_dict['boundary'])
        else:
            boundary = None
        return Vertex(json_dict['x'], json_dict['y'], json_dict['density'], [], VertexFlag(json_dict['flag']),
                      json_dict['anchor'], boundary, json_dict['gravity'])

class Softbody:
    def __init__(self, vertices: list[Vertex], links: list[Link]):
        self.vertices = vertices
        self.links = links

    def update(self, collision_links: list[Link] = []):
        for vertex in self.vertices:
            vertex.update_independently()

        for _ in range(CONSTRAINT_ITERATIONS):
            for link in self.links:
                link.constrain_distance()
            for vertex in self.vertices:
                vertex.constrain_tank_bounds()
                # for link in collision_links:
                #     vertex.constrain_distance_to_static_link(link)

    def to_json(self) -> dict:
        vertex_ids = list(map(id, self.vertices))
        links = [link.to_json() for link in self.links]
        return {'vertex_ids': vertex_ids, 'links': links}
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        vertices = [ids_to_vertices[vertex_id] for vertex_id in json_dict['vertex_ids']]
        links = [Link.from_json(link_json, ids_to_vertices) for link_json in json_dict['links']]
        return Softbody(vertices, links)