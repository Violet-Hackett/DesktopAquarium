from organism import *
import pygame

SNAIL_BUBBLE_SPAWN_RATE = 0.02
DEFAULT_SNAIL_SIZE = 12
SNAIL_MUSCLE_TOUGHNESS = 0.2
SNAIL_BODY_TOUGHNESS = 0.6
SNAIL_SHELL_TOUGHNESS = 0.9
SNAIL_EYE_COLOR = (0, 0, 0)
SNAIL_SHELL_COLOR = (0, 0, 0)
SNAIL_BODY_COLOR = (0, 0, 0)
SNAIL_BODY_ALPHA = 150
SNAIL_SENSORY_RADIUS = 10
SNAIL_SPEED = 1
SNAIL_LURCH_DELAY = 8 # Number of frames to wait between snail lurches, must be even
HEADLIFT_FORCE = 1.5
class Snail(Organism):

    def __init__(self, softbody: Softbody, size: float, wall: Wall = Wall.BOTTOM):
        super().__init__(softbody)
        self.size = size
        self.wall = wall

    def update_ai(self, tank):
        self.update_ai_status()
        if self.ai_status == AIStatus.WANDERING:
            self.wander()
        elif self.ai_status == AIStatus.HIDING:
            #self.hide()
            pass

    def update_ai_status(self):
        if distance(self.root_position(), (get_relative_mouse_position())) < SNAIL_SENSORY_RADIUS:
            self.ai_status = AIStatus.HIDING
        else:
            self.ai_status = AIStatus.WANDERING

    def set_gravity(self, gravity: tuple[float, float]):
        for vertex in self.softbody.vertices: 
            vertex.gravity = gravity

    def touching_wall(self, vertex: Vertex) -> Wall | None:
        if vertex.x <= 1:
            return Wall.LEFT
        elif vertex.x >= state.tank_width() - 1:
            return Wall.RIGHT
        elif vertex.y <= 1:
            return Wall.TOP
        elif vertex.y >= state.tank_height() - 1:
            return Wall.BOTTOM
        return None
    
    def num_vertices_touching_wall(self) -> int:
        count = 0
        for vertex in self.softbody.vertices: 
            if self.touching_wall(vertex) != None:
                count += 1
        return count

    def stick_to_walls(self):
        head = self.softbody.vertices[0]
        head_wall = self.touching_wall(head)
        if head_wall == Wall.LEFT:
            self.set_gravity((-state.GRAVITY, 0))
            self.wall = head_wall
        elif head_wall == Wall.RIGHT:
            self.set_gravity((state.GRAVITY, 0))
            self.wall = head_wall
        elif head_wall == Wall.TOP:
            self.set_gravity((0, -state.GRAVITY))
            self.wall = head_wall
        elif head_wall == Wall.BOTTOM:
            self.set_gravity((0, state.GRAVITY))
            self.wall = head_wall
        
        if head_wall == None and self.num_vertices_touching_wall() < 2:
            self.set_gravity((0, state.GRAVITY))
            
    def crawl(self):
        self.stick_to_walls()
        head, chest = self.softbody.vertices[:2]
        if state.frame_count % SNAIL_LURCH_DELAY == 0:
            head.x += wall_to_direction(self.wall)[0] * SNAIL_SPEED * SNAIL_LURCH_DELAY
            head.y += wall_to_direction(self.wall)[1] * SNAIL_SPEED * SNAIL_LURCH_DELAY

    def lift_head(self, force: tuple[float, float]):
        head = self.softbody.vertices[0]
        head.x += force[0]
        head.y += force[1]
    
    def put_down_head(self):
        neck_muscle = self.softbody.links[-1]
        neck_muscle.length = self.size/1.75

    def wander(self):
        self.crawl()
        head = self.softbody.vertices[0]
        if distance(head.x_y(), state.tank_size()) < SNAIL_SENSORY_RADIUS/2:
            self.lift_head((0, -HEADLIFT_FORCE))
        elif distance(head.x_y(), (state.tank_width(), 0)) < SNAIL_SENSORY_RADIUS/2:
            self.lift_head((-HEADLIFT_FORCE, 0))
        elif distance(head.x_y(), (0, 0)) < SNAIL_SENSORY_RADIUS/2:
            self.lift_head((0, HEADLIFT_FORCE))
        elif distance(head.x_y(), (0, state.tank_height())) < SNAIL_SENSORY_RADIUS/2:
            self.lift_head((HEADLIFT_FORCE, 0))
        else:
            self.put_down_head()


    def render_body(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)
        head, chest, knee, toe, shell_center, eye_tip_1, eye_tip_2 = self.softbody.vertices

        pygame.draw.polygon(surface, SNAIL_BODY_COLOR, [
            toe.x_y(),
            shell_center.x_y(),
            head.x_y(),
            chest.x_y(),
            knee.x_y()
        ])
        pygame.draw.circle(surface, SNAIL_BODY_COLOR, head.x_y(), self.size/8)
        pygame.draw.line(surface, SNAIL_BODY_COLOR, head.x_y(), eye_tip_1.x_y())
        pygame.draw.line(surface, SNAIL_BODY_COLOR, head.x_y(), eye_tip_2.x_y())

        surface.set_alpha(SNAIL_BODY_ALPHA)
        return surface

    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)
        shell_center, eye_tip_1, eye_tip_2 = self.softbody.vertices[-3:]

        surface.blit(self.render_body(tank_rect), (0, 0))
        surface.set_at((eye_tip_1.x, eye_tip_1.y), SNAIL_EYE_COLOR)
        surface.set_at((eye_tip_2.x, eye_tip_2.y), SNAIL_EYE_COLOR)
        pygame.draw.circle(surface, SNAIL_SHELL_COLOR, (shell_center.x, shell_center.y), self.size/4)

        return surface
    
    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        root_x, root_y = root_position
        size = DEFAULT_SNAIL_SIZE + random.randint(-2, 2)

        # Vertices
        head = Vertex(root_x, root_y, 0.5, [], flag=VertexFlag.SNAIL_BODY)
        chest = Vertex(root_x - size/3, root_y, 0.5, [], flag=VertexFlag.SNAIL_BODY)
        knee = Vertex(root_x - size*2/3, root_y, 0.5, [], flag=VertexFlag.SNAIL_BODY)
        toe = Vertex(root_x - size, root_y, 0.5, [], flag=VertexFlag.SNAIL_BODY)
        shell_center = Vertex(root_x - size/2, root_y - size/3, 0.7, [], flag=VertexFlag.SNAIL_SHELL_CENTER)
        eye_tip_1 = Vertex(root_x, root_y - size/4, -0.1, [], flag=VertexFlag.SNAIL_BODY)
        eye_tip_2 = Vertex(root_x, root_y - size/4, -0.1, [], flag=VertexFlag.SNAIL_BODY)

        # Links
        neck = Link(head, chest, size/3, SNAIL_BODY_TOUGHNESS, flag=LinkFlag.SNAIL_FLESH)
        belly = Link(chest, knee, size/3, SNAIL_SHELL_TOUGHNESS+0.2, flag=LinkFlag.SNAIL_FLESH)
        tail = Link(knee, toe, size/3, SNAIL_BODY_TOUGHNESS, flag=LinkFlag.SNAIL_FLESH)
        eye_1 = Link(head, eye_tip_1, size/4, SNAIL_BODY_TOUGHNESS, flag=LinkFlag.SNAIL_FLESH)
        eye_2 = Link(head, eye_tip_2, size/4, SNAIL_BODY_TOUGHNESS, flag=LinkFlag.SNAIL_FLESH)

        # Structural shell links
        shell_link_1 = Link(shell_center, knee, size/3, SNAIL_SHELL_TOUGHNESS, flag=LinkFlag.SNAIL_SHELL)
        shell_link_2 = Link(shell_center, chest, size/3, SNAIL_SHELL_TOUGHNESS, flag=LinkFlag.SNAIL_SHELL)
        neck_muscle = Link(shell_center, head, size/1.75, SNAIL_MUSCLE_TOUGHNESS)

        vertices = [head, chest, knee, toe, shell_center, eye_tip_1, eye_tip_2]
        links = [neck, belly, tail, eye_1, eye_2, shell_link_1, shell_link_2, neck_muscle]
        snail_softbody = Softbody(vertices, links)
        return Snail(snail_softbody, size)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        return Snail.generate_random(root_position)
    
    def bubble_spawn_chance(self) -> float | None:
        return SNAIL_BUBBLE_SPAWN_RATE

    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'Snail'
        json_dict['size'] = self.size
        json_dict['wall'] = self.wall.value
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        size = json_dict['size']
        wall = Wall(json_dict['wall'])
        return Snail(softbody, size, wall)