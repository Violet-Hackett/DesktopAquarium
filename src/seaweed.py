from organism import *

SEAWEED_BLADDER_RADIUS = 1
SEAWEED_STIPE_THICKNESS = 1
SEAWEED_BLADDER_DISTANCE = 10
SEAWEED_CURLINESS = 1.8
class Seaweed(Organism):
    def __init__(self, softbody: Softbody):
        super().__init__(softbody)

    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        for vertex in self.softbody.vertices:
            if vertex.flag == VertexFlag.SEAWEED_BLADDER:
                pygame.draw.circle(surface, BLACK, (vertex.x, vertex.y), 
                                SEAWEED_BLADDER_RADIUS)
        for link in self.softbody.links:
            if link.flag == LinkFlag.NONE:
                continue
            p1 = (link.v1.x, link.v1.y)
            p2 = (link.v2.x, link.v2.y)
            pygame.draw.line(surface, BLACK, p1, p2, SEAWEED_STIPE_THICKNESS)
            if link.v2.flag == VertexFlag.SEAWEED_BLADDER:
                p1 = (link.v1.x-SEAWEED_BLADDER_RADIUS, link.v1.y)
                p2 = (link.v2.x+SEAWEED_BLADDER_RADIUS, link.v2.y)
                pygame.draw.line(surface, BLACK, p1, p2, SEAWEED_STIPE_THICKNESS)
                p1 = (link.v1.x+SEAWEED_BLADDER_RADIUS, link.v1.y)
                p2 = (link.v2.x-SEAWEED_BLADDER_RADIUS, link.v2.y)
                pygame.draw.line(surface, BLACK, p1, p2, SEAWEED_STIPE_THICKNESS)
            
        return surface

    def update_ai(self, tank):
        return
    
    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        num_bladders = random.randint(5, 10)
        root_x, root_y = root_position
        vertices = []
        links = []
        bladder_vertices = []
        for i in range(num_bladders):
            # Make seaweed vertices
            x = root_x + random.randint(-10, 10) if i != 0 else root_x
            y = root_y - SEAWEED_BLADDER_DISTANCE * i
            blade_x = x + random.choice((-5, 5))
            bladder_vertex = Vertex(x, y, -0.3, [], VertexFlag.SEAWEED_BLADDER)
            blade_vertex_1 = Vertex(blade_x, y-5, -0.05, [], VertexFlag.SEAWEED_BLADE)
            blade_vertex_2 = Vertex(blade_x, y-SEAWEED_BLADDER_DISTANCE, 
                                    -0.05, [], VertexFlag.SEAWEED_BLADE)
            # Link up the vertices
            blade_vertex_1.links.append(Link(bladder_vertex, blade_vertex_1, 
                                             SEAWEED_BLADDER_DISTANCE/2, 0.5, LinkFlag.SEAWEED_STIPE))
            blade_vertex_2.links.append(Link(blade_vertex_1, blade_vertex_2, 
                                             SEAWEED_BLADDER_DISTANCE/2, 0.5, LinkFlag.SEAWEED_STIPE))
            bladder_vertices.append(bladder_vertex)
            if i != 0:
                bladder_vertex.links.append(Link(bladder_vertices[i-1], bladder_vertex, 
                                                 SEAWEED_BLADDER_DISTANCE, 0.7, LinkFlag.SEAWEED_STIPE))
                if i != 1 and i % 2 == 0:
                    bladder_vertex.links.append(Link(bladder_vertices[i-2], bladder_vertex, 
                                                     SEAWEED_BLADDER_DISTANCE*SEAWEED_CURLINESS, 1.0))
            else:
                bladder_vertex.anchor = True

            # Store vertices and links
            vertices += [bladder_vertex, blade_vertex_1, blade_vertex_2]
            links += bladder_vertex.links + blade_vertex_1.links + blade_vertex_2.links

        seaweed_softbody = Softbody(vertices, links)
        return Seaweed(seaweed_softbody)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        return Seaweed.generate_random(root_position)
    
    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'Seaweed'
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        return Seaweed(softbody)
    
    @staticmethod
    def get_spawn_key():
        return pygame.K_s
    
    @staticmethod
    def get_do_collision() -> bool:
        return False