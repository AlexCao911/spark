"""
Project management system for Spark AI Video Generation Pipeline.
Handles the complete flow from chatbot generation to crew processing.
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import UserIdea, StoryOutline, CharacterProfile, ApprovedContent
from .storage import ProjectStorage
from .config import config

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages the complete project lifecycle from chatbot to crews."""
    
    def __init__(self, base_path: str = None):
        self.storage = ProjectStorage(base_path)
        self.base_path = Path(base_path or "projects")
    
    def create_project_from_chatbot(
        self, 
        user_idea: UserIdea,
        character_profiles: List[CharacterProfile],
        story_outline: StoryOutline,
        project_name: str = None
    ) -> str:
        """Create a complete project from chatbot-generated content."""
        try:
            # Create project
            project_id = self.storage.create_project(user_idea, project_name)
            project_dir = self.storage.projects_dir / project_id
            
            # Save all chatbot-generated content
            self._save_chatbot_content(project_id, user_idea, character_profiles, story_outline)
            
            # Create approved content structure for crews
            approved_content = self._create_approved_content(user_idea, character_profiles, story_outline)
            self._save_approved_content(project_id, approved_content)
            
            # Update project status
            self.storage._update_project_status(project_id, "chatbot_complete")
            
            logger.info(f"Created complete project {project_id} from chatbot content")
            return project_id
            
        except Exception as e:
            logger.error(f"Error creating project from chatbot: {e}")
            raise
    
    def _save_chatbot_content(
        self,
        project_id: str,
        user_idea: UserIdea,
        character_profiles: List[CharacterProfile],
        story_outline: StoryOutline
    ):
        """Save all chatbot-generated content to project."""
        project_dir = self.storage.projects_dir / project_id
        
        # Save user idea (already saved by storage.create_project)
        
        # Save story outline
        self.storage.save_story_outline(project_id, story_outline)
        
        # Save character profiles
        self.storage.save_character_profiles(project_id, character_profiles)
        
        # Create summary for easy reference
        self._create_chatbot_summary(project_id, user_idea, character_profiles, story_outline)
    
    def _create_approved_content(
        self,
        user_idea: UserIdea,
        character_profiles: List[CharacterProfile],
        story_outline: StoryOutline
    ) -> ApprovedContent:
        """Create ApprovedContent structure for crews."""
        return ApprovedContent(
            story_outline=story_outline,
            character_profiles=character_profiles,
            user_confirmed=True  # Assume user has confirmed through chatbot
        )
    
    def _save_approved_content(self, project_id: str, approved_content: ApprovedContent):
        """Save approved content for crew consumption."""
        project_dir = self.storage.projects_dir / project_id
        
        # Save approved content as JSON
        approved_path = project_dir / "approved_content.json"
        self.storage._save_json(approved_path, approved_content.model_dump())
        
        # Create crew input directory
        crew_input_dir = project_dir / "crew_input"
        crew_input_dir.mkdir(exist_ok=True)
        
        # Save individual components for crew processing
        self.storage._save_json(
            crew_input_dir / "story_outline.json", 
            approved_content.story_outline.model_dump()
        )
        
        self.storage._save_json(
            crew_input_dir / "character_profiles.json",
            [profile.model_dump() for profile in approved_content.character_profiles]
        )
        
        # Create crew instructions
        self._create_crew_instructions(project_id, approved_content)
    
    def _create_crew_instructions(self, project_id: str, approved_content: ApprovedContent):
        """Create instructions file for script crew."""
        project_dir = self.storage.projects_dir / project_id
        crew_input_dir = project_dir / "crew_input"
        
        instructions = {
            "project_id": project_id,
            "instructions": {
                "script_crew": {
                    "input_files": {
                        "story_outline": "crew_input/story_outline.json",
                        "character_profiles": "crew_input/character_profiles.json"
                    },
                    "output_directory": "scripts",
                    "tasks": [
                        "Expand story outline into detailed narrative",
                        "Break story into individual shots",
                        "Generate VEO3-optimized prompts with character references"
                    ]
                },
                "maker_crew": {
                    "input_files": {
                        "video_prompts": "scripts/video_prompts.json",
                        "character_images": "characters/"
                    },
                    "output_directory": "videos",
                    "tasks": [
                        "Generate video clips from prompts",
                        "Ensure visual consistency using character images",
                        "Assemble final video"
                    ]
                }
            },
            "story_summary": approved_content.story_outline.summary,
            "character_count": len(approved_content.character_profiles),
            "estimated_duration": approved_content.story_outline.estimated_duration
        }
        
        self.storage._save_json(crew_input_dir / "instructions.json", instructions)
    
    def _create_chatbot_summary(
        self,
        project_id: str,
        user_idea: UserIdea,
        character_profiles: List[CharacterProfile],
        story_outline: StoryOutline
    ):
        """Create a human-readable summary of chatbot results."""
        project_dir = self.storage.projects_dir / project_id
        
        summary_content = f"""# Spark AI - Chatbot Generated Content Summary

## Project Information
- Project ID: {project_id}
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Status: Chatbot Complete

## User Idea
- **Theme**: {user_idea.theme}
- **Genre**: {user_idea.genre}
- **Target Audience**: {user_idea.target_audience}
- **Duration**: {user_idea.duration_preference} seconds
- **Visual Style**: {user_idea.visual_style}
- **Mood**: {user_idea.mood}

### Characters ({len(user_idea.basic_characters)})
"""
        
        for i, char_desc in enumerate(user_idea.basic_characters, 1):
            summary_content += f"{i}. {char_desc}\n"
        
        summary_content += f"""
### Plot Points ({len(user_idea.plot_points)})
"""
        
        for i, plot in enumerate(user_idea.plot_points, 1):
            summary_content += f"{i}. {plot}\n"
        
        summary_content += f"""

## Generated Story Outline
- **Title**: {story_outline.title}
- **Summary**: {story_outline.summary}
- **Estimated Duration**: {story_outline.estimated_duration} seconds

## Character Profiles ({len(character_profiles)})
"""
        
        for i, profile in enumerate(character_profiles, 1):
            image_status = "✅ Generated" if profile.image_url else "❌ Failed"
            summary_content += f"""
### {i}. {profile.name} ({profile.role})
- **Appearance**: {profile.appearance}
- **Personality**: {profile.personality}
- **Image**: {image_status}
- **Image URL**: {profile.image_url or 'None'}
"""
        
        summary_content += f"""

## Next Steps
1. **Script Crew**: Expand story and generate video prompts
2. **Maker Crew**: Generate video clips and assemble final video

## File Structure
```
{project_id}/
├── project.json              # Project metadata
├── user_idea.json           # Original user idea
├── story_outline.json       # Generated story outline  
├── characters/              # Character profiles and images
├── crew_input/             # Input files for crews
│   ├── instructions.json   # Processing instructions
│   ├── story_outline.json  # Story for crew processing
│   └── character_profiles.json # Characters for crew processing
├── scripts/                # Script crew outputs
├── assets/                 # Additional assets
└── videos/                 # Final video outputs
```
"""
        
        summary_path = project_dir / "CHATBOT_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
    
    def load_project_for_crew(self, project_id: str, crew_type: str = "script") -> Dict[str, Any]:
        """Load project data for crew processing."""
        try:
            project_dir = self.storage.projects_dir / project_id
            if not project_dir.exists():
                raise FileNotFoundError(f"Project {project_id} not found")
            
            crew_input_dir = project_dir / "crew_input"
            
            # Load instructions
            instructions_path = crew_input_dir / "instructions.json"
            if not instructions_path.exists():
                raise FileNotFoundError(f"Instructions not found for project {project_id}")
            
            with open(instructions_path, 'r', encoding='utf-8') as f:
                instructions = json.load(f)
            
            # Load crew-specific data
            crew_data = {
                "project_id": project_id,
                "instructions": instructions,
                "project_dir": str(project_dir)
            }
            
            if crew_type == "script":
                # Load approved content
                approved_content_path = project_dir / "approved_content.json"
                if approved_content_path.exists():
                    with open(approved_content_path, 'r', encoding='utf-8') as f:
                        approved_content_data = json.load(f)
                    crew_data["approved_content"] = approved_content_data
                
                # Load story outline
                story_path = crew_input_dir / "story_outline.json"
                if story_path.exists():
                    with open(story_path, 'r', encoding='utf-8') as f:
                        crew_data["story_outline"] = json.load(f)
                
                # Load character profiles
                characters_path = crew_input_dir / "character_profiles.json"
                if characters_path.exists():
                    with open(characters_path, 'r', encoding='utf-8') as f:
                        crew_data["character_profiles"] = json.load(f)
            
            logger.info(f"Loaded project {project_id} for {crew_type} crew")
            return crew_data
            
        except Exception as e:
            logger.error(f"Error loading project for crew: {e}")
            raise
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get current project status and progress."""
        try:
            project_dir = self.storage.projects_dir / project_id
            project_file = project_dir / "project.json"
            
            if not project_file.exists():
                return {"error": "Project not found"}
            
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Check what files exist
            status = {
                "project_id": project_id,
                "status": project_data.get("status", "unknown"),
                "created_at": project_data.get("created_at"),
                "updated_at": project_data.get("updated_at"),
                "files": {
                    "user_idea": (project_dir / "user_idea.json").exists(),
                    "story_outline": (project_dir / "story_outline.json").exists(),
                    "character_profiles": (project_dir / "characters").exists(),
                    "approved_content": (project_dir / "approved_content.json").exists(),
                    "crew_input": (project_dir / "crew_input").exists(),
                    "scripts": (project_dir / "scripts").exists(),
                    "videos": (project_dir / "videos").exists()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return {"error": str(e)}
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with basic information."""
        projects = []
        
        try:
            for project_dir in self.storage.projects_dir.iterdir():
                if project_dir.is_dir():
                    project_file = project_dir / "project.json"
                    if project_file.exists():
                        with open(project_file, 'r', encoding='utf-8') as f:
                            project_data = json.load(f)
                        
                        projects.append({
                            "project_id": project_data["project_id"],
                            "project_name": project_data["project_name"],
                            "status": project_data.get("status", "unknown"),
                            "created_at": project_data.get("created_at"),
                            "theme": project_data.get("user_idea", {}).get("theme", "Unknown")
                        })
            
            return sorted(projects, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []


# Global project manager instance
project_manager = ProjectManager() 