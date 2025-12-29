from organism import *
from typing import Type

class Egg(Organism):
    def __init__(self, softbody: Softbody, species: Type[Organism], hatch_age: int, color: pygame.Color,
                 radius: int, density: float, age: int = 0):
        super().__init__(softbody, age)
        self.species = species
        self.hatch_age = hatch_age
        self.color = color
        self.radius = radius
        self.density = density

    def render(self, tank_rect: pygame.Rect) -> pygame.Surface:
        surface = pygame.Surface(tank_rect.size, pygame.SRCALPHA)

        shell_color = (self.color.r, self.color.g, self.color.b, min(255, self.color.a*2))
        pygame.draw.circle(surface, self.color, self.root_position(), self.radius)
        pygame.draw.circle(surface, shell_color, self.root_position(), self.radius, 1)

        return surface

    def update_ai(self, tank):
        if self.age > self.hatch_age:
            newborn = self.species.generate_newborn(self.root_position())
            tank.organisms.append(newborn)
            tank.organisms.remove(self)
    
    @staticmethod
    def generate_random(root_position: tuple[float, float], species: Type[Organism], hatch_age: int,
                        color: pygame.Color, radius: int, density: float):
        x, y = root_position
        egg_softbody = Softbody([Vertex(x, y, density, [], VertexFlag.EGG)], [])
        return Egg(egg_softbody, species, hatch_age, color, radius, density)
    
    def to_json(self) -> dict:
        json_dict = super().to_json()
        json_dict['type'] = 'Egg'
        json_dict['species'] = self.species.__name__
        json_dict['hatch_age'] = self.hatch_age
        json_dict['color'] = (self.color.r, self.color.g, self.color.b, self.color.a)
        json_dict['radius'] = self.radius
        json_dict['density'] = self.density
        return json_dict
    
    @staticmethod
    def from_json(json_dict: dict, ids_to_vertices: dict):
        softbody = Softbody.from_json(json_dict['softbody'], ids_to_vertices)
        age = json_dict['age']
        species: Type[Organism] = globals().get(json_dict['species']) # type: ignore
        hatch_age = json_dict['hatch_age']
        r, g, b, a = json_dict['color']
        color = pygame.Color(r, g, b, a)
        radius = json_dict['radius']
        density = json_dict['density']

        return Egg(softbody, species, hatch_age, color, radius, density, age)
    
    @staticmethod
    def get_spawn_key():
        return None
    
    @staticmethod
    def get_do_collision() -> bool:
        return True