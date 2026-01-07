from organism import Organism
from typing import Type
import base_organisms.crab as crab, base_organisms.egg as egg, base_organisms.goby as goby, base_organisms.kelpworm as kelpworm, base_organisms.seaweed as seaweed, base_organisms.snail as snail, base_organisms.jellyfish as jellyfish, base_organisms.angle as angle

SUPPORTED_ORGANISM_TYPES: dict[str, Type[Organism]] = {
    'Egg': egg.Egg,
    'Goby': goby.Goby,
    'KelpWorm': kelpworm.KelpWorm,
    'Seaweed': seaweed.Seaweed,
    'Snail': snail.Snail,
    'Jellyfish': jellyfish.Jellyfish,
    'Crab': crab.Crab,
}

SPAWNABLE_ORGANISM_TYPES: dict[str, Type[Organism]] = {
    'Goby': goby.Goby,
    'KelpWorm': kelpworm.KelpWorm,
    'Seaweed': seaweed.Seaweed,
    'Snail': snail.Snail,
    'Jellyfish': jellyfish.Jellyfish,
}