from pygame import Rect
from pygame.surface import Surface
from organism import *
from softbody import *
from resources import *
import state
from egg import Egg
import math

GOBY_START_SIZE = 1
GOBY_MAX_SIZE = 8
GOBY_GROWTH_SPEED = 0.001
GOBY_EYE_COLOR = pygame.Color(255, 255, 255)
GOBY_FIN_COLOR = pygame.Color(0, 0, 0, 150)
GOBY_SWIM_SPEED = 1.2
GOBY_IDLE_SPEED = 0.6
GOBY_FLEE_RADIUS = 30
GOBY_BUBBLE_SPAWN_CHANCE = 0.05
GOBY_WANDER_CHANCE = 0.005
GOBY_DESTINATION_SATISFACTION_RADIUS = 3
GOBY_FERTILE_AGES = (7000, 7015)
GOBY_EGG_LAYING_CHANCE = 0.1
GOBY_EGG_HATCH_AGE = 1000
GOBY_EGG_COLOR = pygame.Color(255, 90, 90, 100)
GOBY_EGG_RADIUS = 1
GOBY_EGG_DENSITY = 0.3
class Goby(Organism):

    def __init__(self, softbody: Softbody, age: int = 0, destination: tuple[int, int] | None = None,
                 direction: tuple[float, float] = (-1.0, 0.0), speed: float = GOBY_IDLE_SPEED,
                 ai_status: AIStatus = AIStatus.IDLE, alive: bool = True):
        super().__init__(softbody, age, ai_status, alive)
        self.fin_position = 1
        self.direction = direction
        self.speed = speed
        self.destination = destination
        self.size = Goby.calculate_size(age)

    def mature(self):
        new_size = Goby.calculate_size(self.age)
        if new_size != self.size:
            self.size = new_size
            self.update_links()

    def lay_egg(self, tank):
        knee_coordinates = self.softbody.vertices[2].x_y()
        tank.organisms.insert(0, Egg.generate_random(knee_coordinates, Goby, GOBY_EGG_HATCH_AGE,
                                                     GOBY_EGG_COLOR, GOBY_EGG_RADIUS, GOBY_EGG_DENSITY))

    @staticmethod
    def calculate_size(age: int) -> int:
        return math.floor(min(GOBY_MAX_SIZE, GOBY_START_SIZE + age*GOBY_GROWTH_SPEED))

    def update_ai(self, tank):
        self.mature()
        self.update_ai_status()
        if self.ai_status == AIStatus.WANDERING:
            self.wander()
        elif self.ai_status == AIStatus.IDLE:
            self.idle()
        elif self.ai_status == AIStatus.FLEEING:
            self.flee()

        if GOBY_FERTILE_AGES[0] < self.age and self.age <= GOBY_FERTILE_AGES[1]:
            if random.random() < GOBY_EGG_LAYING_CHANCE:
                self.lay_egg(tank)

    def update_ai_status(self):

        # If mouse is too close, flee
        if distance(self.root_position(), (get_relative_mouse_position())) < GOBY_FLEE_RADIUS:
            self.ai_status = AIStatus.FLEEING
        # If mouse is not too close and the goby is still fleeing, idle
        elif self.ai_status == AIStatus.FLEEING:
            self.ai_status = AIStatus.IDLE
        # If the goby is idle, take a chance at wandering
        elif self.ai_status == AIStatus.IDLE and random.random() < GOBY_WANDER_CHANCE:
            self.destination = self.random_wander_destination()
            self.ai_status = AIStatus.WANDERING
        # If the goby is wandering and reaches it's destination, idle
        elif self.ai_status == AIStatus.WANDERING and self.satisfied_with_destination():
            self.ai_status = AIStatus.IDLE

    def satisfied_with_destination(self):
        if self.destination:
            return distance(self.root_position(), self.destination) < GOBY_DESTINATION_SATISFACTION_RADIUS
        return True

    def wander(self):
        self.speed = graduate_value_towards(self.speed, GOBY_SWIM_SPEED, 0.05)
        self.direction = direction_vector(self.root_position(), self.destination)
        self.swim(self.speed, self.direction)

    def idle(self):
        self.speed = graduate_value_towards(self.speed, GOBY_IDLE_SPEED, 0.05)
        self.direction = normalize((self.direction[0], 0)) # Eliminate y-direction and normalise
        self.swim(self.speed, self.direction)

        # If close to the edge of the tank, turn around
        if self.root_position()[0] < 10 and self.direction[0] < 0:
            self.turn_around()
        elif self.root_position()[0] > state.tank_width() - 10 and self.direction[0] > 0:
            self.turn_around()

    def random_wander_destination(self) -> tuple[int, int]:
        collision_sculptures = state.selected_tank.get_collision_sculptures() # type: ignore
        destination = (0, 0)
        for _ in range(20):
            destination = (random.randint(10, state.tank_width()-10),
                        random.randint(10, state.tank_height()-10))
            if not Vertex.collides_with_any_sculptures(*destination, collision_sculptures):
                return destination
        return destination

    def flee(self):
        mouse_pos = get_relative_mouse_position()
        root_pos = self.root_position()

        self.speed = 5 - distance(self.root_position(), mouse_pos)/10
        anti_mouse_direction = direction_vector(mouse_pos, root_pos)
        self.swim(self.speed, anti_mouse_direction)


    def turn_around(self):
        self.direction = (-self.direction[0], self.direction[1])
        self.softbody.vertices[1].y += self.fin_position
        self.softbody.vertices[2].y += self.fin_position
        self.softbody.vertices[3].y += self.fin_position
        self.softbody.vertices[0].y -= self.fin_position

    def swim(self, speed, direction):
        head = self.softbody.vertices[0]
        vx = direction[0] * speed * 20
        vy = direction[1] * speed * 20

        head.lx -= vx
        head.ly -= vy

        if random.random() < speed/2:
            self.fin_position *= -1
            tailfin =  self.softbody.vertices[3]
            tailfin.lx -= self.fin_position * self.direction[1] * min(2, self.speed) * 10
            tailfin.ly -= self.fin_position * self.direction[0] * min(2, self.speed) * 10
    
    def render(self, tank_rect: Rect) -> Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)
        head, abdomen, knee, tailfin = self.softbody.vertices

        pygame.draw.polygon(surface, GOBY_FIN_COLOR, [
            (knee.x, knee.y),
            (tailfin.x, tailfin.y + self.size/4),
            (tailfin.x, tailfin.y - self.size/4)
        ])
        pygame.draw.circle(surface, BLACK, (head.x, head.y), self.size/6)
        pygame.draw.circle(surface, BLACK, (abdomen.x, abdomen.y), self.size/4)

        pygame.draw.polygon(surface, BLACK, [
            (head.x, head.y+self.size/6), 
            (head.x, head.y-self.size/6),
            (abdomen.x, abdomen.y-self.size/4),
            (tailfin.x, tailfin.y),
            (abdomen.x, abdomen.y+self.size/4),
        ])

        pygame.draw.line(surface, BLACK, (head.x, head.y), (abdomen.x, abdomen.y), int(self.size/3))

        if self.alive:
            surface.set_at((int(head.x), int(head.y-1)), GOBY_EYE_COLOR)

        return surface
    
    @staticmethod
    def generate_random(root_position: tuple[float, float], age: int | None = None):
        root_x, root_y = root_position
        if age == None:
            age = random.randint(0, 8000)
        size = Goby.calculate_size(age)

        # Generate vertices
        head = Vertex(root_x, root_y, 0, [], VertexFlag.GOBY_HEAD)
        abdomen = Vertex(root_x + size/3, root_y, 0, [], VertexFlag.GOBY_ABDOMEN)
        knee = Vertex(root_x + size*2/3, root_y, 0, [], VertexFlag.NONE)
        tailfin = Vertex(root_x + size, root_y, 0, [], VertexFlag.GOBY_TAILFIN)

        # Link vertices
        neck, calf, tail = Goby.generate_links([head, abdomen, knee, tailfin], size)

        vertices = [head, abdomen, knee, tailfin]
        links = [neck, calf, tail]
        goby_softbody = Softbody(vertices, links)
        return Goby(goby_softbody, age)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        return Goby.generate_random(root_position, 0)
    
    @staticmethod
    def generate_links(vertices: list[Vertex], size: int):
        head, abdomen, knee, tailfin = vertices
        neck = Link(head, abdomen, size/3, flag=LinkFlag.GOBY_NECK, tension=0.66)
        calf = Link(abdomen, knee, size*2/3, tension=0.66)
        tail = Link(knee, tailfin, size/3, flag=LinkFlag.GOBY_TAIL, tension=0.66)
        return [neck, calf, tail]
    
    def update_links(self):
        self.softbody.links = self.generate_links(self.softbody.vertices, self.size)
    
    def bubble_spawn_chance(self) -> float | None:
        return GOBY_BUBBLE_SPAWN_CHANCE
    
    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'Goby'
        json_dict['destination'] = self.destination
        json_dict['direction'] = self.direction
        json_dict['speed'] = self.speed
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        age = json_dict['age']
        destination = json_dict['destination']
        direction = json_dict['direction']
        speed = json_dict['speed']
        ai_status = AIStatus(json_dict['ai_status'])
        alive = json_dict['alive']
        return Goby(softbody, age, destination, direction, speed, ai_status, alive)
    
    @staticmethod
    def get_spawn_key():
        return pygame.K_g
    
    @staticmethod
    def get_do_collision() -> bool:
        return True