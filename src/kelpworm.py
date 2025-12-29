from organism import *

KELPWORM_BUBBLE_SPAWN_CHANCE = 0.01
KELPWORM_BODY_DENSITY = 0.1
KELPWORM_INFLATED_BLADDER_DENSITY = -2
KELPWORM_DEFLATED_BLADDER_DENSITY = 0.2
KELPWORM_EXTENDED_ANCHOR_DENSITY = 8
KELPWORM_RETRACTED_ANCHOR_DENSITY = 0
KELPWORM_HEAD_DENSITY = -0.1
KELPWORM_NUM_BODYLINKS = 6
KELPWORM_RESTED_BODYLINK_DISTANCE = 2
KELPWORM_EXTENDED_BODYLINK_DISTANCE = 6
KELPWORM_BODY_TENSION = 0.6
KELPWORM_NECK_TENSION = 0.9
KELPWORM_WIDTH = 3
KELPWORM_FLESH_COLOR = pygame.Color(0, 0, 0, 150)
KELPWORM_BONE_COLOR = pygame.Color(0, 0, 0, 255)
KELPWORM_WANDER_TIME = 150
KELPWORM_SWIM_SPEED = 2
KELPWORM_DESTINATION_SATISFACTION_RADIUS = 5
KELPWORM_PREY = ['Goby']
KELPWORM_SENSORY_RADIUS = 10
KELPWORM_GRAB_RADIUS = 2
KELPWORM_DIGEST_PERIOD = 300
class KelpWorm(Organism):
    def __init__(self, softbody: Softbody, time_of_last_catch: int = 0, 
                 ai_status: AIStatus = AIStatus.WANDERING, destination: tuple[int, int] | None = None):
        super().__init__(softbody, ai_status=ai_status)
        self.time_of_last_catch = time_of_last_catch
        self.destination = destination
        self.targeted_organism: Organism | None = None
        self.caught_organism: Organism | None = None

    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        head, bladder = self.softbody.vertices[:2]
        body_links = self.softbody.links[1:] if not self.caught_organism else self.softbody.links[1:-1]

        # Body
        for i, link in enumerate(body_links):
            p1 = link.v1.x_y()
            p2 = link.v2.x_y()
            thickness = int(KELPWORM_WIDTH - (i/KELPWORM_NUM_BODYLINKS) * KELPWORM_WIDTH)
            pygame.draw.line(surface, KELPWORM_FLESH_COLOR, p1, p2, thickness)
            pygame.draw.line(surface, KELPWORM_BONE_COLOR, p1, p2, 1)

        # Bladder and neck
        pygame.draw.circle(surface, KELPWORM_FLESH_COLOR, bladder.x_y(), KELPWORM_WIDTH/2 + 1)
        pygame.draw.circle(surface, KELPWORM_BONE_COLOR, bladder.x_y(), KELPWORM_WIDTH/2)
        pygame.draw.line(surface, KELPWORM_BONE_COLOR, head.x_y(), bladder.x_y(), 1)

        # Spike
        head_direction = direction_vector(bladder.x_y(), head.x_y())
        spike_point = (head.x_y()[0] + head_direction[0]*4, head.x_y()[1] + head_direction[1]*4)
        pygame.draw.line(surface, KELPWORM_BONE_COLOR, head.x_y(), spike_point, 1)

        return surface

    def update_ai(self, tank):
        self.update_ai_status()
        if self.ai_status == AIStatus.WANDERING:
            self.wander()
        elif self.ai_status == AIStatus.HUNTING:
            self.hunt(tank)
        elif self.ai_status == AIStatus.DIGESTING:
            self.digest(tank)

    def update_ai_status(self):

        # If prey is caught and the time since last catch is less than the digesting period, digest
        if self.caught_organism and state.frame_count - self.time_of_last_catch < KELPWORM_DIGEST_PERIOD:
            self.ai_status = AIStatus.DIGESTING
        # If the time since last catch is more than the digesting period + wander time, hunt
        elif state.frame_count - self.time_of_last_catch > KELPWORM_WANDER_TIME + KELPWORM_DIGEST_PERIOD:
            self.ai_status = AIStatus.HUNTING
        else:
            self.ai_status = AIStatus.WANDERING

    def satisfied_with_destination(self):
        if self.destination:
            return distance(self.root_position(), self.destination) < KELPWORM_DESTINATION_SATISFACTION_RADIUS
        return False
    
    def digest(self, tank):
        self.retract(keep_anchor=True)

        # Kill the prey halfway through digesting
        if state.frame_count - self.time_of_last_catch > KELPWORM_DIGEST_PERIOD/2:
            self.caught_organism.alive = False # type: ignore

        # Delete the prey right before digesting period ends and reset anchor
        if state.frame_count - self.time_of_last_catch == KELPWORM_DIGEST_PERIOD-1:
            tank.organisms.remove(self.caught_organism)
            self.caught_organism = None
            self.retract(keep_anchor=False)
            self.softbody.links = self.softbody.links[:-1]
    
    def find_target_prey(self, tank):

        target: Organism | None = None
        for organism in tank.organisms:
            if type(organism).__name__ in KELPWORM_PREY:
                prey_root_pos = organism.root_position()
                prey_distance = distance(prey_root_pos, self.root_position())
                if prey_distance < KELPWORM_SENSORY_RADIUS:
                    if not target or distance(target.root_position(), self.root_position()) > prey_distance:
                        target = organism

        self.targeted_organism = target

    def grab(self, prey: Organism):
        head = self.softbody.vertices[0]
        link = Link(head, prey.softbody.vertices[0], 1, 0.9)
        self.softbody.links.append(link)
    
    def hunt(self, tank):
        self.extend()
        self.find_target_prey(tank)
        if self.targeted_organism == None:
            return

        prey_root_pos = self.targeted_organism.root_position() # type: ignore
        prey_distance = distance(prey_root_pos, self.root_position())
        speed = 1 + KELPWORM_SWIM_SPEED*2 - 1/(prey_distance+1)
        prey_direction = direction_vector(self.root_position(), prey_root_pos)
        self.swim(speed, prey_direction)
        if prey_distance < KELPWORM_GRAB_RADIUS:
            self.grab(self.targeted_organism)
            self.caught_organism = self.targeted_organism
            self.time_of_last_catch = state.frame_count
                    
    def wander(self):
        self.retract()
        if not self.destination or self.satisfied_with_destination():
            self.destination = self.random_wander_destination()
        self.direction = direction_vector(self.root_position(), self.destination)
        self.swim(KELPWORM_SWIM_SPEED, self.direction)

    def swim(self, speed: float, direction: tuple[float, float]):
        self.softbody.vertices[0].x += direction[0] * (speed*2)
        self.softbody.vertices[0].y += direction[1] * (speed*2)

    def random_wander_destination(self) -> tuple[int, int]:
        destination = (random.randint(10, state.tank_width()-10),
                       random.randint(10, state.tank_height()-10))
        return destination
    
    def retract(self, keep_anchor: bool = False):
        for link in self.softbody.links[1:]:
            link.length = KELPWORM_RESTED_BODYLINK_DISTANCE
        self.softbody.vertices[1].density = KELPWORM_DEFLATED_BLADDER_DENSITY
        if not keep_anchor:
            self.softbody.vertices[-1].density = KELPWORM_RETRACTED_ANCHOR_DENSITY

    def extend(self):
        for link in self.softbody.links[1:]:
            link.length = graduate_value_towards(link.length, KELPWORM_EXTENDED_BODYLINK_DISTANCE, 0.05)
        self.softbody.vertices[1].density = graduate_value_towards(self.softbody.vertices[1].density,
                                                                   KELPWORM_INFLATED_BLADDER_DENSITY, 0.05)
        self.softbody.vertices[-1].density = graduate_value_towards(KELPWORM_EXTENDED_ANCHOR_DENSITY,
                                                                    self.softbody.vertices[-1].density, 0.01)
    
    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        
        # Generate vertices
        head = Vertex(*root_position, KELPWORM_HEAD_DENSITY, [], VertexFlag.KELPWORM_HEAD)
        bladder = Vertex(head.x, head.y, KELPWORM_DEFLATED_BLADDER_DENSITY, [], VertexFlag.SEAWEED_BLADDER)
        body_vertices: list[Vertex] = []
        for i in range(KELPWORM_NUM_BODYLINKS):
            body_vertices.append(Vertex(bladder.x, bladder.y-KELPWORM_RESTED_BODYLINK_DISTANCE*(i+1), 
                                        KELPWORM_BODY_DENSITY, [], VertexFlag.KELPWORM_BODY))
            
        # Link vertices
        neck = Link(head, bladder, KELPWORM_RESTED_BODYLINK_DISTANCE/2, KELPWORM_NECK_TENSION, LinkFlag.KELPWORM_NECK)
        body_links: list[Link] = []
        body_links.append(Link(bladder, body_vertices[0], KELPWORM_RESTED_BODYLINK_DISTANCE, 
                               KELPWORM_BODY_TENSION, LinkFlag.KELPWORM_BODY))
        for i in range(0, KELPWORM_NUM_BODYLINKS-1):
            body_links.append(Link(body_vertices[i], body_vertices[i+1], KELPWORM_RESTED_BODYLINK_DISTANCE, 
                               KELPWORM_BODY_TENSION, LinkFlag.KELPWORM_BODY))
            
        vertices = [head, bladder] + body_vertices
        links = [neck] + body_links
        kelpworm_softbody = Softbody(vertices, links)
        return KelpWorm(kelpworm_softbody)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        pass

    def bubble_spawn_chance(self) -> float | None:
        return 0.01
    
    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'KelpWorm'
        json_dict['destination'] = self.destination
        json_dict['time_of_last_catch'] = self.time_of_last_catch
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        destination = json_dict['destination']
        ai_status = AIStatus(json_dict['ai_status'])
        time_of_last_catch = json_dict['time_of_last_catch']
        return KelpWorm(softbody, time_of_last_catch, ai_status, destination)