"""
🌍 YAPPYVERSE WORLD MODEL 🌍

Manages 3D environments, locations, and timeline
Integrates with lingbot-world for avatar environments
Pauli "The Polyglot" Morelli monitors all locations
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import json
import uuid


class LocationType(Enum):
    """Types of locations in the Yappyverse"""
    HOMES = "homes"  # Where sleeper agents live
    SAFE_HOUSES = "safe_houses"  # Agent meeting points
    MONITORING_STATIONS = "monitoring_stations"  # Data collection
    PORTALS = "portals"  # Time travel entry/exit
    KEY_SITES = "key_sites"  # Environmental importance
    VIRTUAL_HUBS = "virtual_hubs"  # Digital meeting spaces


class TimelineEventType(Enum):
    """Types of timeline events"""
    MISSION = "mission"
    DISCOVERY = "discovery"
    ALLIANCE = "alliance"
    CONFLICT = "conflict"
    TECH_ADVANCE = "tech_advance"
    ECO_MILESTONE = "eco_milestone"


@dataclass
class Location:
    """
    A location in the Yappyverse
    
    Can be real-world location where agents operate
    or virtual environment for 3D avatar interactions
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    location_type: LocationType = LocationType.HOMES
    real_world_address: str = ""  # Actual geographic location
    coordinates: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))  # lat, lng
    description: str = ""
    environment_3d_url: str = ""  # Link to lingbot-world 3D scene
    current_agents: List[str] = field(default_factory=list)  # Character IDs present
    secret_facilities: List[str] = field(default_factory=list)  # Hidden tech
    risk_level: int = 1  # 1-10, chance of discovery
    environmental_threat: str = ""  # Local eco issue being addressed
    cover_story: str = ""  # What humans think this place is
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "location_type": self.location_type.value,
            "real_world_address": self.real_world_address,
            "coordinates": self.coordinates,
            "description": self.description,
            "environment_3d_url": self.environment_3d_url,
            "current_agents": self.current_agents,
            "secret_facilities": self.secret_facilities,
            "risk_level": self.risk_level,
            "environmental_threat": self.environmental_threat,
            "cover_story": self.cover_story,
            "created_at": self.created_at
        }


