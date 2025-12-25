from pygame import Rect
from pygame.surface import Surface as Surface
from organism import *
from softbody import *
from runtime_resources import *
import state

DEFAULT_GOBY_SIZE = 6
GOBY_EYE_COLOR = pygame.Color(255, 255, 255)
GOBY_FIN_COLOR = pygame.Color(0, 0, 0, 100)
GOBY_RESTING_SPEED = 0.6
GOBY_FLEE_RADIUS = 30
class Goby(Organism):
    def __init__(self, softbody: Softbody, size: float):
        super().__init__(softbody)
        self.size = size
        self.fin_position = 1
        self.direction = -1
        self.speed = GOBY_RESTING_SPEED
        self.ai_status: AIStatus = AIStatus.WANDERING

    def update_ai(self):
        self.update_ai_status()
        if self.ai_status == AIStatus.WANDERING:
            self.wander()
        elif self.ai_status == AIStatus.FLEEING:
            self.flee()

    def update_ai_status(self):
        if distance((self.softbody.vertices[0].x, self.softbody.vertices[0].y), 
                    (get_relative_mouse_position())) < GOBY_FLEE_RADIUS:
            self.ai_status = AIStatus.FLEEING
        else:
            self.ai_status = AIStatus.WANDERING

    def wander(self):
        self.speed = (self.speed - GOBY_RESTING_SPEED) / 1.1 + GOBY_RESTING_SPEED
        self.swim(self.speed)
        if random.random() < 0.01 and random.random() < 0.2:
            self.turn()
        if self.softbody.vertices[0].x < 10 and self.direction == -1:
            self.turn()
        elif self.softbody.vertices[0].x > state.TANK_SIZE[0] - 10 and self.direction == 1:
            self.turn()

    def flee(self):
        self.speed = 5 - distance((self.softbody.vertices[0].x, self.softbody.vertices[0].y), 
                    (get_relative_mouse_position()))/10
        flee_direction = 0
        if get_relative_mouse_position()[0] < self.softbody.vertices[0].x:
            flee_direction = 1
        else:
            flee_direction = -1
        if flee_direction != self.direction:
            self.turn()
        self.swim(self.speed)

    def turn(self):
        self.direction *= -1
        self.softbody.vertices[1].y += self.fin_position
        self.softbody.vertices[2].y += self.fin_position
        self.softbody.vertices[3].y += self.fin_position
        self.softbody.vertices[0].y -= self.fin_position
        #self.speed = 0.0

    def swim(self, speed: float):
        self.softbody.vertices[0].x += self.direction * (speed*2)
        if random.random() < speed/2:
            self.fin_position *= -1
            self.softbody.vertices[3].y += self.fin_position
    
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

        surface.set_at((int(head.x), int(head.y-1)), GOBY_EYE_COLOR)

        return surface
    
    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        root_x, root_y = root_position

        size = DEFAULT_GOBY_SIZE + random.randint(-2, 2)

        # Generate vertices
        head = Vertex(root_x, root_y, 0, [], VertexFlag.GOBY_HEAD)
        abdomen = Vertex(root_x + size/3, root_y, 0, [], VertexFlag.GOBY_ABDOMEN)
        knee = Vertex(root_x + size*2/3, root_y, 0, [], VertexFlag.NONE)
        tailfin = Vertex(root_x + size, root_y, 0, [], VertexFlag.GOBY_TAILFIN)

        # Link vertices
        neck = Link(head, abdomen, size/3, flag=LinkFlag.GOBY_NECK, tension=1.5)
        calf = Link(abdomen, knee, size*2/3, tension=1.5)
        tail = Link(knee, tailfin, size/3, flag=LinkFlag.GOBY_TAIL, tension=1.5)

        vertices = [head, abdomen, knee, tailfin]
        links = [neck, calf, tail]
        goby_softbody = Softbody(vertices, links)
        return Goby(goby_softbody, size)