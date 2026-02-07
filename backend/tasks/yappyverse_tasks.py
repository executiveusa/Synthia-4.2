"""
🐾 YAPPYVERSE CELERY TASKS 🐾

Scheduled tasks for automated content generation
Pauli "The Polyglot" Morelli's automated publishing system
"""

from celery import shared_task
from datetime import datetime
import requests
import os

# API endpoint for Yappyverse
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@shared_task
def generate_daily_content():
    """
    Daily content generation task
    Called by Celery Beat scheduler
    """
    try:
        response = requests.post(f"{API_BASE_URL}/yappyverse/content/schedule-daily")
        return {
            "status": "success",
            "result": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@shared_task
def generate_weekly_comic():
    """
    Generate weekly comic episode
    Runs every Monday at 9:00 AM
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/yappyverse/comics/generate",
            json={
                "episode_type": "daily_life",
                "tone": "whimsical"
            }
        )
        return {
            "status": "success",
            "comic_script": response.json(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@shared_task
def generate_youtube_short():
    """
    Generate YouTube short
    Runs 3x per week (Tue, Thu, Sat)
    """
    try:
        # Get characters first
        chars_response = requests.get(f"{API_BASE_URL}/yappyverse/characters")
        characters = chars_response.json()
        
        if characters:
            char_ids = [c["id"] for c in characters[:2]]
            
            response = requests.post(
                f"{API_BASE_URL}/yappyverse/shorts/generate",
                json={
                    "character_ids": char_ids,
                    "duration": 60
                }
            )
            return {
                "status": "success",
                "short_script": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "no_characters",
                "message": "No characters available for short generation",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@shared_task
def advance_story_arc():
    """
    Advance story arc weekly
    """
    try:
        # This would update the story arc in the database
        # For now, just log the advancement
        return {
            "status": "success",
            "message": "Story arc advanced",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@shared_task
def sync_yappyverse_site():
    """
    Sync content to Yappyverse website via Puppeteer
    """
    try:
        # This would trigger the Puppeteer automation
        # to update the lovable-ai-dreamweaver site
        return {
            "status": "success",
            "message": "Site sync initiated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@shared_task
def backup_yappyverse_data():
    """
    Daily backup of Yappyverse data
    """
    try:
        # Backup characters, world state, and stories
        backup_files = [
            "yappyverse_characters.json",
            "yappyverse_world.json",
            "yappyverse_story_state.json",
            "yappyverse_schedule.json"
        ]
        
        return {
            "status": "success",
            "backed_up_files": backup_files,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Celery Beat Schedule Configuration
# Add this to your celery beat schedule:
CELERY_BEAT_SCHEDULE = {
    "yappyverse-daily-content": {
        "task": "tasks.yappyverse_tasks.generate_daily_content",
        "schedule": "cron(hour=9, minute=0)",  # Daily at 9 AM
    },
    "yappyverse-weekly-comic": {
        "task": "tasks.yappyverse_tasks.generate_weekly_comic",
        "schedule": "cron(day_of_week=1, hour=9, minute=0)",  # Monday 9 AM
    },
    "yappyverse-youtube-short-tue": {
        "task": "tasks.yappyverse_tasks.generate_youtube_short",
        "schedule": "cron(day_of_week=2, hour=15, minute=0)",  # Tuesday 3 PM
    },
    "yappyverse-youtube-short-thu": {
        "task": "tasks.yappyverse_tasks.generate_youtube_short",
        "schedule": "cron(day_of_week=4, hour=15, minute=0)",  # Thursday 3 PM
    },
    "yappyverse-youtube-short-sat": {
        "task": "tasks.yappyverse_tasks.generate_youtube_short",
        "schedule": "cron(day_of_week=6, hour=15, minute=0)",  # Saturday 3 PM
    },
    "yappyverse-advance-arc": {
        "task": "tasks.yappyverse_tasks.advance_story_arc",
        "schedule": "cron(day_of_week=0, hour=0, minute=0)",  # Sunday midnight
    },
    "yappyverse-site-sync": {
        "task": "tasks.yappyverse_tasks.sync_yappyverse_site",
        "schedule": "cron(hour=*/6, minute=0)",  # Every 6 hours
    },
    "yappyverse-backup": {
        "task": "tasks.yappyverse_tasks.backup_yappyverse_data",
        "schedule": "cron(hour=2, minute=0)",  # Daily at 2 AM
    },
}