@dataclass
class TimelineEvent:
    """An event in the Yappyverse timeline"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: TimelineEventType = TimelineEventType.MISSION
    year: int = 2026  # 2026 (present) or 2056 (future)
    title: str = ""
    description: str = ""
    characters_involved: List[str] = field(default_factory=list)
    location_id: str = ""
    impact_level: int = 1  # 1-10 importance
    consequences: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)  # Other event IDs
    resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "year": self.year,
            "title": self.title,
            "description": self.description,
            "characters_involved": self.characters_involved,
            "location_id": self.location_id,
            "impact_level": self.impact_level,
            "consequences": self.consequences,
            "related_events": self.related_events,
            "resolved": self.resolved,
            "created_at": self.created_at
        }


class WorldModel:
    """
    Manages the Yappyverse world state
    Tracks locations, timeline, and 3D environments
    """
    
    def __init__(self, storage_path: str = "yappyverse_world.json"):
        self.storage_path = storage_path
        self.locations: Dict[str, Location] = {}
        self.timeline: Dict[str, TimelineEvent] = {}
        self._load_world()
    
    def _load_world(self) -> None:
        """Load world state from storage"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load locations
                    for loc_data in data.get("locations", []):
                        loc = Location(
                            id=loc_data["id"],
                            name=loc_data["name"],
                            location_type=LocationType(loc_data["location_type"]),
                            real_world_address=loc_data.get("real_world_address", ""),
                            coordinates=tuple(loc_data.get("coordinates", [0.0, 0.0])),
                            description=loc_data.get("description", ""),
                            environment_3d_url=loc_data.get("environment_3d_url", ""),
                            current_agents=loc_data.get("current_agents", []),
                            secret_facilities=loc_data.get("secret_facilities", []),
                            risk_level=loc_data.get("risk_level", 1),
                            environmental_threat=loc_data.get("environmental_threat", ""),
                            cover_story=loc_data.get("cover_story", ""),
                            created_at=loc_data.get("created_at", datetime.now().isoformat())
                        )
                        self.locations[loc.id] = loc
                    
                    # Load timeline
                    for event_data in data.get("timeline", []):
                        event = TimelineEvent(
                            id=event_data["id"],
                            event_type=TimelineEventType(event_data["event_type"]),
                            year=event_data["year"],
                            title=event_data["title"],
                            description=event_data["description"],
                            characters_involved=event_data.get("characters_involved", []),
                            location_id=event_data.get("location_id", ""),
                            impact_level=event_data.get("impact_level", 1),
                            consequences=event_data.get("consequences", []),
                            related_events=event_data.get("related_events", []),
                            resolved=event_data.get("resolved", False),
                            created_at=event_data.get("created_at", datetime.now().isoformat())
                        )
                        self.timeline[event.id] = event
        except Exception as e:
            print(f"Error loading world: {e}")
            self._initialize_default_world()
    
    def _initialize_default_world(self) -> None:
        """Create default world locations"""
        # Add some starter locations
        locations = [
            {
                "name": "The Warren - Portland Hub",
                "location_type": LocationType.SAFE_HOUSES,
                "real_world_address": "Portland, Oregon, USA",
                "coordinates": (45.5152, -122.6784),
                "description": "Underground bunker disguised as a garden shed. Meeting point for Pacific Northwest agents.",
                "environmental_threat": "Urban deforestation",
                "cover_story": "Community garden tool shed"
            },
            {
                "name": "Whisker Station Alpha",
                "location_type": LocationType.MONITORING_STATIONS,
                "real_world_address": "San Francisco, California, USA",
                "coordinates": (37.7749, -122.4194),
                "description": "Hidden beneath a tech startup office. Monitoring ocean pollution levels.",
                "environmental_threat": "Ocean plastic pollution",
                "cover_story": "Server room for tech company"
            },
            {
                "name": "The Burrow - London Safe House",
                "location_type": LocationType.SAFE_HOUSES,
                "real_world_address": "London, UK",
                "coordinates": (51.5074, -0.1278),
                "description": "Victorian basement network. European coordination center.",
                "environmental_threat": "Air quality degradation",
                "cover_story": "Historical preservation site"
            },
            {
                "name": "Temporal Portal 001",
                "location_type": LocationType.PORTALS,
                "real_world_address": "Remote location, coordinates classified",
                "coordinates": (0.0, 0.0),  # Hidden
                "description": "Main entry/exit point for 2056. Highly classified.",
                "environmental_threat": "Timeline stability",
                "cover_story": "Abandoned research facility"
            },
            {
                "name": "Coral Watch Station",
                "location_type": LocationType.KEY_SITES,
                "real_world_address": "Great Barrier Reef, Australia",
                "coordinates": (-18.2871, 147.6992),
                "description": "Underwater monitoring station tracking reef bleaching.",
                "environmental_threat": "Coral reef bleaching",
                "cover_story": "Marine research outpost"
            }
        ]
        
        for loc_data in locations:
            location = Location(**loc_data)
            self.locations[location.id] = location
        
        # Add starter timeline events
        events = [
            {
                "event_type": TimelineEventType.TECH_ADVANCE,
                "year": 2056,
                "title": "The Discovery of Temporal Displacement",
                "description": "Scientists in 2056 perfect time travel technology as Earth's condition becomes critical.",
                "impact_level": 10,
                "consequences": ["Time travel becomes possible", "Agent program initiated"]
            },
            {
                "event_type": TimelineEventType.MISSION,
                "year": 2026,
                "title": "The First Wave",
                "description": "Initial batch of sleeper agents arrives in 2026. Pauli coordinates their deployment.",
                "impact_level": 9,
                "consequences": ["Sleeper agent network established", "Data collection begins"]
            },
            {
                "event_type": TimelineEventType.DISCOVERY,
                "year": 2026,
                "title": "The Pattern Recognition",
                "description": "Agents begin noticing patterns that could lead to environmental breakthroughs.",
                "impact_level": 7,
                "consequences": ["New intervention strategies developed"]
            }
        ]
        
        for event_data in events:
            event = TimelineEvent(**event_data)
            self.timeline[event.id] = event
        
        self.save_world()
    
    def save_world(self) -> None:
        """Save world state to storage"""
        try:
            data = {
                "locations": [loc.to_dict() for loc in self.locations.values()],
                "timeline": [event.to_dict() for event in self.timeline.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving world: {e}")
    
    def create_location(self, **kwargs) -> Location:
        """Create a new location"""
        location = Location(**kwargs)
        self.locations[location.id] = location
        self.save_world()
        return location
    
    def get_location(self, loc_id: str) -> Optional[Location]:
        """Get location by ID"""
        return self.locations.get(loc_id)
    
    def find_location_by_name(self, name: str) -> Optional[Location]:
        """Find location by name"""
        for loc in self.locations.values():
            if loc.name.lower() == name.lower():
                return loc
        return None
    
    def list_locations(self, loc_type: Optional[LocationType] = None) -> List[Location]:
        """List all locations, optionally filtered by type"""
        if loc_type:
            return [loc for loc in self.locations.values() if loc.location_type == loc_type]
        return list(self.locations.values())
    
    def add_agent_to_location(self, loc_id: str, char_id: str) -> bool:
        """Add an agent to a location"""
        loc = self.get_location(loc_id)
        if loc and char_id not in loc.current_agents:
            loc.current_agents.append(char_id)
            self.save_world()
            return True
        return False
    
    def remove_agent_from_location(self, loc_id: str, char_id: str) -> bool:
        """Remove an agent from a location"""
        loc = self.get_location(loc_id)
        if loc and char_id in loc.current_agents:
            loc.current_agents.remove(char_id)
            self.save_world()
            return True
        return False
    
    def create_timeline_event(self, **kwargs) -> TimelineEvent:
        """Create a new timeline event"""
        event = TimelineEvent(**kwargs)
        self.timeline[event.id] = event
        self.save_world()
        return event
    
    def get_timeline_for_year(self, year: int) -> List[TimelineEvent]:
        """Get all events for a specific year"""
        return [e for e in self.timeline.values() if e.year == year]
    
    def get_timeline_for_character(self, char_id: str) -> List[TimelineEvent]:
        """Get all events involving a character"""
        return [e for e in self.timeline.values() if char_id in e.characters_involved]
    
    def connect_events(self, event_id1: str, event_id2: str) -> bool:
        """Connect two events as related"""
        event1 = self.timeline.get(event_id1)
        event2 = self.timeline.get(event_id2)
        
        if event1 and event2:
            if event_id2 not in event1.related_events:
                event1.related_events.append(event_id2)
            if event_id1 not in event2.related_events:
                event2.related_events.append(event_id1)
            self.save_world()
            return True
        return False
    
    def get_3d_environment_url(self, loc_id: str) -> Optional[str]:
        """Get 3D environment URL for a location (lingbot-world integration)"""
        loc = self.get_location(loc_id)
        if loc and loc.environment_3d_url:
            return loc.environment_3d_url
        return None
    
    def generate_3d_scene_config(self, loc_id: str) -> Dict:
        """Generate configuration for lingbot-world 3D scene"""
        loc = self.get_location(loc_id)
        if not loc:
            return {}
        
        return {
            "scene_name": loc.name,
            "environment_type": loc.location_type.value,
            "coordinates": loc.coordinates,
            "character_positions": [
                {"character_id": char_id, "position": self._generate_random_position()}
                for char_id in loc.current_agents[:5]  # Limit to 5 characters
            ],
            "props": self._generate_scene_props(loc),
            "lighting": self._generate_lighting_config(loc),
            "secret_areas_visible": False  # Only visible to agents
        }
    
    def _generate_random_position(self) -> Dict[str, float]:
        """Generate random position in 3D space"""
        import random
        return {
            "x": random.uniform(-10, 10),
            "y": 0,
            "z": random.uniform(-10, 10)
        }
    
    def _generate_scene_props(self, loc: Location) -> List[Dict]:
        """Generate props based on location type"""
        props_by_type = {
            LocationType.HOMES: ["couch", "food_bowl", "window", "toy"],
            LocationType.SAFE_HOUSES: ["hologram_table", "secret_door", "communication_array"],
            LocationType.MONITORING_STATIONS: ["screens", "sensors", "data_consoles"],
            LocationType.PORTALS: ["temporal_gateway", "energy_field", "control_panel"],
            LocationType.KEY_SITES: ["environmental_sensors", "protection_equipment"],
            LocationType.VIRTUAL_HUBS: ["holographic_interface", "data_streams", "avatar_stations"]
        }
        
        props = props_by_type.get(loc.location_type, ["generic_prop"])
        return [{"type": prop, "position": self._generate_random_position()} for prop in props]
    
    def _generate_lighting_config(self, loc: Location) -> Dict:
        """Generate lighting configuration"""
        return {
            "time_of_day": "variable",
            "ambient": 0.6,
            "secret_areas_dim": True,  # Hidden areas are darker
            "special_effects": ["temporal_shimmer"] if loc.location_type == LocationType.PORTALS else []
        }
    
    def get_mission_map(self) -> Dict:
        """Get complete mission map for Pauli's dashboard"""
        return {
            "total_locations": len(self.locations),
            "active_hubs": len(self.list_locations(LocationType.SAFE_HOUSES)),
            "monitoring_stations": len(self.list_locations(LocationType.MONITORING_STATIONS)),
            "agent_deployments": sum(len(loc.current_agents) for loc in self.locations.values()),
            "timeline_events_2026": len(self.get_timeline_for_year(2026)),
            "timeline_events_2056": len(self.get_timeline_for_year(2056)),
            "high_risk_locations": [loc.name for loc in self.locations.values() if loc.risk_level >= 7],
            "critical_threats": list(set(loc.environmental_threat for loc in self.locations.values() if loc.environmental_threat))
        }
    
    def get_world_state_summary(self) -> str:
        """Get narrative summary of current world state"""
        active_agents = sum(len(loc.current_agents) for loc in self.locations.values())
        high_risk = len([loc for loc in self.locations.values() if loc.risk_level >= 7])
        
        return f"""
🌍 YAPPYVERSE WORLD STATE REPORT 🌍

The network spans {len(self.locations)} strategic locations across the globe.
Currently, {active_agents} sleeper agents maintain their cover while working to prevent Earth's destruction.

HIGH PRIORITY ALERTS:
- {high_risk} locations at elevated risk of discovery
- Active monitoring of {len(self.list_locations(LocationType.MONITORING_STATIONS))} environmental threat zones

TIMELINE STATUS:
- {len(self.get_timeline_for_year(2026))} events recorded in present timeline
- {len(self.get_timeline_for_year(2056))} events from the future documented

Pauli "The Polyglot" Morelli continues coordinating from the central hub,
ensuring each agent maintains their cover while advancing the mission to save Earth.

The future depends on their success.
        """