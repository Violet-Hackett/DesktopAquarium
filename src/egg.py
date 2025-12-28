from organism import *
from typing import Type

class Egg(Organism):
    def __init__(self, softbody: Softbody, species: Type[Organism], hatch_age: int, color: pygame.Color,
                 radius: int, density: float):
        super().__init__(softbody)
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
        if self.age == self.hatch_age:
            print("Egg hatched <3")
            newborn = self.species.generate_newborn(self.root_position())
            tank.organisms.insert(0, newborn)
    
    @staticmethod
    def generate_random(root_position: tuple[float, float], species: Type[Organism], hatch_age: int,
                        color: pygame.Color, radius: int, density: float):
        x, y = root_position
        egg_softbody = Softbody([Vertex(x, y, density, [], VertexFlag.EGG)], [])
        return Egg(egg_softbody, species, hatch_age, color, radius, density)