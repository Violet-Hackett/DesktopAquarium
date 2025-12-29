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
CONSTRAINT_ITERATIONS = 8
VERTEX_COLLISION_RADIUS = 2

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

    def compute_aabb(self):
        self.minx = min(self.v1.x, self.v2.x)
        self.maxx = max(self.v1.x, self.v2.x)
        self.miny = min(self.v1.y, self.v2.y)
        self.maxy = max(self.v1.y, self.v2.y)   

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
    
    def apply_mouse_grab_force(self):
        self.x , self.y = get_relative_mouse_position()
    
    def apply_water_force(self):
        vx, vy = get_mouse_velocity()
        mouse_distance = distance(get_relative_mouse_position(), (self.x, self.y))
        MWF = MOUSE_WATER_FORCE
        self.lx -= max(-MWF, min(MWF, vx * MWF / (mouse_distance**2 + .1))) * 10
        self.ly -= max(-MWF, min(MWF, vy * MWF / (mouse_distance**2 + .1))) * 10

    def update_independently(self, collision_sculptures: list = [], do_collision: bool = True):
        if self.anchor:
            return

        self.apply_water_force()

        vx = (self.x - self.lx) * DRAG + self.gravity[0] * self.density
        vy = (self.y - self.ly) * DRAG + self.gravity[1] * self.density

        self.lx = self.x
        self.ly = self.y

        if not do_collision or not Vertex.collides_with_any_sculptures(self.x + vx, self.y + vy, collision_sculptures):
            self.x += vx
            self.y += vy

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
        # Broad-phase AABB rejection
        if (self.x < link.minx - vertex_radius or self.x > link.maxx + vertex_radius or
            self.y < link.miny - vertex_radius or self.y > link.maxy + vertex_radius):
            return

        # Link endpoints
        link_start_x, link_start_y = link.v1.x, link.v1.y
        link_end_x,   link_end_y   = link.v2.x, link.v2.y

        # Current and previous vertex positions
        curr_x, curr_y = self.x,  self.y
        prev_x, prev_y = self.lx, self.ly

        # Link direction vector
        link_dx = link_end_x - link_start_x
        link_dy = link_end_y - link_start_y
        link_len_sq = link_dx * link_dx + link_dy * link_dy
        if link_len_sq == 0:
            return

        # Project current vertex position onto link segment
        to_curr_x = curr_x - link_start_x
        to_curr_y = curr_y - link_start_y
        t_closest = max(
            0.0,
            min(1.0, (to_curr_x * link_dx + to_curr_y * link_dy) / link_len_sq)
        )

        closest_x = link_start_x + link_dx * t_closest
        closest_y = link_start_y + link_dy * t_closest

        # Distance from vertex to link
        sep_x = curr_x - closest_x
        sep_y = curr_y - closest_y
        distance = (sep_x * sep_x + sep_y * sep_y) ** 0.5

        # Static overlap resolution
        if 0 < distance < vertex_radius:
            penetration = (vertex_radius - distance) / distance
            self.x += sep_x * penetration
            self.y += sep_y * penetration
            return

        # Vertex displacement over the timestep
        vel_x = curr_x - prev_x
        vel_y = curr_y - prev_y
        if vel_x == 0 and vel_y == 0:
            return

        # Link outward normal (unit length)
        inv_link_len = 1.0 / (link_len_sq ** 0.5)
        normal_x = -link_dy * inv_link_len
        normal_y =  link_dx * inv_link_len

        # Signed distances to link plane at previous and current positions
        prev_signed_dist = (
            (prev_x - link_start_x) * normal_x +
            (prev_y - link_start_y) * normal_y
        )
        curr_signed_dist = (
            (curr_x - link_start_x) * normal_x +
            (curr_y - link_start_y) * normal_y
        )

        r = vertex_radius

        # No crossing of the collision slab
        if (prev_signed_dist > r and curr_signed_dist > r) or \
        (prev_signed_dist < -r and curr_signed_dist < -r):
            return

        denom = prev_signed_dist - curr_signed_dist
        if denom == 0:
            return

        # Time of impact along the vertex path
        toi = (prev_signed_dist - r) / denom
        if toi < 0 or toi > 1:
            return

        # Contact point
        hit_x = prev_x + vel_x * toi
        hit_y = prev_y + vel_y * toi

        # Check if contact lies within the segment
        to_hit_x = hit_x - link_start_x
        to_hit_y = hit_y - link_start_y
        proj = (to_hit_x * link_dx + to_hit_y * link_dy) / link_len_sq
        if proj < 0 or proj > 1:
            return

        # Resolve to non-penetrating position
        self.x = hit_x + normal_x * r
        self.y = hit_y + normal_y * r

    @staticmethod
    def collides_with_any_sculptures(px: float, py: float, collision_sculptures: list) -> bool:
        for sculpture in collision_sculptures:
            if Vertex.collides_with_sculpture(px, py, sculpture):
                return True
        return False

    @staticmethod
    def collides_with_sculpture(px: float, py: float, sculpture) -> bool:
        polygon = sculpture.vertices
        inside = False

        n = len(polygon)
        if n < 3:
            return False

        for i in range(n):
            v1 = polygon[i]
            v2 = polygon[(i + 1) % n]

            x1, y1 = v1.x, v1.y
            x2, y2 = v2.x, v2.y

            intersects = ((y1 > py) != (y2 > py))
            if intersects:
                t = (py - y1) / (y2 - y1)
                x_intersect = x1 + t * (x2 - x1)
                if x_intersect > px:
                    inside = not inside

        return inside

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

    def update(self, collision_links: list[Link] = [], collision_sculptures: list = [], 
               do_collision: bool = True):
        # Integrate motion
        for vertex in self.vertices:
            vertex.update_independently(collision_sculptures, do_collision)
    
            # Assign and apply mouse grab forces to the grabbed vertex
            if get_mouse_presses()[0]:
                if not state.vertex_grabbed and distance(vertex.x_y(), get_relative_mouse_position()) < MOUSE_GRAB_RADIUS:
                    state.vertex_grabbed = vertex
                if vertex == state.vertex_grabbed:
                    vertex.apply_mouse_grab_force()
            else:
                state.vertex_grabbed = None

        # Solve constraints + collisions together
        for _ in range(CONSTRAINT_ITERATIONS):
            for link in self.links:
                link.constrain_distance()

            for vertex in self.vertices:
                vertex.constrain_tank_bounds()

        if do_collision:
            for _ in range(2):
                for vertex in self.vertices:
                    for static_link in collision_links:
                        vertex.constrain_distance_to_static_link(static_link)


    def to_json(self) -> dict:
        vertex_ids = list(map(id, self.vertices))
        links = [link.to_json() for link in self.links]
        return {'vertex_ids': vertex_ids, 'links': links}
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        vertices = [ids_to_vertices[vertex_id] for vertex_id in json_dict['vertex_ids']]
        links = [Link.from_json(link_json, ids_to_vertices) for link_json in json_dict['links']]
        return Softbody(vertices, links)