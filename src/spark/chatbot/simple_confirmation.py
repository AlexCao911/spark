"""
简单的用户确认和数据存储系统
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..models import StoryOutline, CharacterProfile, UserIdea, ApprovedContent
from ..config import config

logger = logging.getLogger(__name__)


class SimpleConfirmationManager:
    """简单的确认管理器，用于用户确认story outline和角色后存储数据"""
    
    def __init__(self):
        # Use same path structure as ProjectManager: projects/projects/
        base_path = config.PROJECTS_STORAGE_PATH
        self.storage_path = os.path.join(base_path, "projects")
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self) -> None:
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def save_approved_content(self, user_idea: UserIdea, 
                            story_outline: StoryOutline,
                            character_profiles: List[CharacterProfile],
                            project_name: Optional[str] = None) -> Dict:
        """保存用户确认的内容"""
        try:
            # 生成项目ID和名称
            project_id = self._generate_project_id()
            if not project_name:
                project_name = story_outline.title or f"Project_{project_id[:8]}"
            
            # 创建项目目录
            project_dir = os.path.join(self.storage_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # 创建crew_input目录（Script Crew需要）
            crew_input_dir = os.path.join(project_dir, "crew_input")
            os.makedirs(crew_input_dir, exist_ok=True)
            
            # 准备保存的数据
            approved_content = {
                "project_id": project_id,
                "project_name": project_name,
                "created_at": datetime.now().isoformat(),
                "user_idea": user_idea.model_dump(),
                "story_outline": story_outline.model_dump(),
                "character_profiles": [char.model_dump() for char in character_profiles],
                "status": "approved",
                "user_confirmed": True
            }
            
            # 保存主要数据文件
            main_file = os.path.join(project_dir, "approved_content.json")
            with open(main_file, 'w', encoding='utf-8') as f:
                json.dump(approved_content, f, ensure_ascii=False, indent=2)
            
            # 创建Script Crew所需的instructions.json
            instructions_data = {
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
                    }
                },
                "story_summary": story_outline.summary,
                "character_count": len(character_profiles),
                "estimated_duration": story_outline.estimated_duration
            }
            
            instructions_file = os.path.join(crew_input_dir, "instructions.json")
            with open(instructions_file, 'w', encoding='utf-8') as f:
                json.dump(instructions_data, f, ensure_ascii=False, indent=2)
            
            # 保存crew_input所需的文件
            # story_outline.json in crew_input
            crew_story_file = os.path.join(crew_input_dir, "story_outline.json")
            with open(crew_story_file, 'w', encoding='utf-8') as f:
                json.dump(story_outline.model_dump(), f, ensure_ascii=False, indent=2)
            
            # character_profiles.json in crew_input
            crew_characters_file = os.path.join(crew_input_dir, "character_profiles.json")
            with open(crew_characters_file, 'w', encoding='utf-8') as f:
                json.dump([char.model_dump() for char in character_profiles], f, ensure_ascii=False, indent=2)
            
            # 保存角色图片信息（如果有的话）
            self._save_character_images_info(project_dir, character_profiles)
            
            # 保存story outline单独文件（便于查看）
            story_file = os.path.join(project_dir, "story_outline.json")
            with open(story_file, 'w', encoding='utf-8') as f:
                json.dump(story_outline.model_dump(), f, ensure_ascii=False, indent=2)
            
            # 保存角色信息单独文件
            characters_file = os.path.join(project_dir, "characters.json")
            with open(characters_file, 'w', encoding='utf-8') as f:
                json.dump([char.model_dump() for char in character_profiles], f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存确认内容到项目 {project_id}")
            
            return {
                "status": "success",
                "project_id": project_id,
                "project_name": project_name,
                "project_path": project_dir,
                "files_created": [
                    "approved_content.json",
                    "story_outline.json", 
                    "characters.json"
                ]
            }
            
        except Exception as e:
            logger.error(f"保存确认内容时出错: {str(e)}")
            return {
                "status": "error",
                "message": f"保存失败: {str(e)}"
            }
    
    def load_approved_content(self, project_id: str) -> Optional[Dict]:
        """加载已确认的内容"""
        try:
            project_dir = os.path.join(self.storage_path, project_id)
            main_file = os.path.join(project_dir, "approved_content.json")
            
            if not os.path.exists(main_file):
                return None
            
            with open(main_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"加载项目内容时出错: {str(e)}")
            return None
    
    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        projects = []
        
        try:
            if not os.path.exists(self.storage_path):
                return projects
            
            for item in os.listdir(self.storage_path):
                project_dir = os.path.join(self.storage_path, item)
                if os.path.isdir(project_dir):
                    main_file = os.path.join(project_dir, "approved_content.json")
                    if os.path.exists(main_file):
                        try:
                            with open(main_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                projects.append({
                                    "project_id": data.get("project_id", item),
                                    "project_name": data.get("project_name", "Unknown"),
                                    "created_at": data.get("created_at", "Unknown"),
                                    "status": data.get("status", "unknown"),
                                    "character_count": len(data.get("character_profiles", []))
                                })
                        except Exception as e:
                            logger.warning(f"无法读取项目 {item}: {str(e)}")
            
            # 按创建时间排序
            projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"列出项目时出错: {str(e)}")
        
        return projects
    
    def delete_project(self, project_id: str) -> Dict:
        """删除项目"""
        try:
            project_dir = os.path.join(self.storage_path, project_id)
            
            if not os.path.exists(project_dir):
                return {
                    "status": "error",
                    "message": "项目不存在"
                }
            
            import shutil
            shutil.rmtree(project_dir)
            
            logger.info(f"成功删除项目 {project_id}")
            
            return {
                "status": "success",
                "message": f"项目 {project_id} 已删除"
            }
            
        except Exception as e:
            logger.error(f"删除项目时出错: {str(e)}")
            return {
                "status": "error",
                "message": f"删除失败: {str(e)}"
            }
    
    def regenerate_character_image(self, project_id: str, character_name: str, 
                                 feedback: str) -> Dict:
        """重新生成角色图片（简化版）"""
        try:
            # 加载项目数据
            project_data = self.load_approved_content(project_id)
            if not project_data:
                return {
                    "status": "error",
                    "message": "项目不存在"
                }
            
            # 找到对应角色
            character_profiles = project_data.get("character_profiles", [])
            target_character = None
            char_index = -1
            
            for i, char in enumerate(character_profiles):
                if char.get("name") == character_name:
                    target_character = char
                    char_index = i
                    break
            
            if not target_character:
                return {
                    "status": "error",
                    "message": f"角色 '{character_name}' 不存在"
                }
            
            # 这里可以集成图片重新生成逻辑
            # 暂时返回成功状态，实际实现时可以调用图片生成API
            
            logger.info(f"角色 {character_name} 图片重新生成请求已记录，反馈: {feedback}")
            
            return {
                "status": "success",
                "message": f"角色 {character_name} 的图片重新生成请求已提交",
                "character_name": character_name,
                "feedback": feedback
            }
            
        except Exception as e:
            logger.error(f"重新生成角色图片时出错: {str(e)}")
            return {
                "status": "error",
                "message": f"重新生成失败: {str(e)}"
            }
    
    def _generate_project_id(self) -> str:
        """生成项目ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _save_character_images_info(self, project_dir: str, 
                                  character_profiles: List[CharacterProfile]) -> None:
        """保存角色图片信息"""
        try:
            images_info = []
            for char in character_profiles:
                if char.image_url:
                    images_info.append({
                        "character_name": char.name,
                        "image_url": char.image_url,
                        "visual_tags": char.visual_consistency_tags
                    })
            
            if images_info:
                images_file = os.path.join(project_dir, "character_images.json")
                with open(images_file, 'w', encoding='utf-8') as f:
                    json.dump(images_info, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            logger.warning(f"保存角色图片信息时出错: {str(e)}")


# 全局实例
confirmation_manager = SimpleConfirmationManager()