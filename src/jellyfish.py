from organism import *
from egg import Egg

JELLYFISH_HEAD_DENSITY = 0
JELLYFISH_ARM_DENSITY = 0
JELLYFISH_FLESH_DENSITY = 0
JELLYFISH_NUM_BELL_VERTICES = 5 # <- Must be odd
JELLYFISH_MIN_SIZE = 1
JELLYFISH_MAX_SIZE = 15
JELLYFISH_GROWTH_RATE = 0.005
JELLYFISH_NUM_ARM_VERTICES = 9
JELLYFISH_BELL_TENSION = 0.7
JELLYFISH_ARM_TENSION = 0.2
JELLYFISH_ARM_CURL_FACTOR = 0.8
JELLYFISH_BELL_COLOR = pygame.Color(0, 0, 0, 190)
JELLYFISH_FLESH_COLOR = pygame.Color(0, 0, 0, 230)
JELLYFISH_SWIM_SPEED = 0.25
JELLYFISH_DESTINATION_SATISFACTION_RADIUS = 5
JELLYFISH_EGG_HATCH_AGE = 150
JELLYFISH_POLYP_MATURE_AGE = 1000
JELLYFISH_REPRODUCTION_AGE = 3500
POLYP_CAP_DENSITY = 5
POLYP_TENTACLE_DENSITY = -0.025
SOFTBODY_SIZE_REFRESH_RATE = 15
class Jellyfish(Organism):
    def __init__(self, softbody: Softbody, age: int):
        super().__init__(softbody, age)
        self.destination: tuple[int, int] | None = None

    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        head = self.softbody.vertices[0]
        bell_vertices = self.softbody.vertices[1:1+JELLYFISH_NUM_BELL_VERTICES]
        arm_links = self.softbody.links[-10-JELLYFISH_NUM_ARM_VERTICES:-6]
        left_tentacle_links = self.softbody.links[-6:-3]
        right_tentacle_links = self.softbody.links[-3:]

        size = Jellyfish.get_size(self.age)

        # Bell
        pygame.draw.circle(surface, JELLYFISH_FLESH_COLOR, head.x_y(), size/4)
        pygame.draw.polygon(surface, JELLYFISH_BELL_COLOR, list(map(Vertex.x_y, bell_vertices + [head])))

        # Arm 
        arm_width = max(1, min(2, int(size/4)))
        for link in arm_links:
            pygame.draw.line(surface, JELLYFISH_BELL_COLOR, link.v1.x_y(), link.v2.x_y(), width=arm_width)
            pygame.draw.line(surface, JELLYFISH_FLESH_COLOR, link.v1.x_y(), link.v2.x_y(), width=1)

        # Tentacles
        gonad_radius = max(1, min(2, int(size/4)))-1
        for link in left_tentacle_links + right_tentacle_links:
            pygame.draw.line(surface, JELLYFISH_FLESH_COLOR, link.v1.x_y(), link.v2.x_y())
        pygame.draw.circle(surface, JELLYFISH_FLESH_COLOR, left_tentacle_links[-2].v2.x_y(), gonad_radius)
        pygame.draw.circle(surface, JELLYFISH_FLESH_COLOR, right_tentacle_links[-2].v2.x_y(), gonad_radius)
            
        return surface

    def update_ai(self, tank):
        if not self.destination or self.satisfied_with_destination():
            self.destination = self.random_wander_destination()

        if self.age < JELLYFISH_POLYP_MATURE_AGE:
            self.polyp_mode()
        elif self.age >= JELLYFISH_POLYP_MATURE_AGE:
            self.jellyfish_mode()
            self.swim(JELLYFISH_SWIM_SPEED, direction_vector(self.root_position(), self.destination))
            if self.age == JELLYFISH_REPRODUCTION_AGE:
                self.lay_egg(tank)

        if state.frame_count % SOFTBODY_SIZE_REFRESH_RATE:
            self.softbody.links = Jellyfish.generate_links(self.softbody.vertices, self.age)

    def polyp_mode(self):
        top_of_cap_vertex = self.softbody.vertices[1+int(JELLYFISH_NUM_BELL_VERTICES/2)]
        arm_and_tentacle_vertices = self.softbody.vertices[1+JELLYFISH_NUM_BELL_VERTICES:]

        top_of_cap_vertex.density = POLYP_CAP_DENSITY
        for vertex in arm_and_tentacle_vertices:
            vertex.density = POLYP_TENTACLE_DENSITY

    def jellyfish_mode(self):
        top_of_cap_vertex = self.softbody.vertices[1+int(JELLYFISH_NUM_BELL_VERTICES/2)]
        arm_and_tentacle_vertices = self.softbody.vertices[1+JELLYFISH_NUM_BELL_VERTICES:]

        top_of_cap_vertex.density = JELLYFISH_FLESH_DENSITY
        for vertex in arm_and_tentacle_vertices:
            vertex.density = JELLYFISH_FLESH_DENSITY

    def lay_egg(self, tank):
        tank.organisms.insert(0, Egg.generate_random(self.root_position(), Jellyfish, JELLYFISH_EGG_HATCH_AGE,
                                                     JELLYFISH_BELL_COLOR, 1, 2))
    
    def swim(self, speed: float, direction: tuple[float, float]):
        top_of_cap_vertex = self.softbody.vertices[1+int(JELLYFISH_NUM_BELL_VERTICES/2)]
        vx = direction[0] * speed * 20
        vy = direction[1] * speed * 20

        top_of_cap_vertex.lx -= vx
        top_of_cap_vertex.ly -= vy

    def satisfied_with_destination(self):
        dest_distance = distance(self.root_position(), self.destination) # type: ignore
        return dest_distance < JELLYFISH_DESTINATION_SATISFACTION_RADIUS

    def random_wander_destination(self) -> tuple[int, int]:
        collision_sculptures = state.selected_tank.get_collision_sculptures() # type: ignore
        destination = (0, 0)
        for _ in range(20):
            destination = (random.randint(10, state.tank_width()-10),
                        random.randint(10, int(state.tank_height()/2-10)))
            if not Vertex.collides_with_any_sculptures(*destination, collision_sculptures):
                return destination
        return destination

    @staticmethod
    def get_size(age: int) -> int:
        return int(min(JELLYFISH_MAX_SIZE, JELLYFISH_MIN_SIZE + age * JELLYFISH_GROWTH_RATE))
    
    @staticmethod
    def generate_links(vertices: list[Vertex], age: int) -> list:
        head = vertices[0]
        bell_vertices = vertices[1:1+JELLYFISH_NUM_BELL_VERTICES]
        size = Jellyfish.get_size(age)
        bell_vertices_spacing = (size/2.5)
        bell_radius = size/2
        arm_vertices = vertices[7+JELLYFISH_NUM_BELL_VERTICES:]
        arm_vertices_spacing = (size/4)
        left_tentacle_vertices = vertices[1+JELLYFISH_NUM_BELL_VERTICES:4+JELLYFISH_NUM_BELL_VERTICES]
        right_tentacle_vertices = vertices[4+JELLYFISH_NUM_BELL_VERTICES:7+JELLYFISH_NUM_BELL_VERTICES]
        tentacle_vertices_spacing = (size/3)

        body_links: list[Link] = []
        for i, bell_vertex in enumerate(bell_vertices):
            if i != len(bell_vertices) - 1:
                next_bell_vertex = bell_vertices[i+1]
                body_links.append(Link(bell_vertex, next_bell_vertex, bell_vertices_spacing,
                                       JELLYFISH_BELL_TENSION, LinkFlag.JELLYFISH_BELL))
            body_links.append(Link(head, bell_vertex, bell_radius, JELLYFISH_BELL_TENSION, LinkFlag.NONE))

        arm_links: list[Link] = []
        for i, arm_vertex in enumerate(arm_vertices):
            if i != len(arm_vertices) - 1:
                next_arm_vertex = arm_vertices[i+1]
                arm_links.append(Link(arm_vertex, next_arm_vertex, arm_vertices_spacing, JELLYFISH_ARM_TENSION,
                                      LinkFlag.JELLYFISH_ARM))
            if i % 2 == 0 and i < len(arm_vertices)-1:
                arm_links.append(Link(arm_vertex, arm_vertices[i+2], 
                                      arm_vertices_spacing*(JELLYFISH_ARM_CURL_FACTOR+1), 
                                      JELLYFISH_ARM_TENSION))
        arm_links.append(Link(head, arm_vertices[0], arm_vertices_spacing, JELLYFISH_ARM_TENSION,
                              LinkFlag.JELLYFISH_ARM))
        
        left_tentacle_links: list[Link] = []
        for i, left_tentacle_vertex in enumerate(left_tentacle_vertices):
            if i != len(left_tentacle_vertices) - 1:
                next_left_tentacle_vertex = left_tentacle_vertices[i+1]
                left_tentacle_links.append(Link(left_tentacle_vertex, next_left_tentacle_vertex, 
                                                tentacle_vertices_spacing, JELLYFISH_ARM_TENSION,
                                                LinkFlag.JELLYFISH_TENTACLE))
        left_tentacle_links.append(Link(bell_vertices[0], left_tentacle_vertices[0], tentacle_vertices_spacing, 
                                        JELLYFISH_ARM_TENSION, LinkFlag.JELLYFISH_TENTACLE))
        
        right_tentacle_links: list[Link] = []
        for i, right_tentacle_vertex in enumerate(right_tentacle_vertices):
            if i != len(right_tentacle_vertices) - 1:
                next_right_tentacle_vertex = right_tentacle_vertices[i+1]
                right_tentacle_links.append(Link(right_tentacle_vertex, next_right_tentacle_vertex, 
                                                tentacle_vertices_spacing, JELLYFISH_ARM_TENSION,
                                                LinkFlag.JELLYFISH_TENTACLE))
        right_tentacle_links.append(Link(bell_vertices[-1], right_tentacle_vertices[0], tentacle_vertices_spacing, 
                                        JELLYFISH_ARM_TENSION, LinkFlag.JELLYFISH_TENTACLE))
        
        return body_links + arm_links + left_tentacle_links + right_tentacle_links
    
    @staticmethod
    def generate_random(root_position: tuple[float, float], age: int | None = None):

        if age == None:
            age = random.randrange(0, 2000)
        size = Jellyfish.get_size(age)
        
        # VERTICES

        head = Vertex(root_position[0], root_position[1], JELLYFISH_HEAD_DENSITY, [], VertexFlag.JELLYFISH_HEAD)

        bell_vertices: list[Vertex] = []
        bell_vertices_spacing = (size/3)
        bell_radius = size/2
        for i in range(JELLYFISH_NUM_BELL_VERTICES):
            bell_vertices.append(Vertex(head.x+bell_vertices_spacing*i
                                        -bell_vertices_spacing*JELLYFISH_NUM_BELL_VERTICES/2, 
                                        head.y-bell_radius, JELLYFISH_FLESH_DENSITY, [],
                                        VertexFlag.JELLYFISH_FLESH))
        
        arm_vertices: list[Vertex] = []
        arm_vertices_spacing = (size/4)
        for i in range(JELLYFISH_NUM_ARM_VERTICES):
            arm_vertices.append(Vertex(head.x, head.y + (i+1)*arm_vertices_spacing, JELLYFISH_ARM_DENSITY,
                                       [], VertexFlag.JELLYFISH_ARM))
            
        left_tentacle_vertices: list[Vertex] = []
        tentacle_vertices_spacing = (size/3)
        for i in range(3):
            left_tentacle_vertices.append(Vertex(head.x-bell_radius, head.y + (i+1)*tentacle_vertices_spacing, 
                                       JELLYFISH_FLESH_DENSITY, [], VertexFlag.JELLYFISH_FLESH))
        
        right_tentacle_vertices: list[Vertex] = []
        for i in range(3):
            right_tentacle_vertices.append(Vertex(head.x+bell_radius, head.y + (i+1)*tentacle_vertices_spacing, 
                                       JELLYFISH_FLESH_DENSITY, [], VertexFlag.JELLYFISH_FLESH))
        
        vertices = [head] + bell_vertices + left_tentacle_vertices + right_tentacle_vertices + arm_vertices
        links = Jellyfish.generate_links(vertices, age)

        jellyfish_softbody = Softbody(vertices, links)
        return Jellyfish(jellyfish_softbody, age)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        return Jellyfish.generate_random(root_position, 0)
    
    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'Jellyfish'
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        return Jellyfish(softbody, json_dict['age'])
    
    @staticmethod
    def get_do_collision() -> bool:
        return True