"""
🎭 YAPPYVERSE STORY ENGINE 🎭

Generates episodic stories, comic scripts, and YouTube shorts
Pauli "The Polyglot" Morelli orchestrates the narrative
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import random
import uuid

from .characters import Character, CharacterManager, Species, AgentStatus


class EpisodeType(Enum):
    """Types of story episodes"""
    COMIC = "comic"  # Traditional comic episode
    SHORT = "short"  # YouTube manga-style short
    DAILY_LIFE = "daily_life"  # Character's cover identity moment
    MISSION = "mission"  # Active agent mission
    CROSSOVER = "crossover"  # Multiple characters interact
    FLASHBACK = "flashback"  # 2056 future timeline
    PROPHECY = "prophecy"  # Vision of Earth's destruction


class Tone(Enum):
    """Story tone options"""
    WHIMSICAL = "whimsical"  # Beatrix Potter style
    ADVENTUROUS = "adventurous"  # Disney Pixar action
    HEARTFELT = "heartfelt"  # Emotional character moments
    SUSPENSEFUL = "suspenseful"  # Mission tension
    COMEDIC = "comedic"  # Pet perspective humor
    URGENT = "urgent"  # Environmental stakes


@dataclass
class Panel:
    """A single comic panel"""
    panel_number: int
    description: str  # Visual description for artist/AI
    dialogue: List[Dict[str, str]]  # [{"speaker": "Name", "text": "..."}]
    action: str  # What's happening
    setting: str  # Where it takes place
    perspective: str  # Which character's POV
    emotional_beat: str  # What the reader should feel


@dataclass
class ComicScript:
    """Complete comic episode script"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    episode_number: int = 0
    arc_name: str = ""  # Story arc this belongs to
    characters: List[str] = field(default_factory=list)  # Character IDs
    panels: List[Panel] = field(default_factory=list)
    tone: Tone = Tone.WHIMSICAL
    theme: str = ""  # Environmental message or moral
    word_count: int = 0
    estimated_pages: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "episode_number": self.episode_number,
            "arc_name": self.arc_name,
            "characters": self.characters,
            "panels": [
                {
                    "panel_number": p.panel_number,
                    "description": p.description,
                    "dialogue": p.dialogue,
                    "action": p.action,
                    "setting": p.setting,
                    "perspective": p.perspective,
                    "emotional_beat": p.emotional_beat
                }
                for p in self.panels
            ],
            "tone": self.tone.value,
            "theme": self.theme,
            "word_count": self.word_count,
            "estimated_pages": self.estimated_pages,
            "created_at": self.created_at
        }


