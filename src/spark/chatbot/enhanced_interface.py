"""
Enhanced chatbot interface with storage integration.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from ..storage import project_storage, session_storage
from .core import ChatbotCore
from .idea_structurer import IdeaStructurer
from .character_generator import CharacterProfileGenerator
from ..models import UserIdea, StoryOutline, CharacterProfile

logger = logging.getLogger(__name__)


class EnhancedChatbotInterface:
    """Enhanced chatbot interface with persistent storage."""
    
    def __init__(self):
        self.chatbot_core = ChatbotCore()
        self.idea_structurer = IdeaStructurer()
        self.character_generator = CharacterProfileGenerator()
        self.current_session_id = None
        self.current_project_id = None
    
    def start_new_session(self) -> str:
        """Start a new conversation session."""
        self.current_session_id = session_storage.create_session()
        self.chatbot_core.reset_conversation()
        
        logger.info(f"Started new session: {self.current_session_id}")
        return self.current_session_id
    
    def continue_conversation(self, message: str) -> Dict[str, Any]:
        """Continue conversation and auto-save progress."""
        if not self.current_session_id:
            self.start_new_session()
        
        try:
            # Get response from chatbot
            if not session_storage.get_session(self.current_session_id).get("conversation_history"):
                response_data = self.chatbot_core.engage_user(message)
            else:
                response_data = self.chatbot_core.continue_conversation(message)
            
            # Update session with conversation history
            conversation_history = self.chatbot_core.get_conversation_history()
            session_storage.update_session(self.current_session_id, {
                "conversation_history": conversation_history,
                "current_step": "conversation"
            })
            
            # Add storage info to response
            response_data["session_id"] = self.current_session_id
            response_data["auto_saved"] = True
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            return {
                "status": "error",
                "response": f"对话出错: {str(e)}",
                "session_id": self.current_session_id,
                "auto_saved": False
            }
    
    def structure_current_idea(self) -> Dict[str, Any]:
        """Structure the current conversation and save to session."""
        if not self.current_session_id:
            return {"error": "没有活动会话"}
        
        try:
            session_data = session_storage.get_session(self.current_session_id)
            if not session_data or not session_data.get("conversation_history"):
                return {"error": "没有对话历史可以结构化"}
            
            # Structure the idea
            user_idea = self.idea_structurer.structure_conversation(
                session_data["conversation_history"]
            )
            
            if user_idea:
                # Save to session
                session_storage.update_session(self.current_session_id, {
                    "user_idea": user_idea.model_dump(),
                    "current_step": "idea_structured"
                })
                
                # Validate completeness
                validation = self.idea_structurer.validate_idea_completeness(user_idea)
                
                result = {
                    "status": "success",
                    "user_idea": user_idea.model_dump(),
                    "validation": validation,
                    "session_id": self.current_session_id,
                    "auto_saved": True
                }
                
                logger.info(f"Structured idea for session {self.current_session_id}")
                return result
            else:
                return {"error": "结构化失败"}
                
        except Exception as e:
            logger.error(f"Error structuring idea: {e}")
            return {"error": f"结构化错误: {str(e)}"}
    
    def generate_story_outline(self) -> Dict[str, Any]:
        """Generate story outline and save to session."""
        if not self.current_session_id:
            return {"error": "没有活动会话"}
        
        try:
            session_data = session_storage.get_session(self.current_session_id)
            if not session_data or not session_data.get("user_idea"):
                return {"error": "请先结构化创意"}
            
            # Create UserIdea object
            user_idea = UserIdea(**session_data["user_idea"])
            
            # Generate story outline
            story_outline = self.idea_structurer.generate_story_outline(user_idea)
            
            if story_outline:
                # Save to session
                session_storage.update_session(self.current_session_id, {
                    "story_outline": story_outline.model_dump(),
                    "current_step": "story_generated"
                })
                
                result = {
                    "status": "success",
                    "story_outline": story_outline.model_dump(),
                    "session_id": self.current_session_id,
                    "auto_saved": True
                }
                
                logger.info(f"Generated story outline for session {self.current_session_id}")
                return result
            else:
                return {"error": "故事大纲生成失败"}
                
        except Exception as e:
            logger.error(f"Error generating story outline: {e}")
            return {"error": f"故事生成错误: {str(e)}"}
    
    def generate_character_profiles(self) -> Dict[str, Any]:
        """Generate character profiles and save to session."""
        if not self.current_session_id:
            return {"error": "没有活动会话"}
        
        try:
            session_data = session_storage.get_session(self.current_session_id)
            if not session_data or not session_data.get("user_idea"):
                return {"error": "请先结构化创意"}
            
            # Create UserIdea object
            user_idea = UserIdea(**session_data["user_idea"])
            
            if not user_idea.basic_characters:
                return {"error": "创意中没有角色信息"}
            
            # Generate character profiles
            character_profiles = self.character_generator.generate_complete_character_profiles(
                user_idea.basic_characters,
                user_idea
            )
            
            if character_profiles:
                # Save to session
                profiles_data = [profile.model_dump() for profile in character_profiles]
                session_storage.update_session(self.current_session_id, {
                    "character_profiles": profiles_data,
                    "current_step": "characters_generated"
                })
                
                result = {
                    "status": "success",
                    "character_profiles": profiles_data,
                    "character_count": len(character_profiles),
                    "session_id": self.current_session_id,
                    "auto_saved": True
                }
                
                logger.info(f"Generated {len(character_profiles)} character profiles for session {self.current_session_id}")
                return result
            else:
                return {"error": "角色档案生成失败"}
                
        except Exception as e:
            logger.error(f"Error generating character profiles: {e}")
            return {"error": f"角色生成错误: {str(e)}"}
    
    def save_as_project(self, project_name: str = None) -> Dict[str, Any]:
        """Save current session as a permanent project."""
        if not self.current_session_id:
            return {"error": "没有活动会话"}
        
        try:
            # Save session to project
            project_id = session_storage.save_session_to_project(
                self.current_session_id, 
                project_storage
            )
            
            if project_id:
                self.current_project_id = project_id
                
                # Update project name if provided
                if project_name:
                    project_data = project_storage.load_project(project_id)
                    if project_data:
                        project_data["project_name"] = project_name
                        project_storage._save_json(
                            project_storage.projects_dir / project_id / "project.json",
                            project_data
                        )
                
                result = {
                    "status": "success",
                    "project_id": project_id,
                    "project_name": project_name or f"Project_{project_id[:8]}",
                    "message": "项目保存成功"
                }
                
                logger.info(f"Saved session {self.current_session_id} as project {project_id}")
                return result
            else:
                return {"error": "项目保存失败"}
                
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            return {"error": f"保存错误: {str(e)}"}
    
    def load_project(self, project_id: str) -> Dict[str, Any]:
        """Load an existing project."""
        try:
            project_data = project_storage.load_project(project_id)
            if not project_data:
                return {"error": f"项目 {project_id} 不存在"}
            
            self.current_project_id = project_id
            
            # Create new session from project data
            self.current_session_id = session_storage.create_session()
            
            # Load data into session
            session_update = {
                "current_step": "loaded"
            }
            
            if project_data.get("user_idea"):
                session_update["user_idea"] = project_data["user_idea"]
            
            if project_data.get("story_outline"):
                session_update["story_outline"] = project_data["story_outline"]
            
            if project_data.get("character_profiles"):
                session_update["character_profiles"] = project_data["character_profiles"].get("characters", [])
            
            if project_data.get("conversation_history"):
                session_update["conversation_history"] = project_data["conversation_history"].get("conversation_history", [])
            
            session_storage.update_session(self.current_session_id, session_update)
            
            result = {
                "status": "success",
                "project_data": project_data,
                "session_id": self.current_session_id,
                "message": f"项目 {project_data.get('project_name', project_id)} 加载成功"
            }
            
            logger.info(f"Loaded project {project_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return {"error": f"加载错误: {str(e)}"}
    
    def list_projects(self) -> List[Dict]:
        """List all available projects."""
        try:
            return project_storage.list_projects()
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []
    
    def export_current_project(self, export_format: str = "json") -> Dict[str, Any]:
        """Export current project to file."""
        if not self.current_project_id:
            return {"error": "没有当前项目"}
        
        try:
            export_path = project_storage.export_project(self.current_project_id, export_format)
            if export_path:
                return {
                    "status": "success",
                    "export_path": export_path,
                    "message": f"项目导出成功: {export_path}"
                }
            else:
                return {"error": "导出失败"}
                
        except Exception as e:
            logger.error(f"Error exporting project: {e}")
            return {"error": f"导出错误: {str(e)}"}
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status and progress."""
        if not self.current_session_id:
            return {"status": "no_session"}
        
        session_data = session_storage.get_session(self.current_session_id)
        if not session_data:
            return {"status": "session_not_found"}
        
        return {
            "status": "active",
            "session_id": self.current_session_id,
            "project_id": self.current_project_id,
            "current_step": session_data.get("current_step", "conversation"),
            "has_conversation": bool(session_data.get("conversation_history")),
            "has_user_idea": bool(session_data.get("user_idea")),
            "has_story_outline": bool(session_data.get("story_outline")),
            "has_character_profiles": bool(session_data.get("character_profiles")),
            "created_at": session_data.get("created_at"),
            "updated_at": session_data.get("updated_at")
        }