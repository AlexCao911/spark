"""
Data storage and persistence system for Spark AI Video Generation Pipeline.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .models import UserIdea, StoryOutline, CharacterProfile
from .config import config

logger = logging.getLogger(__name__)


class ProjectStorage:
    """Manages storage and retrieval of video generation projects."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "projects")
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.projects_dir = self.base_path / "projects"
        self.assets_dir = self.base_path / "assets"
        self.exports_dir = self.base_path / "exports"
        
        for dir_path in [self.projects_dir, self.assets_dir, self.exports_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def create_project(self, user_idea: UserIdea, project_name: str = None) -> str:
        """Create a new project and return project ID."""
        project_id = str(uuid.uuid4())
        project_name = project_name or f"Video_Project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Create project structure
        (project_dir / "assets").mkdir(exist_ok=True)
        (project_dir / "characters").mkdir(exist_ok=True)
        (project_dir / "scripts").mkdir(exist_ok=True)
        (project_dir / "videos").mkdir(exist_ok=True)
        
        # Save project metadata
        project_metadata = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "created",
            "user_idea": user_idea.model_dump()
        }
        
        self._save_json(project_dir / "project.json", project_metadata)
        
        # Save user idea
        self._save_json(project_dir / "user_idea.json", user_idea.model_dump())
        
        logger.info(f"Created project {project_id}: {project_name}")
        return project_id
    
    def save_story_outline(self, project_id: str, story_outline: StoryOutline) -> bool:
        """Save story outline to project."""
        try:
            project_dir = self.projects_dir / project_id
            if not project_dir.exists():
                logger.error(f"Project {project_id} not found")
                return False
            
            # Save story outline
            outline_path = project_dir / "story_outline.json"
            self._save_json(outline_path, story_outline.model_dump())
            
            # Update project metadata
            self._update_project_status(project_id, "story_generated")
            
            logger.info(f"Saved story outline for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving story outline: {e}")
            return False
    
    def save_character_profiles(self, project_id: str, character_profiles: List[CharacterProfile]) -> bool:
        """Save character profiles to project."""
        try:
            project_dir = self.projects_dir / project_id
            if not project_dir.exists():
                logger.error(f"Project {project_id} not found")
                return False
            
            characters_dir = project_dir / "characters"
            
            # Save individual character profiles
            for i, profile in enumerate(character_profiles):
                character_file = characters_dir / f"character_{i+1}_{profile.name}.json"
                self._save_json(character_file, profile.model_dump())
                
                # Download and save character image if URL exists
                if profile.image_url:
                    self._save_character_image(project_id, profile.name, profile.image_url)
            
            # Save characters summary
            characters_summary = {
                "character_count": len(character_profiles),
                "characters": [profile.model_dump() for profile in character_profiles],
                "generated_at": datetime.now().isoformat()
            }
            self._save_json(characters_dir / "characters_summary.json", characters_summary)
            
            # Update project metadata
            self._update_project_status(project_id, "characters_generated")
            
            logger.info(f"Saved {len(character_profiles)} character profiles for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving character profiles: {e}")
            return False
    
    def save_conversation_history(self, project_id: str, conversation_history: List[Dict]) -> bool:
        """Save conversation history to project."""
        try:
            project_dir = self.projects_dir / project_id
            if not project_dir.exists():
                logger.error(f"Project {project_id} not found")
                return False
            
            conversation_data = {
                "conversation_history": conversation_history,
                "saved_at": datetime.now().isoformat(),
                "message_count": len(conversation_history)
            }
            
            conversation_path = project_dir / "conversation.json"
            self._save_json(conversation_path, conversation_data)
            
            logger.info(f"Saved conversation history for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
            return False
    
    def load_project(self, project_id: str) -> Optional[Dict]:
        """Load complete project data."""
        try:
            project_dir = self.projects_dir / project_id
            if not project_dir.exists():
                logger.error(f"Project {project_id} not found")
                return None
            
            # Load project metadata
            project_metadata = self._load_json(project_dir / "project.json")
            if not project_metadata:
                return None
            
            # Load additional data
            project_data = project_metadata.copy()
            
            # Load user idea
            user_idea_data = self._load_json(project_dir / "user_idea.json")
            if user_idea_data:
                project_data["user_idea"] = user_idea_data
            
            # Load story outline
            story_outline_data = self._load_json(project_dir / "story_outline.json")
            if story_outline_data:
                project_data["story_outline"] = story_outline_data
            
            # Load character profiles
            characters_summary = self._load_json(project_dir / "characters" / "characters_summary.json")
            if characters_summary:
                project_data["character_profiles"] = characters_summary
            
            # Load conversation history
            conversation_data = self._load_json(project_dir / "conversation.json")
            if conversation_data:
                project_data["conversation_history"] = conversation_data
            
            return project_data
            
        except Exception as e:
            logger.error(f"Error loading project {project_id}: {e}")
            return None
    
    def list_projects(self) -> List[Dict]:
        """List all projects with basic metadata."""
        projects = []
        
        try:
            for project_dir in self.projects_dir.iterdir():
                if project_dir.is_dir():
                    metadata_file = project_dir / "project.json"
                    if metadata_file.exists():
                        metadata = self._load_json(metadata_file)
                        if metadata:
                            projects.append({
                                "project_id": metadata.get("project_id"),
                                "project_name": metadata.get("project_name"),
                                "created_at": metadata.get("created_at"),
                                "updated_at": metadata.get("updated_at"),
                                "status": metadata.get("status")
                            })
        
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
        
        return sorted(projects, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its data."""
        try:
            project_dir = self.projects_dir / project_id
            if not project_dir.exists():
                logger.error(f"Project {project_id} not found")
                return False
            
            import shutil
            shutil.rmtree(project_dir)
            
            logger.info(f"Deleted project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False
    
    def export_project(self, project_id: str, export_format: str = "json") -> Optional[str]:
        """Export project data to a file."""
        try:
            project_data = self.load_project(project_id)
            if not project_data:
                return None
            
            export_filename = f"project_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            export_path = self.exports_dir / export_filename
            
            if export_format == "json":
                self._save_json(export_path, project_data)
            else:
                logger.error(f"Unsupported export format: {export_format}")
                return None
            
            logger.info(f"Exported project {project_id} to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Error exporting project {project_id}: {e}")
            return None
    
    def _save_json(self, file_path: Path, data: Dict) -> bool:
        """Save data as JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            return False
    
    def _load_json(self, file_path: Path) -> Optional[Dict]:
        """Load data from JSON file."""
        try:
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
            return None
    
    def _update_project_status(self, project_id: str, status: str) -> bool:
        """Update project status and timestamp."""
        try:
            project_dir = self.projects_dir / project_id
            metadata_file = project_dir / "project.json"
            
            metadata = self._load_json(metadata_file)
            if metadata:
                metadata["status"] = status
                metadata["updated_at"] = datetime.now().isoformat()
                return self._save_json(metadata_file, metadata)
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return False
    
    def _save_character_image(self, project_id: str, character_name: str, image_url: str) -> bool:
        """Download and save character image locally."""
        try:
            import requests
            from urllib.parse import urlparse
            
            project_dir = self.projects_dir / project_id
            assets_dir = project_dir / "assets"
            
            # Download image
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # Determine file extension
                parsed_url = urlparse(image_url)
                file_ext = ".png"  # Default to PNG
                if "." in parsed_url.path:
                    file_ext = "." + parsed_url.path.split(".")[-1].split("?")[0]
                
                # Save image
                image_filename = f"character_{character_name}{file_ext}"
                image_path = assets_dir / image_filename
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Saved character image: {image_path}")
                return True
            else:
                logger.warning(f"Failed to download image from {image_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving character image: {e}")
            return False


class SessionStorage:
    """Manages temporary session data during active conversations."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new session."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "conversation_history": [],
            "user_idea": None,
            "story_outline": None,
            "character_profiles": [],
            "current_step": "conversation"
        }
        
        return session_id
    
    def update_session(self, session_id: str, data: Dict) -> bool:
        """Update session data."""
        if session_id not in self.sessions:
            return False
        
        self.sessions[session_id].update(data)
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
        return True
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data."""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def save_session_to_project(self, session_id: str, project_storage: ProjectStorage) -> Optional[str]:
        """Save session data as a permanent project."""
        session_data = self.get_session(session_id)
        if not session_data:
            return None
        
        try:
            # Create UserIdea from session data
            if session_data.get("user_idea"):
                user_idea = UserIdea(**session_data["user_idea"])
                project_id = project_storage.create_project(user_idea)
                
                # Save additional data
                if session_data.get("story_outline"):
                    story_outline = StoryOutline(**session_data["story_outline"])
                    project_storage.save_story_outline(project_id, story_outline)
                
                if session_data.get("character_profiles"):
                    character_profiles = [
                        CharacterProfile(**profile) 
                        for profile in session_data["character_profiles"]
                    ]
                    project_storage.save_character_profiles(project_id, character_profiles)
                
                if session_data.get("conversation_history"):
                    project_storage.save_conversation_history(project_id, session_data["conversation_history"])
                
                return project_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error saving session to project: {e}")
            return None


# Global storage instances
project_storage = ProjectStorage()
session_storage = SessionStorage()