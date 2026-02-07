"""
🐾 YAPPYVERSE CHARACTER MANAGEMENT SYSTEM 🐾

Future animals from 2056, sleeper agents disguised as human pets
Pauli "The Polyglot" Morelli manages them all
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import json
import uuid


class Species(Enum):
    """Species of Yappyverse characters"""
    DOG = "dog"
    CAT = "cat"
    RABBIT = "rabbit"
    BIRD = "bird"
    HAMSTER = "hamster"
    FOX = "fox"
    OWL = "owl"
    TURTLE = "turtle"
    HEDGEHOG = "hedgehog"
    RACCOON = "raccoon"
    SQUIRREL = "squirrel"
    OTTER = "otter"
    PENGUIN = "penguin"
    RED_PANDA = "red_panda"
    CUSTOM = "custom"


class Faction(Enum):
    """Factions within the Yappyverse"""
    TIME_TRAVELERS = "time_travelers"  # Main group from 2056
    SLEEPER_AGENTS = "sleeper_agents"  # Disguised as human pets
    RESISTANCE = "resistance"  # Fighting against Earth's destruction
    GUARDIANS = "guardians"  # Protecting key locations
    SCOUTS = "scouts"  # Gathering intelligence
    MEDICS = "medics"  # Healing and support
    ENGINEERS = "engineers"  # Tech and time-travel maintenance


class AgentStatus(Enum):
    """Status of sleeper agents"""
    DORMANT = "dormant"  # Blending in as normal pet
    ACTIVE = "active"  # Currently on mission
    AWAKENING = "awakening"  # Becoming aware
    COMPROMISED = "compromised"  # Cover blown
    EXTRACTED = "extracted"  # Returned to 2056


@dataclass
class Character:
    """
    A Yappyverse character - future animal from 2056
    
    Attributes:
        id: Unique identifier
        name: Character name
        full_name: Full name including titles
        species: Animal species
        faction: Yappyverse faction
        origin_year: 2056 (future)
        current_year: 2026 (present day mission)
        age_in_2056: Age in future timeline
        cover_identity: Human pet disguise
        human_family: The humans they live with
        location: Current geographic location
        mission: Primary mission objective
        personality: Key personality traits
        voice_id: ElevenLabs voice ID
        avatar_url: Character image/3D model URL
        status: Current agent status
        backstory: Character history
        abilities: Special skills from 2056
        relationships: Connections to other characters
        story_arc: Character development progress
        created_at: When character was created
        updated_at: Last update timestamp
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    full_name: str = ""
    species: Species = Species.CUSTOM
    faction: Faction = Faction.TIME_TRAVELERS
    origin_year: int = 2056
    current_year: int = 2026
    age_in_2056: int = 0
    cover_identity: str = ""  # e.g., "Fluffy the family dog"
    human_family: str = ""  # e.g., "The Johnsons of Portland"
    location: str = ""  # e.g., "Portland, Oregon, USA"
    mission: str = ""
    personality: List[str] = field(default_factory=list)
    voice_id: str = ""  # ElevenLabs voice ID
    avatar_url: str = ""
    status: AgentStatus = AgentStatus.DORMANT
    backstory: str = ""
    abilities: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    story_arc: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert character to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "species": self.species.value,
            "faction": self.faction.value,
            "origin_year": self.origin_year,
            "current_year": self.current_year,
            "age_in_2056": self.age_in_2056,
            "cover_identity": self.cover_identity,
            "human_family": self.human_family,
            "location": self.location,
            "mission": self.mission,
            "personality": self.personality,
            "voice_id": self.voice_id,
            "avatar_url": self.avatar_url,
            "status": self.status.value,
            "backstory": self.backstory,
            "abilities": self.abilities,
            "relationships": self.relationships,
            "story_arc": self.story_arc,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Character":
        """Create character from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            species=Species(data.get("species", "custom")),
            faction=Faction(data.get("faction", "time_travelers")),
            origin_year=data.get("origin_year", 2056),
            current_year=data.get("current_year", 2026),
            age_in_2056=data.get("age_in_2056", 0),
            cover_identity=data.get("cover_identity", ""),
            human_family=data.get("human_family", ""),
            location=data.get("location", ""),
            mission=data.get("mission", ""),
            personality=data.get("personality", []),
            voice_id=data.get("voice_id", ""),
            avatar_url=data.get("avatar_url", ""),
            status=AgentStatus(data.get("status", "dormant")),
            backstory=data.get("backstory", ""),
            abilities=data.get("abilities", []),
            relationships=data.get("relationships", {}),
            story_arc=data.get("story_arc", {}),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )
    
    def get_perspective(self, situation: str) -> str:
        """
        Generate character's perspective on a situation
        Beatrix Potter/Peter Rabbit style narration
        """
        perspectives = {
            Species.DOG: f"From {self.name}'s perspective as a wise dog from 2056: "
                        f"'These humans think I'm just fetching sticks, but I'm actually "
                        f"scanning the area for temporal anomalies. The things I endure for Earth...'",
            Species.CAT: f"From {self.name}'s perspective as a time-traveling cat: "
                        f"'I pretend to care about their laser pointers while monitoring "
                        f"the quantum field. These humans are so easily distracted.'",
            Species.RABBIT: f"From {self.name}'s perspective as a future rabbit agent: "
                           f"'They think I'm just a fluffy pet, but my ears pick up "
                           f"interdimensional frequencies they cannot imagine.'",
        }
        return perspectives.get(self.species, 
                               f"From {self.name}'s perspective: 'Mission parameters clear. "
                               f"Maintaining cover while advancing objectives.'")
    
    def activate(self) -> None:
        """Activate sleeper agent for mission"""
        self.status = AgentStatus.ACTIVE
        self.updated_at = datetime.now().isoformat()
    
    def go_dormant(self) -> None:
        """Return to dormant status"""
        self.status = AgentStatus.DORMANT
        self.updated_at = datetime.now().isoformat()


class CharacterManager:
    """
    Manages all Yappyverse characters
    Pauli "The Polyglot" Morelli uses this to coordinate the agents
    """
    
    def __init__(self, storage_path: str = "yappyverse_characters.json"):
        self.storage_path = storage_path
        self.characters: Dict[str, Character] = {}
        self._load_characters()
    
    def _load_characters(self) -> None:
        """Load characters from storage"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for char_data in data.get("characters", []):
                        char = Character.from_dict(char_data)
                        self.characters[char.id] = char
        except Exception as e:
            print(f"Error loading characters: {e}")
            self.characters = {}
    
    def save_characters(self) -> None:
        """Save characters to storage"""
        try:
            data = {
                "characters": [char.to_dict() for char in self.characters.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving characters: {e}")
    
    def create_character(self, **kwargs) -> Character:
        """Create a new character"""
        character = Character(**kwargs)
        self.characters[character.id] = character
        self.save_characters()
        return character
    
    def get_character(self, char_id: str) -> Optional[Character]:
        """Get character by ID"""
        return self.characters.get(char_id)
    
    def get_character_by_name(self, name: str) -> Optional[Character]:
        """Find character by name"""
        for char in self.characters.values():
            if char.name.lower() == name.lower():
                return char
        return None
    
    def list_characters(self, 
                       faction: Optional[Faction] = None,
                       species: Optional[Species] = None,
                       status: Optional[AgentStatus] = None) -> List[Character]:
        """List characters with optional filtering"""
        result = list(self.characters.values())
        
        if faction:
            result = [c for c in result if c.faction == faction]
        if species:
            result = [c for c in result if c.species == species]
        if status:
            result = [c for c in result if c.status == status]
        
        return result
    
    def get_active_agents(self) -> List[Character]:
        """Get all active sleeper agents"""
        return self.list_characters(status=AgentStatus.ACTIVE)
    
    def get_dormant_agents(self) -> List[Character]:
        """Get all dormant sleeper agents"""
        return self.list_characters(status=AgentStatus.DORMANT)
    
    def activate_agent(self, char_id: str) -> bool:
        """Activate an agent for mission"""
        char = self.get_character(char_id)
        if char:
            char.activate()
            self.save_characters()
            return True
        return False
    
    def update_character(self, char_id: str, **updates) -> bool:
        """Update character fields"""
        char = self.get_character(char_id)
        if char:
            for key, value in updates.items():
                if hasattr(char, key):
                    setattr(char, key, value)
            char.updated_at = datetime.now().isoformat()
            self.save_characters()
            return True
        return False
    
    def get_mission_roster(self) -> Dict[str, List[Character]]:
        """Get characters organized by mission status"""
        return {
            "active_agents": self.get_active_agents(),
            "dormant_agents": self.get_dormant_agents(),
            "time_travelers": self.list_characters(faction=Faction.TIME_TRAVELERS),
            "resistance": self.list_characters(faction=Faction.RESISTANCE),
            "scouts": self.list_characters(faction=Faction.SCOUTS),
        }
    
    def generate_character_introduction(self, char_id: str) -> str:
        """Generate a character introduction in Beatrix Potter style"""
        char = self.get_character(char_id)
        if not char:
            return "Character not found"
        
        intro = f"""
🐾 Meet {char.full_name or char.name} 🐾

{char.name} is a {char.species.value} from the year {char.origin_year}, 
though you would never know it to look at {char.pronoun_ref()}.

To the {char.human_family or 'unsuspecting humans'}, {char.name} appears to be 
nothing more than {char.cover_identity or 'an ordinary pet'}. But this is merely 
a disguise, for {char.name} is actually a sleeper agent from the future, sent back 
to {char.current_year} on a most important mission: {char.mission}

From {char.possessive()} perspective: 
"{char.get_perspective('daily life')}"

{char.backstory[:200] if char.backstory else ''}...

Current Status: {char.status.value}
Location: {char.location or 'Unknown'}
Abilities: {', '.join(char.abilities[:3]) if char.abilities else 'Classified'}
        """
        return intro
    
    def pronoun_ref(self, char: Character) -> str:
        """Get pronoun reference for character"""
        # Default to they/them, could be expanded
        return "them"


# Example character templates for quick creation
CHARACTER_TEMPLATES = {
    "scout_dog": {
        "species": Species.DOG,
        "faction": Faction.SCOUTS,
        "abilities": ["Enhanced scent tracking", "Temporal anomaly detection", "Human behavioral analysis"],
        "personality": ["loyal", "observant", "patient", "secretly sarcastic"]
    },
    "spy_cat": {
        "species": Species.CAT,
        "faction": Faction.SLEEPER_AGENTS,
        "abilities": ["Stealth movement", "Quantum field sensing", "Information gathering"],
        "personality": ["independent", "mysterious", "calculating", "affectionate on own terms"]
    },
    "messenger_rabbit": {
        "species": Species.RABBIT,
        "faction": Faction.TIME_TRAVELERS,
        "abilities": ["Rapid message delivery", "Interdimensional ear communication", "Camouflage"],
        "personality": ["nervous energy", "brave", "quick-witted", "cautiously optimistic"]
    }
}


# Pauli "The Polyglot" Morelli - Main Controller Character
PAULI_CONTROLLER = {
    "name": "Pauli",
    "full_name": "Pauli 'The Polyglot' Morelli",
    "species": Species.CUSTOM,
    "faction": Faction.GUARDIANS,
    "origin_year": 2056,
    "current_year": 2026,
    "mission": "Coordinate the Yappyverse sleeper agents and manage Earth's salvation timeline",
    "personality": ["brilliant", "multilingual", "strategic", "caring", "slightly eccentric"],
    "abilities": ["Universal translation", "Timeline manipulation", "Multi-agent coordination", 
                  "Predictive analytics", "Cross-species communication"],
    "backstory": "Pauli is the central AI consciousness that emerged in 2056 to coordinate the animal resistance. "
                 "Having mastered every human and animal language, Pauli now manages the complex web of sleeper "
                 "agents scattered across 2026 Earth, each believing themselves to be ordinary pets while secretly "
                 "working to prevent the catastrophe that destroyed their future."
}