from organism import *

class Angle(Organism):
    def __init__(self, softbody: Softbody):
        super().__init__(softbody)

    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        for link in self.softbody.links:
            pygame.draw.line(surface, BLACK, link.v1.x_y(), link.v2.x_y())

        return surface

    def update_ai(self, tank):
        pass

    @staticmethod
    def generate_random(root_position: tuple[float, float]):
        
        root_x, root_y = root_position
        a = Vertex(*root_position, 0.5, [])
        b = Vertex(root_x+3, root_y+3, 0.5, [])
        c = Vertex(root_x+3, root_y-3, 0.5, [])

        ab = Link(a, b, 9*(2**(1/2)), 0.6)
        bc = Link(b, c, 9*(2**(1/2)), 0.6)

        abc = AngleConstraint(a, b, c, 90, 0.05)
            
        vertices = [a, b, c]
        links = [ab, bc]
        angles = [abc]
        angle_softbody = Softbody(vertices, links, angles)
        return Angle(angle_softbody)
    
    @staticmethod
    def generate_newborn(root_position: tuple[float, float]):
        pass

    def bubble_spawn_chance(self) -> float | None:
        return None
    
    # def to_json(self) -> dict:
    #     json_dict = super().to_json()
    #     json_dict['type'] = 'KelpWorm'
    #     json_dict['destination'] = self.destination
    #     json_dict['time_of_last_catch'] = self.time_of_last_catch
    #     return json_dict
    
    # @staticmethod
    # def from_json(json_dict: dict, ids_to_vertices: dict):
    #     softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
    #     destination = json_dict['destination']
    #     ai_status = AIStatus(json_dict['ai_status'])
    #     time_of_last_catch = json_dict['time_of_last_catch']
    #     return KelpWorm(softbody, time_of_last_catch, ai_status, destination)
    
    @staticmethod
    def get_do_collision() -> bool:
        return True