@dataclass
class ShortScript:
    """YouTube manga-style short script"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    episode_number: int = 0
    duration_seconds: int = 60  # YouTube Shorts max
    characters: List[str] = field(default_factory=list)
    scenes: List[Dict] = field(default_factory=list)
    hook: str = ""  # First 3 seconds grabber
    voiceover: str = ""  # Narration text
    text_overlays: List[Dict] = field(default_factory=list)  # Manga text bubbles
    music_mood: str = ""  # Background music type
    call_to_action: str = ""  # End card CTA
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "episode_number": self.episode_number,
            "duration_seconds": self.duration_seconds,
            "characters": self.characters,
            "scenes": self.scenes,
            "hook": self.hook,
            "voiceover": self.voiceover,
            "text_overlays": self.text_overlays,
            "music_mood": self.music_mood,
            "call_to_action": self.call_to_action,
            "created_at": self.created_at
        }


@dataclass
class Episode:
    """Complete story episode (metadata)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    episode_type: EpisodeType = EpisodeType.COMIC
    title: str = ""
    summary: str = ""
    script: Optional[Any] = None  # ComicScript or ShortScript
    publish_date: Optional[str] = None
    status: str = "draft"  # draft, reviewing, scheduled, published
    engagement_metrics: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class StoryEngine:
    """
    Generates Yappyverse stories
    Creates comics and YouTube shorts with consistent continuity
    """
    
    # Story prompts for different tones and types
    STORY_TEMPLATES = {
        "daily_life_cover": {
            "setup": "{character} must maintain their cover as {cover_identity} while secretly {secret_action}",
            "conflict": "Humans almost discover the truth when {incident}",
            "resolution": "{character} uses {ability} to deflect suspicion and learns {lesson}",
            "moral": "Sometimes the best disguise is being exactly what they expect"
        },
        "mission_active": {
            "setup": "{character} receives a transmission from 2056 about {threat}",
            "conflict": "The mission requires {objective} but {obstacle} blocks the way",
            "resolution": "Using {ability} and {allies}, they {outcome}",
            "moral": "Even the smallest agents can change the course of history"
        },
        "crossover_teamup": {
            "setup": "{character1} and {character2} discover they're both from 2056",
            "conflict": "Their cover identities create {comedy_situation}",
            "resolution": "They combine {ability1} and {ability2} to {success}",
            "moral": "Trust makes us stronger than stealth"
        },
        "flashback_2056": {
            "setup": "In 2056, {character} witnessed {catastrophe}",
            "conflict": "They had to {desperate_action} to survive",
            "resolution": "This is why they volunteered to go back to {current_year}",
            "moral": "We fight for the future because we remember the past"
        }
    }
    
    # Environmental themes integrated into stories
    ECO_THEMES = [
        "Plastic pollution in oceans",
        "Deforestation and habitat loss",
        "Climate change impacts",
        "Endangered species protection",
        "Sustainable living",
        "Renewable energy",
        "Ocean acidification",
        "Biodiversity loss",
        "Coral reef bleaching",
        "Urban wildlife conservation"
    ]
    
    # Beatrix Potter style opening phrases
    OPENING_PHRASES = [
        "Once upon a time in a garden much like your own...",
        "In a cozy home where humans slept unaware...",
        "On a morning when the dew still clung to the grass...",
        "While the world bustled about its business...",
        "In that magical hour between dog walks...",
        "Beneath the floorboards where secrets are kept..."
    ]
    
    def __init__(self, character_manager: CharacterManager):
        self.character_manager = character_manager
        self.episode_counter = self._load_episode_counter()
        self.story_arc = self._load_story_arc()
        
    def _load_episode_counter(self) -> int:
        """Load current episode number"""
        try:
            with open("yappyverse_story_state.json", "r") as f:
                data = json.load(f)
                return data.get("episode_counter", 0)
        except:
            return 0
    
    def _load_story_arc(self) -> Dict:
        """Load current story arc progress"""
        try:
            with open("yappyverse_story_state.json", "r") as f:
                data = json.load(f)
                return data.get("story_arc", {})
        except:
            return {"current_arc": "The Awakening", "arc_episode": 0}
    
    def _save_state(self):
        """Save story engine state"""
        with open("yappyverse_story_state.json", "w") as f:
            json.dump({
                "episode_counter": self.episode_counter,
                "story_arc": self.story_arc,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def generate_comic_episode(self, 
                              episode_type: EpisodeType = EpisodeType.DAILY_LIFE,
                              characters: Optional[List[str]] = None,
                              tone: Tone = Tone.WHIMSICAL,
                              eco_theme: Optional[str] = None) -> ComicScript:
        """Generate a complete comic episode"""
        
        # Select characters if not provided
        if not characters:
            chars = self.character_manager.list_characters()
            if len(chars) >= 2:
                selected = random.sample(chars, 2)
            else:
                selected = chars
        else:
            selected = [self.character_manager.get_character(c) for c in characters if self.character_manager.get_character(c)]
        
        if not selected:
            raise ValueError("No characters available for story generation")
        
        main_char = selected[0]
        eco_theme = eco_theme or random.choice(self.ECO_THEMES)
        
        # Generate script
        self.episode_counter += 1
        script = ComicScript(
            title=f"Episode {self.episode_counter}: {main_char.name}'s Secret",
            episode_number=self.episode_counter,
            arc_name=self.story_arc.get("current_arc", "The Awakening"),
            characters=[c.id for c in selected],
            tone=tone,
            theme=eco_theme
        )
        
        # Create panels (6-8 panels per episode)
        num_panels = random.randint(6, 8)
        panels = []
        
        # Panel 1: Opening/Setup
        opening = random.choice(self.OPENING_PHRASES)
        panels.append(Panel(
            panel_number=1,
            description=f"Wide establishing shot. {opening} We see {main_char.location or 'a typical suburban home'}. Soft morning light.",
            dialogue=[{"speaker": "Narrator", "text": opening}],
            action="Establishing the setting",
            setting=main_char.location or "Suburban home",
            perspective="Omniscient narrator",
            emotional_beat="Warm, inviting"
        ))
        
        # Panel 2: Character introduction
        panels.append(Panel(
            panel_number=2,
            description=f"Close-up of {main_char.name}. They appear to be {main_char.cover_identity or 'an ordinary pet'}, but their eyes show ancient wisdom.",
            dialogue=[{"speaker": "Narrator", "text": f"This is {main_char.name}, though the {main_char.human_family or 'humans'} know {main_char.pronoun_ref()} by another name."}],
            action="Character introduction",
            setting="Inside the home",
            perspective=main_char.name,
            emotional_beat="Mysterious"
        ))
        
        # Panel 3-4: The secret life
        panels.append(Panel(
            panel_number=3,
            description=f"{main_char.name} checks a hidden device or shows subtle signs of future technology.",
            dialogue=[{"speaker": main_char.name, "text": f"The humans think I'm just {main_char.cover_identity or 'a simple pet'}. If only they knew I was scanning for {eco_theme.lower()}..."}],
            action="Revealing secret mission",
            setting="Hidden spot in the house",
            perspective=main_char.name,
            emotional_beat="Secretive determination"
        ))
        
        # Add remaining panels based on episode type
        if episode_type == EpisodeType.DAILY_LIFE:
            panels.extend(self._generate_daily_life_panels(main_char, eco_theme, start_panel=4))
        elif episode_type == EpisodeType.MISSION:
            panels.extend(self._generate_mission_panels(main_char, selected, eco_theme, start_panel=4))
        elif episode_type == EpisodeType.CROSSOVER and len(selected) > 1:
            panels.extend(self._generate_crossover_panels(selected, eco_theme, start_panel=4))
        
        # Final panel: Closing/Moral
        panels.append(Panel(
            panel_number=len(panels) + 1,
            description=f"{main_char.name} returns to their cover identity, the secret safe for another day. Sunset colors.",
            dialogue=[{"speaker": "Narrator", "text": f"And so {main_char.name} continues the watch, one day closer to saving the world from {eco_theme.lower()}. For in the Yappyverse, even the smallest paws can change the future."}],
            action="Return to normalcy",
            setting="Evening at home",
            perspective="Omniscient",
            emotional_beat="Hopeful, inspiring"
        ))
        
        script.panels = panels
        script.estimated_pages = (len(panels) + 3) // 4  # 4 panels per page
        script.word_count = sum(len(d["text"]) for p in panels for d in p.dialogue)
        
        self._save_state()
        return script
    
    def generate_short_script(self,
                             character_ids: List[str],
                             duration: int = 60) -> ShortScript:
        """Generate YouTube manga-style short script"""
        
        chars = [self.character_manager.get_character(c) for c in character_ids]
        chars = [c for c in chars if c]
        
        if not chars:
            raise ValueError("No valid characters provided")
        
        main_char = chars[0]
        self.episode_counter += 1
        
        eco_theme = random.choice(self.ECO_THEMES)
        
        script = ShortScript(
            title=f"Yappyverse Short #{self.episode_counter}: {main_char.name}'s Mission",
            episode_number=self.episode_counter,
            duration_seconds=duration,
            characters=[c.id for c in chars],
            hook=f"🔥 This {main_char.species.value} is from the FUTURE... and they're here to save Earth! 🌍",
            music_mood="Upbeat, adventurous with mysterious undertones",
            call_to_action="Follow for more Yappyverse adventures! 🐾 #Yappyverse #FutureAnimals #ClimateAction"
        )
        
        # Generate scenes (4-6 scenes for 60 seconds)
        scenes = []
        scene_duration = duration // 5
        
        # Scene 1: Hook (0-3 seconds)
        scenes.append({
            "timestamp": "0:00-0:03",
            "duration": 3,
            "description": f"Fast zoom on {main_char.name}'s eyes with glitch effect revealing 2056 tech",
            "text_overlay": "They look like a normal pet...",
            "voiceover": ""
        })
        
        # Scene 2: Setup (3-15 seconds)
        scenes.append({
            "timestamp": "0:03-0:15",
            "duration": 12,
            "description": f"Montage of {main_char.name} doing 'normal' pet things with subtle hints of intelligence",
            "text_overlay": f"But {main_char.name} is actually from 2056! 🕒",
            "voiceover": f"I'm {main_char.name}, and I'm here from the year 2056 to stop {eco_theme.lower()}."
        })
        
        # Scene 3: The Mission (15-35 seconds)
        scenes.append({
            "timestamp": "0:15-0:35",
            "duration": 20,
            "description": f"{main_char.name} in action, using future abilities to address {eco_theme}",
            "text_overlay": "🌍 Mission: Save Earth! ⚡",
            "voiceover": f"In my time, {eco_theme.lower()} destroyed everything. But here, I can change that."
        })
        
        # Scene 4: Obstacle (35-50 seconds)
        scenes.append({
            "timestamp": "0:35-0:50",
            "duration": 15,
            "description": "A challenge appears - humans nearby, or the task is harder than expected",
            "text_overlay": "Will they succeed? 😰",
            "voiceover": "But I must stay hidden. One wrong move and my cover is blown."
        })
        
        # Scene 5: Resolution + CTA (50-60 seconds)
        scenes.append({
            "timestamp": "0:50-0:60",
            "duration": 10,
            "description": f"{main_char.name} succeeds, returns to cover. End card with subscribe button.",
            "text_overlay": "The Yappyverse needs YOU! 🐾",
            "voiceover": f"Join {main_char.name} and the Yappyverse. Together, we can rewrite the future!"
        })
        
        script.scenes = scenes
        script.voiceover = " ".join([s["voiceover"] for s in scenes if s["voiceover"]])
        
        self._save_state()
        return script
    
    def _generate_daily_life_panels(self, character: Character, eco_theme: str, start_panel: int) -> List[Panel]:
        """Generate panels for daily life episode"""
        panels = []
        
        panels.append(Panel(
            panel_number=start_panel,
            description=f"{character.name} interacts with humans, maintaining their cover while secretly observing {eco_theme.lower()}.",
            dialogue=[
                {"speaker": "Human", "text": "Who's a good {character.species.value}?"},
                {"speaker": character.name, "text": "(thinking) If only you knew I'm analyzing ocean pH levels..."}
            ],
            action="Maintaining cover while gathering data",
            setting="Living room",
            perspective=character.name,
            emotional_beat="Comedic irony"
        ))
        
        panels.append(Panel(
            panel_number=start_panel + 1,
            description=f"{character.name} finds an opportunity to make a small difference regarding {eco_theme.lower()}.",
            dialogue=[{"speaker": "Narrator", "text": f"But {character.name} saw a chance to help, in the smallest of ways."}],
            action="Taking small action",
            setting="Kitchen/yard",
            perspective="Third person",
            emotional_beat="Quiet determination"
        ))
        
        panels.append(Panel(
            panel_number=start_panel + 2,
            description="Humans notice something different but can't quite place it.",
            dialogue=[
                {"speaker": "Human", "text": "Did you do that? That's... surprisingly helpful."},
                {"speaker": character.name, "text": "(innocent look) Woof?"}
            ],
            action="Cover maintained",
            setting="Same location",
            perspective="Third person",
            emotional_beat="Tension relieved with humor"
        ))
        
        return panels
    
    def _generate_mission_panels(self, main_char: Character, characters: List[Character], eco_theme: str, start_panel: int) -> List[Panel]:
        """Generate panels for mission episode"""
        panels = []
        # Similar pattern but higher stakes
        return panels
    
    def _generate_crossover_panels(self, characters: List[Character], eco_theme: str, start_panel: int) -> List[Panel]:
        """Generate panels for crossover episode"""
        panels = []
        # Multiple characters working together
        return panels
    
    def get_story_bible(self) -> Dict:
        """Get the complete story bible for reference"""
        return {
            "universe": {
                "name": "The Yappyverse",
                "concept": "Animals from 2056 time-traveled to 2026 to save Earth",
                "tone": ["Beatrix Potter whimsy", "Disney Pixar heart", "Environmental urgency"],
                "main_controller": "Pauli 'The Polyglot' Morelli"
            },
            "timelines": {
                "2056": "Dystopian future where environmental collapse has occurred",
                "2026": "Present day where sleeper agents work in secret"
            },
            "factions": {
                "Time Travelers": "Main group from 2056",
                "Sleeper Agents": "Disguised as human pets",
                "Resistance": "Active fighters against destruction"
            },
            "themes": self.ECO_THEMES,
            "current_arc": self.story_arc,
            "total_episodes": self.episode_counter
        }