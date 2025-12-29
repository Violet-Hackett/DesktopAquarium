import pygame
from organism import *
from softbody import *

CRAB_BUBBLE_SPAWN_CHANCE = 0.05
DEFAULT_CRAB_SIZE = 15
SHELL_HARDNESS = 0.8
LIMB_HARDNESS = 0.6
MUSCLE_HARDNESS = 0.3
ANTI_GROUND_FORCE = 1.5
class Crab(Organism):
    def __init__(self, softbody: Softbody, size: float):
        super().__init__(softbody)
        self.size = size

    def render_limb_onto(self, limb: Link, surface: pygame.Surface):
        pygame.draw.line(surface, BLACK, (limb.v1.x, limb.v1.y), 
                         (limb.v2.x, limb.v2.y), max(1, int(self.size / 6)))
        
    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)
        body_top_left, body_top_right, body_bottom_left, body_bottom_right = self.softbody.vertices[:4]
        arm_left, arm_right, clawtip_left, clawtip_right = self.softbody.vertices[-4:]
        limbs = self.softbody.links[4:-4]

        # Main body
        pygame.draw.polygon(surface, BLACK, [
            (body_top_left.x, body_top_left.y),
            (body_top_right.x, body_top_right.y),
            (body_bottom_right.x, body_bottom_right.y),
            (body_bottom_left.x, body_bottom_left.y),
        ])

        # Limbs
        for limb in limbs:
            self.render_limb_onto(limb, surface)

        # Claws
        
        return surface

    def update_ai(self, tank):
        pass

    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        root_x, root_y = root_position
        size = DEFAULT_CRAB_SIZE + random.randint(-5, 5)

        # Body nodes
        body_top_left = Vertex(root_x - size/2, root_y, 0.5, [], VertexFlag.CRAB_BODY)
        body_top_right = Vertex(root_x + size/2, root_y, 0.5, [], VertexFlag.CRAB_BODY)
        body_bottom_left = Vertex(root_x - size/2, root_y + size/2, 0.5, [], VertexFlag.CRAB_BODY)
        body_bottom_right = Vertex(root_x + size/2, root_y + size/2, 0.5, [], VertexFlag.CRAB_BODY)

        # Leg nodes
        knee_left = Vertex(root_x - size, root_y + size/2, 0.5, [], VertexFlag.CRAB_JOINT)
        knee_right = Vertex(root_x + size, root_y + size/2, 0.5, [], VertexFlag.CRAB_JOINT)
        foot_left = Vertex(root_x - size, root_y + size, 0.5, [], VertexFlag.CRAB_JOINT)
        foot_right = Vertex(root_x + size, root_y + size, 0.5, [], VertexFlag.CRAB_JOINT)

        # Arm nodes
        wrist_left = Vertex(root_x - size*2/3, root_y + size/2, 0.5, [], VertexFlag.CRAB_JOINT)
        wrist_right = Vertex(root_x + size*2/3, root_y + size/2, 0.5, [], VertexFlag.CRAB_JOINT)
        clawtip_left = Vertex(root_x - size/2, root_y + size, 0.5, [], VertexFlag.CRAB_CLAWTIP)
        clawtip_right = Vertex(root_x + size/2, root_y + size, 0.5, [], VertexFlag.CRAB_CLAWTIP)

        # Body links
        shell_top = Link(body_top_left, body_top_right, size/1.5, SHELL_HARDNESS, flag=LinkFlag.CRAB_SHELL)
        shell_left = Link(body_top_left, body_bottom_left, size/2, SHELL_HARDNESS, flag=LinkFlag.CRAB_SHELL)
        shell_right = Link(body_top_right, body_bottom_right, size/2, SHELL_HARDNESS, flag=LinkFlag.CRAB_SHELL)
        belly = Link(body_bottom_left, body_bottom_right, size/2.5, SHELL_HARDNESS, flag=LinkFlag.CRAB_SHELL)

        # Leg links
        thigh_left = Link(body_bottom_left, knee_left, size/1.5, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)
        thigh_right = Link(body_bottom_right, knee_right, size/1.5, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)
        calf_left = Link(knee_left, foot_left, size/2, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)
        calf_right = Link(knee_right, foot_right, size/2, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)

        # Arm links
        arm_left = Link(body_bottom_left, wrist_left, size/1.5, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)
        arm_right = Link(body_bottom_right, wrist_right, size/1.5, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)
        claw_left = Link(wrist_left, clawtip_left, size/1.5, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)
        claw_right = Link(wrist_right, clawtip_right, size/1.5, LIMB_HARDNESS, flag=LinkFlag.CRAB_LIMB)

        # Structural links
        rib_1 = Link(body_top_left, body_bottom_right, (size/2)*(2**(1/2)), SHELL_HARDNESS)
        rib_2 = Link(body_top_right, body_bottom_left, (size/2)*(2**(1/2)), SHELL_HARDNESS)
        quad_left = Link(body_top_left, knee_left, size/1.66, MUSCLE_HARDNESS)
        quad_right = Link(body_top_right, knee_right, size/1.66, MUSCLE_HARDNESS)
        bicep_left = Link(body_top_left, wrist_left, size/3, MUSCLE_HARDNESS)
        bicep_right = Link(body_top_right, wrist_right, size/3, MUSCLE_HARDNESS)

        # Set belly's gound higher than actual ground to make crab stand
        belly_boundary = pygame.Rect(0, 0, state.tank_width(), state.tank_height()-size/2)
        body_bottom_left.boundary = belly_boundary
        body_bottom_right.boundary = belly_boundary

        vertices = [body_top_left, body_top_right, body_bottom_left, body_bottom_right, knee_left, 
                    knee_right, foot_left, foot_right, wrist_left, wrist_right, clawtip_left, clawtip_right]
        links = [shell_top, shell_left, shell_right, belly, thigh_left, thigh_right, calf_left, calf_right,
                 arm_left, arm_right, claw_left, claw_right, rib_1, rib_2, quad_left, quad_right, bicep_left, 
                 bicep_right]
        crab_softbody = Softbody(vertices, links)
        return Crab(crab_softbody, size)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        return Crab.generate_random(root_position)
    
    def bubble_spawn_chance(self) -> float | None:
        return CRAB_BUBBLE_SPAWN_CHANCE
    
    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'Crab'
        json_dict['size'] = self.size
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        return Crab(softbody, json_dict['size'])
    
    @staticmethod
    def get_spawn_key():
        return pygame.K_c
    
    @staticmethod
    def get_do_collision() -> bool:
        return True