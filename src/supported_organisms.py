from organism import Organism
from typing import Type
import crab, egg, goby, kelpworm, seaweed, snail, jellyfish

SUPPORTED_ORGANISM_TYPES: dict[str, Type[Organism]] = {
    'Crab': crab.Crab,
    'Egg': egg.Egg,
    'Goby': goby.Goby,
    'KelpWorm': kelpworm.KelpWorm,
    'Seaweed': seaweed.Seaweed,
    'Snail': snail.Snail,
    'Jellyfish': jellyfish.Jellyfish
}

SPAWNABLE_ORGANISM_TYPES: dict[str, Type[Organism]] = {
    'Crab': crab.Crab,
    'Goby': goby.Goby,
    'KelpWorm': kelpworm.KelpWorm,
    'Seaweed': seaweed.Seaweed,
    'Snail': snail.Snail,
    'Jellyfish': jellyfish.Jellyfish
}