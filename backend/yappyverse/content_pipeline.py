"""
🎬 YAPPYVERSE CONTENT PIPELINE 🎬

Automated comic and YouTube shorts generation
Integrates with Puppeteer for screenshots and publishing
Pauli "The Polyglot" Morelli oversees all content production
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .characters import CharacterManager
from .story_engine import StoryEngine, ComicScript, ShortScript, EpisodeType, Tone
from .world_model import WorldModel


@dataclass
class ContentJob:
    """A content production job"""
    id: str
    job_type: str  # "comic" or "short"
    status: str  # "pending", "generating", "rendering", "publishing", "complete", "failed"
    script: Optional[Dict] = None
    output_files: List[str] = field(default_factory=list)
    scheduled_for: Optional[str] = None
    published_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class ComicPipeline:
    """
    Pipeline for generating Yappyverse comics
    Creates comic panels, renders images, publishes to site
    """
    
    def __init__(self, 
                 character_manager: CharacterManager,
                 story_engine: StoryEngine,
                 world_model: WorldModel,
                 output_dir: str = "content/comics"):
        self.character_manager = character_manager
        self.story_engine = story_engine
        self.world_model = world_model
        self.output_dir = output_dir
        self.jobs: Dict[str, ContentJob] = {}
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_comic(self, 
                      characters: Optional[List[str]] = None,
                      episode_type: EpisodeType = EpisodeType.DAILY_LIFE,
                      tone: Tone = Tone.WHIMSICAL,
                      eco_theme: Optional[str] = None) -> ComicScript:
        """Generate a complete comic episode"""
        
        # Generate script using story engine
        script = self.story_engine.generate_comic_episode(
            episode_type=episode_type,
            characters=characters,
            tone=tone,
            eco_theme=eco_theme
        )
        
        return script
    
    def render_comic_panels(self, script: ComicScript) -> List[str]:
        """
        Render comic panels as images
        Uses DALL-E/Stable Diffusion for panel generation
        """
        rendered_files = []
        
        for panel in script.panels:
            # Generate image for each panel
            # This would integrate with DALL-E or Stable Diffusion
            prompt = self._create_panel_prompt(panel)
            
            # Placeholder for actual image generation
            filename = f"{self.output_dir}/ep{script.episode_number}_panel{panel.panel_number}.png"
            rendered_files.append(filename)
            
            # TODO: Actually generate images using:
            # - DALL-E 3
            # - Stable Diffusion
            # - Midjourney API
            # - Custom model
        
        return rendered_files
    
    def _create_panel_prompt(self, panel) -> str:
        """Create image generation prompt for a panel"""
        base_prompt = f"""
        Comic book panel style, children's book illustration,
        Beatrix Potter meets modern graphic novel aesthetic.
        
        Scene: {panel.description}
        Characters: {panel.perspective}
        Mood: {panel.emotional_beat}
        
        Style: Soft watercolor textures, detailed backgrounds,
        expressive animal characters, cinematic lighting,
        4K quality, professional comic art
        """
        return base_prompt.strip()
    
    def compile_comic(self, script: ComicScript, panel_files: List[str]) -> str:
        """
        Compile panels into final comic format
        Returns path to compiled comic (PDF or web format)
        """
        # Create comic metadata
        comic_data = {
            "script": script.to_dict(),
            "panels": panel_files,
            "compiled_at": datetime.now().isoformat(),
            "format": "web"  # or "pdf"
        }
        
        # Save comic data
        output_file = f"{self.output_dir}/episode_{script.episode_number}_compiled.json"
        with open(output_file, 'w') as f:
            json.dump(comic_data, f, indent=2)
        
        return output_file
    
    def schedule_comic(self, 
                      characters: Optional[List[str]] = None,
                      episode_type: EpisodeType = EpisodeType.DAILY_LIFE,
                      publish_date: Optional[str] = None) -> str:
        """Schedule a comic for generation and publishing"""
        job_id = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = ContentJob(
            id=job_id,
            job_type="comic",
            status="pending",
            scheduled_for=publish_date
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def process_job(self, job_id: str) -> bool:
        """Process a content job"""
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        try:
            if job.job_type == "comic":
                job.status = "generating"
                script = self.generate_comic()
                job.script = script.to_dict()
                
                job.status = "rendering"
                panel_files = self.render_comic_panels(script)
                job.output_files = panel_files
                
                job.status = "publishing"
                compiled = self.compile_comic(script, panel_files)
                job.output_files.append(compiled)
                
                job.status = "complete"
                job.completed_at = datetime.now().isoformat()
                
            return True
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            return False


class ShortsPipeline:
    """
    Pipeline for generating YouTube manga-style shorts
    Creates video scripts, renders animations, publishes to YouTube
    """
    
    def __init__(self,
                 character_manager: CharacterManager,
                 story_engine: StoryEngine,
                 output_dir: str = "content/shorts"):
        self.character_manager = character_manager
        self.story_engine = story_engine
        self.output_dir = output_dir
        self.jobs: Dict[str, ContentJob] = {}
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_short(self,
                      character_ids: List[str],
                      duration: int = 60) -> ShortScript:
        """Generate a YouTube short script"""
        
        script = self.story_engine.generate_short_script(
            character_ids=character_ids,
            duration=duration
        )
        
        return script
    
    def render_short(self, script: ShortScript) -> str:
        """
        Render short video
        Uses RunwayML/Pika for video generation + text overlays
        """
        # TODO: Integrate with:
        # - RunwayML API for video generation
        # - Pika Labs for animations
        # - FFmpeg for editing
        # - PIL for text overlays
        
        output_file = f"{self.output_dir}/short_{script.episode_number}.mp4"
        
        # Placeholder for actual video generation
        return output_file
    
    def add_voiceover(self, script: ShortScript, video_file: str) -> str:
        """
        Add voiceover using ElevenLabs
        Characters speak their lines
        """
        # TODO: Integrate with ElevenLabs API
        # - Generate voice for each character
        # - Mix with background music
        # - Sync with video
        
        return video_file
    
    def add_text_overlays(self, script: ShortScript, video_file: str) -> str:
        """
        Add manga-style text overlays
        """
        # TODO: Use PIL/OpenCV to add text overlays
        return video_file
    
    def schedule_short(self,
                      character_ids: List[str],
                      publish_date: Optional[str] = None) -> str:
        """Schedule a short for generation and publishing"""
        job_id = f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = ContentJob(
            id=job_id,
            job_type="short",
            status="pending",
            scheduled_for=publish_date
        )
        
        self.jobs[job_id] = job
        return job_id


class ContentScheduler:
    """
    Schedules and manages automated content production
    Runs via cron jobs or Celery beat
    """
    
    def __init__(self,
                 comic_pipeline: ComicPipeline,
                 shorts_pipeline: ShortsPipeline):
        self.comic_pipeline = comic_pipeline
        self.shorts_pipeline = shorts_pipeline
        self.schedule_config = self._load_schedule()
    
    def _load_schedule(self) -> Dict:
        """Load content schedule configuration"""
        try:
            with open("yappyverse_schedule.json", 'r') as f:
                return json.load(f)
        except:
            return self._default_schedule()
    
    def _default_schedule(self) -> Dict:
        """Default content schedule"""
        return {
            "comics": {
                "frequency": "weekly",  # One comic per week
                "day": "monday",
                "time": "09:00",
                "episode_type": "daily_life",
                "tone": "whimsical"
            },
            "shorts": {
                "frequency": "3x_weekly",  # 3 shorts per week
                "days": ["tuesday", "thursday", "saturday"],
                "time": "15:00",
                "duration": 60
            },
            "story_arcs": {
                "arc_duration_weeks": 4,
                "current_arc": "The Awakening",
                "arc_episode": 0
            }
        }
    
    def generate_daily_content(self) -> List[str]:
        """Generate content for the day - called by cron job"""
        job_ids = []
        
        today = datetime.now().strftime("%A").lower()
        
        # Check if comic is scheduled for today
        if self.schedule_config["comics"]["day"] == today:
            job_id = self.comic_pipeline.schedule_comic(
                episode_type=self.schedule_config["comics"]["episode_type"]
            )
            job_ids.append(job_id)
        
        # Check if short is scheduled for today
        if today in self.schedule_config["shorts"]["days"]:
            # Get random characters for the short
            chars = self.comic_pipeline.character_manager.list_characters()
            if chars:
                char_ids = [c.id for c in chars[:2]]  # Use up to 2 characters
                job_id = self.shorts_pipeline.schedule_short(char_ids)
                job_ids.append(job_id)
        
        return job_ids
    
    def get_upcoming_content(self) -> Dict:
        """Get list of upcoming scheduled content"""
        return {
            "next_comic": self.schedule_config["comics"]["day"],
            "next_shorts": self.schedule_config["shorts"]["days"],
            "current_arc": self.schedule_config["story_arcs"]["current_arc"],
            "arc_progress": f"{self.schedule_config['story_arcs']['arc_episode']}/"
                           f"{self.schedule_config['story_arcs']['arc_duration_weeks']}"
        }
    
    def advance_story_arc(self):
        """Advance to next story arc episode"""
        self.schedule_config["story_arcs"]["arc_episode"] += 1
        
        # Check if arc is complete
        if (self.schedule_config["story_arcs"]["arc_episode"] >= 
            self.schedule_config["story_arcs"]["arc_duration_weeks"]):
            self._start_new_arc()
        
        self._save_schedule()
    
    def _start_new_arc(self):
        """Start a new story arc"""
        arcs = [
            "The Awakening",
            "The Gathering",
            "Hidden in Plain Sight",
            "The Great Alliance",
            "Race Against Time"
        ]
        
        current = self.schedule_config["story_arcs"]["current_arc"]
        current_index = arcs.index(current) if current in arcs else -1
        next_arc = arcs[(current_index + 1) % len(arcs)]
        
        self.schedule_config["story_arcs"]["current_arc"] = next_arc
        self.schedule_config["story_arcs"]["arc_episode"] = 0
    
    def _save_schedule(self):
        """Save schedule configuration"""
        with open("yappyverse_schedule.json", 'w') as f:
            json.dump(self.schedule_config, f, indent=2)


# Puppeteer automation for site updates and publishing
class PuppeteerAutomation:
    """
    Browser automation using Puppeteer
    Updates Yappyverse website, publishes content, captures analytics
    """
    
    def __init__(self, site_url: str = "https://yappyverse.com"):
        self.site_url = site_url
        self.automation_script = self._generate_puppeteer_script()
    
    def _generate_puppeteer_script(self) -> str:
        """Generate Puppeteer automation script"""
        return """
