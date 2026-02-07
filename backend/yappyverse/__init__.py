"""
🐾 THE YAPPYVERSE 🐾
AI Avatar Universe - Animals from Future 2056

Pauli "The Polyglot" Morelli - Main AI Avatar Controller
Managing sleeper agents posing as human pets to save Earth
"""

from .characters import CharacterManager, Character, Species, Faction
from .story_engine import StoryEngine, Episode, ComicScript, ShortScript
from .world_model import WorldModel, Location, Timeline
from .content_pipeline import ComicPipeline, ShortsPipeline

__version__ = "1.0.0"
__all__ = [
    "CharacterManager",
    "Character",
    "Species",
    "Faction",
    "StoryEngine",
    "Episode",
    "ComicScript",
    "ShortScript",
    "WorldModel",
    "Location",
    "Timeline",
    "ComicPipeline",
    "ShortsPipeline",
]