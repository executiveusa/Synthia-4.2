"""
🛠️ RALPHY CLI SKILL 🛠️

Integrates Ralphy CLI tool as an agent skill for code generation
Ralphy: AI-powered CLI for Next.js development
"""

import os
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from .registry import Skill, SkillCategory, AutomationLevel

logger = logging.getLogger(__name__)


@dataclass
class RalphyConfig:
    """Configuration for Ralphy CLI"""
    project_path: str = "./generated"
    framework: str = "nextjs"
    styling: str = "tailwind"
    components: str = "shadcn"


class RalphySkill(Skill):
    """
    Ralphy CLI Integration Skill
    
    Uses Ralphy (https://github.com/michaelshimeles/ralphy)
    to generate Next.js applications with modern stack:
    - Next.js 14+ (App Router)
    - TypeScript
    - Tailwind CSS
    - shadcn/ui components
    - AI-powered code generation
    """
    
    skill_id = "ralphy-cli-generator"
    display_name = "Ralphy CLI Generator"
    category = SkillCategory.DEVELOPMENT
    description = "Generate production-ready Next.js applications using Ralphy CLI"
    when_to_use = [
        "Creating new Next.js projects from scratch",
        "Generating full-stack applications quickly",
        "Building with modern React stack (Next.js 14+, TypeScript, Tailwind)",
        "Need AI-powered component generation",
        "Want shadcn/ui component library integration"
    ]
    
    inputs = [
        "project_name",
        "project_description",
        "features",
        "pages_needed",
        "styling_preferences"
    ]
    
    outputs = [
        "generated_project_path",
        "project_structure",
        "installed_dependencies",
        "setup_instructions"
    ]
    
    automation_level = AutomationLevel.FULL
    approval_required = False
    
    def __init__(self):
        self.ralphy_path = self._find_ralphy()
        self.config = RalphyConfig()
    
    def _find_ralphy(self) -> Optional[str]:
        """Find Ralphy CLI installation"""
        # Check if ralphy is installed globally
        try:
            result = subprocess.run(
                ["which", "ralphy"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Check local installation
        local_paths = [
            "./integrations/ralphy/bin/ralphy",
            "./integrations/ralphy/dist/ralphy",
            "./node_modules/.bin/ralphy",
        ]
        
        for path in local_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # Check if we can use npx
        try:
            result = subprocess.run(
                ["npx", "--yes", "ralphy", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return "npx ralphy"
        except Exception:
            pass
        
        return None
    
    def is_available(self) -> bool:
        """Check if Ralphy is available"""
        return self.ralphy_path is not None
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Ralphy skill
        
        Args:
            context: Contains:
                - project_name: Name of the project
                - description: Project description
                - features: List of features needed
                - output_dir: Where to generate (default: ./generated)
        
        Returns:
            Result dict with generation status
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Ralphy CLI not found. Install with: npm install -g ralphy",
                "fallback": "Use web-artifacts-builder-plus skill instead"
            }
        
        project_name = context.get("project_name", "my-app")
        description = context.get("description", "A Next.js application")
        features = context.get("features", [])
        output_dir = context.get("output_dir", "./generated")
        
        # Sanitize project name
        project_name = self._sanitize_project_name(project_name)
        
        # Create output directory
        project_path = os.path.join(output_dir, project_name)
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Build Ralphy command
            cmd = self._build_command(project_name, description, features, output_dir)
            
            logger.info(f"Running Ralphy: {' '.join(cmd)}")
            
            # Execute Ralphy
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=output_dir,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Get project structure
                structure = self._get_project_structure(project_path)
                
                return {
                    "success": True,
                    "project_name": project_name,
                    "project_path": project_path,
                    "structure": structure,
                    "stdout": result.stdout,
                    "message": f"Successfully generated {project_name} with Ralphy",
                    "next_steps": [
                        f"cd {project_path}",
                        "npm install",
                        "npm run dev"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout,
                    "message": "Ralphy generation failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Ralphy command timed out after 5 minutes",
                "message": "Generation took too long"
            }
        except Exception as e:
            logger.error(f"Ralphy execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error executing Ralphy"
            }
    
    def _build_command(self, project_name: str, description: str, 
                      features: List[str], output_dir: str) -> List[str]:
        """Build Ralphy CLI command"""
        cmd = ["npx", "--yes", "ralphy", "create", project_name]
        
        # Add options
        if description:
            cmd.extend(["--description", description])
        
        # Add features if supported
        if features:
            # Map features to Ralphy flags
            feature_map = {
                "auth": "--auth",
                "database": "--db",
                "stripe": "--stripe",
                "resend": "--resend",
                "upload": "--upload"
            }
            
            for feature in features:
                if feature.lower() in feature_map:
                    cmd.append(feature_map[feature.lower()])
        
        return cmd
    
    def _sanitize_project_name(self, name: str) -> str:
        """Sanitize project name for filesystem"""
        # Remove special characters
        sanitized = "".join(c for c in name if c.isalnum() or c in "-_")
        # Ensure starts with letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "app-" + sanitized
        # Default if empty
        if not sanitized:
            sanitized = "my-app"
        return sanitized.lower()
    
    def _get_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Get generated project structure"""
        structure = {
            "root": project_path,
            "files": [],
            "directories": []
        }
        
        try:
            for item in os.listdir(project_path):
                item_path = os.path.join(project_path, item)
                if os.path.isdir(item_path):
                    structure["directories"].append(item)
                else:
                    structure["files"].append(item)
        except Exception:
            pass
        
        return structure
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information"""
        return {
            "skill_id": self.skill_id,
            "display_name": self.display_name,
            "available": self.is_available(),
            "ralphy_path": self.ralphy_path,
            "config": {
                "framework": self.config.framework,
                "styling": self.config.styling,
                "components": self.config.components
            },
            "capabilities": [
                "Next.js 14+ generation",
                "TypeScript support",
                "Tailwind CSS integration",
                "shadcn/ui components",
                "AI-powered scaffolding"
            ]
        }


# Singleton instance
_ralphy_skill: Optional[RalphySkill] = None


def get_ralphy_skill() -> RalphySkill:
    """Get Ralphy skill singleton"""
    global _ralphy_skill
    if _ralphy_skill is None:
        _ralphy_skill = RalphySkill()
    return _ralphy_skill


# Register skill
from .registry import register_skill

ralphy_skill = get_ralphy_skill()
register_skill(ralphy_skill)