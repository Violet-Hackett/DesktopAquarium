from organism import Organism
from typing import Type
import crab, egg, goby, kelpworm, seaweed, snail, jellyfish

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