const puppeteer = require('puppeteer');

async function updateYappyverseSite(content) {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        
        // Login to site
        await page.goto(process.env.YAPPYVERSE_ADMIN_URL);
        await page.type('#email', process.env.YAPPYVERSE_ADMIN_EMAIL);
        await page.type('#password', process.env.YAPPYVERSE_ADMIN_PASSWORD);
        await page.click('#login-button');
        await page.waitForNavigation();
        
        // Navigate to content section
        await page.goto(`${process.env.YAPPYVERSE_ADMIN_URL}/content`);
        
        // Add new comic/short
        await page.click('#add-content');
        await page.type('#title', content.title);
        await page.type('#description', content.description);
        
        // Upload media
        const fileInput = await page.$('#media-upload');
        await fileInput.uploadFile(content.file_path);
        
        // Publish
        await page.click('#publish-button');
        await page.waitForSelector('.success-message');
        
        // Capture screenshot for verification
        await page.screenshot({
            path: `screenshots/publish_${Date.now()}.png`,
            fullPage: true
        });
        
        return { success: true, url: page.url() };
        
    } catch (error) {
        console.error('Automation error:', error);
        return { success: false, error: error.message };
    } finally {
        await browser.close();
    }
}

async function captureComicPanel(sceneConfig) {
    // Capture 3D scene for comic panel
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    await page.goto(sceneConfig.url);
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Wait for 3D scene to load
    await page.waitForSelector('#scene-loaded');
    
    // Capture screenshot
    await page.screenshot({
        path: sceneConfig.output_path,
        type: 'png'
    });
    
    await browser.close();
    return sceneConfig.output_path;
}

module.exports = { updateYappyverseSite, captureComicPanel };
"""
    
    def save_automation_script(self, output_path: str = "yappyverse_automation.js"):
        """Save Puppeteer script to file"""
        with open(output_path, 'w') as f:
            f.write(self.automation_script)
    
    def get_site_update_command(self, content_file: str) -> str:
        """Get command to update site with new content"""
        return f"node yappyverse_automation.js --update --file {content_file}"


# Export main classes
__all__ = [
    "ComicPipeline",
    "ShortsPipeline", 
    "ContentScheduler",
    "ContentJob",
    "PuppeteerAutomation"
]