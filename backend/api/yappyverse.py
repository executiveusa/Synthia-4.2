"""
🐾 YAPPYVERSE API ENDPOINTS 🐾

REST API for managing the Yappyverse universe
Pauli "The Polyglot" Morelli's command center
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from yappyverse.characters import CharacterManager, Character, Species, Faction, AgentStatus, PAULI_CONTROLLER
from yappyverse.story_engine import StoryEngine, ComicScript, ShortScript, EpisodeType, Tone
from yappyverse.world_model import WorldModel, Location, TimelineEvent, LocationType
from yappyverse.content_pipeline import ComicPipeline, ShortsPipeline, ContentScheduler


# Initialize managers
character_manager = CharacterManager()
world_model = WorldModel()
story_engine = StoryEngine(character_manager)
comic_pipeline = ComicPipeline(character_manager, story_engine, world_model)
shorts_pipeline = ShortsPipeline(character_manager, story_engine)
content_scheduler = ContentScheduler(comic_pipeline, shorts_pipeline)

router = APIRouter(prefix="/yappyverse", tags=["yappyverse"])


# ============ Pydantic Models ============

class CharacterCreate(BaseModel):
    name: str
    full_name: Optional[str] = ""
    species: str = "custom"
    faction: str = "time_travelers"
    origin_year: int = 2056
    age_in_2056: int = 0
    cover_identity: str = ""
    human_family: str = ""
    location: str = ""
    mission: str = ""
    personality: List[str] = []
    voice_id: str = ""
    abilities: List[str] = []
    backstory: str = ""


class CharacterResponse(BaseModel):
    id: str
    name: str
    full_name: str
    species: str
    faction: str
    status: str
    cover_identity: str
    location: str
    mission: str


class ComicGenerateRequest(BaseModel):
    character_ids: Optional[List[str]] = None
    episode_type: str = "daily_life"
    tone: str = "whimsical"
    eco_theme: Optional[str] = None


class ShortGenerateRequest(BaseModel):
    character_ids: List[str]
    duration: int = 60


class LocationCreate(BaseModel):
    name: str
    location_type: str = "homes"
    real_world_address: str = ""
    coordinates: tuple = (0.0, 0.0)
    description: str = ""
    environmental_threat: str = ""
    cover_story: str = ""


# ============ Character Endpoints ============

@router.post("/characters", response_model=CharacterResponse)
async def create_character(character: CharacterCreate):
    """Create a new Yappyverse character"""
    try:
        new_char = character_manager.create_character(
            name=character.name,
            full_name=character.full_name,
            species=Species(character.species),
            faction=Faction(character.faction),
            origin_year=character.origin_year,
            age_in_2056=character.age_in_2056,
            cover_identity=character.cover_identity,
            human_family=character.human_family,
            location=character.location,
            mission=character.mission,
            personality=character.personality,
            voice_id=character.voice_id,
            abilities=character.abilities,
            backstory=character.backstory
        )
        return CharacterResponse(
            id=new_char.id,
            name=new_char.name,
            full_name=new_char.full_name,
            species=new_char.species.value,
            faction=new_char.faction.value,
            status=new_char.status.value,
            cover_identity=new_char.cover_identity,
            location=new_char.location,
            mission=new_char.mission
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/characters", response_model=List[CharacterResponse])
async def list_characters(
    faction: Optional[str] = None,
    species: Optional[str] = None,
    status: Optional[str] = None
):
    """List all Yappyverse characters with optional filtering"""
    chars = character_manager.list_characters(
        faction=Faction(faction) if faction else None,
        species=Species(species) if species else None,
        status=AgentStatus(status) if status else None
    )
    return [
        CharacterResponse(
            id=c.id,
            name=c.name,
            full_name=c.full_name,
            species=c.species.value,
            faction=c.faction.value,
            status=c.status.value,
            cover_identity=c.cover_identity,
            location=c.location,
            mission=c.mission
        )
        for c in chars
    ]


@router.get("/characters/{char_id}")
async def get_character(char_id: str):
    """Get detailed character information"""
    char = character_manager.get_character(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char.to_dict()


@router.post("/characters/{char_id}/activate")
async def activate_character(char_id: str):
    """Activate a sleeper agent for mission"""
    success = character_manager.activate_agent(char_id)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"status": "activated", "character_id": char_id}


@router.get("/characters/{char_id}/introduction")
async def get_character_introduction(char_id: str):
    """Get character introduction in Beatrix Potter style"""
    intro = character_manager.generate_character_introduction(char_id)
    return {"introduction": intro}


@router.get("/pauli")
async def get_pauli_info():
    """Get information about Pauli 'The Polyglot' Morelli"""
    return {
        "name": "Pauli",
        "full_name": "Pauli 'The Polyglot' Morelli",
        "title": "Main AI Avatar Controller of the Yappyverse",
        "role": "Coordinates sleeper agents from 2056",
        "mission": "Save Earth from environmental destruction",
        "abilities": PAULI_CONTROLLER["abilities"],
        "personality": PAULI_CONTROLLER["personality"],
        "backstory": PAULI_CONTROLLER["backstory"]
    }


# ============ Story/Content Endpoints ============

@router.post("/comics/generate")
async def generate_comic(request: ComicGenerateRequest):
    """Generate a new comic episode"""
    try:
        script = comic_pipeline.generate_comic(
            characters=request.character_ids,
            episode_type=EpisodeType(request.episode_type),
            tone=Tone(request.tone),
            eco_theme=request.eco_theme
        )
        return {
            "script": script.to_dict(),
            "message": "Comic script generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shorts/generate")
async def generate_short(request: ShortGenerateRequest):
    """Generate a YouTube short script"""
    try:
        script = shorts_pipeline.generate_short(
            character_ids=request.character_ids,
            duration=request.duration
        )
        return {
            "script": script.to_dict(),
            "message": "Short script generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/schedule-daily")
async def schedule_daily_content(background_tasks: BackgroundTasks):
    """Trigger daily content generation (called by cron job)"""
    job_ids = content_scheduler.generate_daily_content()
    
    # Process jobs in background
    for job_id in job_ids:
        background_tasks.add_task(process_content_job, job_id)
    
    return {
        "message": "Daily content scheduled",
        "jobs_created": len(job_ids),
        "job_ids": job_ids
    }


async def process_content_job(job_id: str):
    """Process a content job in the background"""
    # This would be called by Celery in production
    if job_id.startswith("comic_"):
        comic_pipeline.process_job(job_id)
    elif job_id.startswith("short_"):
        # shorts_pipeline.process_job(job_id)
        pass


@router.get("/content/schedule")
async def get_content_schedule():
    """Get upcoming content schedule"""
    return content_scheduler.get_upcoming_content()


# ============ World/Location Endpoints ============

@router.post("/locations")
async def create_location(location: LocationCreate):
    """Create a new location in the Yappyverse"""
    try:
        new_loc = world_model.create_location(
            name=location.name,
            location_type=LocationType(location.location_type),
            real_world_address=location.real_world_address,
            coordinates=location.coordinates,
            description=location.description,
            environmental_threat=location.environmental_threat,
            cover_story=location.cover_story
        )
        return new_loc.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/locations")
async def list_locations(location_type: Optional[str] = None):
    """List all locations"""
    locs = world_model.list_locations(
        loc_type=LocationType(location_type) if location_type else None
    )
    return [loc.to_dict() for loc in locs]


@router.get("/locations/{loc_id}")
async def get_location(loc_id: str):
    """Get location details"""
    loc = world_model.get_location(loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc.to_dict()


@router.get("/world/state")
async def get_world_state():
    """Get complete world state summary"""
    return {
        "mission_map": world_model.get_mission_map(),
        "summary": world_model.get_world_state_summary()
    }


@router.get("/world/timeline")
async def get_timeline(year: Optional[int] = None):
    """Get timeline events"""
    if year:
        events = world_model.get_timeline_for_year(year)
    else:
        events = list(world_model.timeline.values())
    return [event.to_dict() for event in events]


# ============ Story Bible Endpoints ============

@router.get("/story-bible")
async def get_story_bible():
    """Get the complete Yappyverse story bible"""
    return story_engine.get_story_bible()


@router.get("/story-bible/themes")
async def get_eco_themes():
    """Get environmental themes for stories"""
    return {
        "themes": story_engine.ECO_THEMES,
        "count": len(story_engine.ECO_THEMES)
    }


# ============ Stats/Analytics Endpoints ============

@router.get("/stats")
async def get_yappyverse_stats():
    """Get Yappyverse statistics"""
    return {
        "characters": {
            "total": len(character_manager.characters),
            "active_agents": len(character_manager.get_active_agents()),
            "dormant_agents": len(character_manager.get_dormant_agents())
        },
        "locations": {
            "total": len(world_model.locations),
            "by_type": {
                loc_type.value: len(world_model.list_locations(loc_type))
                for loc_type in LocationType
            }
        },
        "content": {
            "total_episodes": story_engine.episode_counter,
            "current_arc": story_engine.story_arc.get("current_arc", "Unknown"),
            "comics_pending": len([j for j in comic_pipeline.jobs.values() if j.status == "pending"]),
            "shorts_pending": len([j for j in shorts_pipeline.jobs.values() if j.status == "pending"])
        },
        "timeline": {
            "events_2026": len(world_model.get_timeline_for_year(2026)),
            "events_2056": len(world_model.get_timeline_for_year(2056))
        }
    }


@router.get("/")
async def yappyverse_root():
    """Yappyverse API root"""
    return {
        "name": "The Yappyverse API",
        "controller": "Pauli 'The Polyglot' Morelli",
        "description": "AI Avatar Universe - Animals from 2056 saving Earth",
        "endpoints": [
            "/yappyverse/characters",
            "/yappyverse/pauli",
            "/yappyverse/locations",
            "/yappyverse/comics/generate",
            "/yappyverse/shorts/generate",
            "/yappyverse/world/state",
            "/yappyverse/story-bible",
            "/yappyverse/stats"
        ],
        "documentation": "Beatrix Potter meets Disney Pixar with environmental urgency"
    }