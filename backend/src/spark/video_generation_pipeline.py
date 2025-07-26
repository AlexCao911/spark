"""
Complete Video Generation Pipeline
完整的视频生成管道，整合所有组件
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from .crews.script.src.script.crew import ScriptGenerationCrew
from .crews.maker.src.maker.crew import VideoProductionCrew
from .project_manager import project_manager

logger = logging.getLogger(__name__)


class VideoGenerationPipeline:
    """完整的视频生成管道"""
    
    def __init__(self):
        """初始化管道"""
        self.script_crew = ScriptGenerationCrew()
        self.video_crew = VideoProductionCrew()
        
        logger.info("Video generation pipeline initialized")
    
    def generate_complete_video(self, project_id: str) -> Dict[str, Any]:
        """
        生成完整视频的主要方法
        
        Args:
            project_id: 项目ID
            
        Returns:
            包含所有处理结果的字典
        """
        try:
            logger.info(f"Starting complete video generation for project {project_id}")
            
            # 验证项目存在且已确认
            if not self._validate_project(project_id):
                raise Exception(f"Project {project_id} not found or not approved")
            
            # 阶段1: 脚本生成 (如果还没有)
            script_result = self._ensure_script_generated(project_id)
            
            # 阶段2: 视频制作
            video_result = self._generate_video(project_id)
            
            # 整合结果
            final_result = {
                "project_id": project_id,
                "pipeline_status": "completed",
                "script_generation": script_result,
                "video_production": video_result,
                "final_videos": video_result.get("final_videos", {}),
                "thumbnail": video_result.get("thumbnail", ""),
                "metadata": {
                    "total_duration": video_result.get("metadata", {}).get("final_duration", 0),
                    "total_clips": video_result.get("metadata", {}).get("total_clips", 0),
                    "successful_clips": video_result.get("metadata", {}).get("successful_clips", 0)
                }
            }
            
            # 保存最终结果
            self._save_pipeline_result(project_id, final_result)
            
            logger.info(f"Complete video generation finished for project {project_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"Video generation pipeline failed for project {project_id}: {e}")
            error_result = {
                "project_id": project_id,
                "pipeline_status": "failed",
                "error": str(e)
            }
            self._save_pipeline_result(project_id, error_result)
            raise
    
    def _validate_project(self, project_id: str) -> bool:
        """验证项目是否存在且已确认"""
        try:
            project_dir = Path("projects/projects") / project_id
            if not project_dir.exists():
                return False
            
            # 检查是否有已确认的内容
            approved_file = project_dir / "approved_content.json"
            if not approved_file.exists():
                return False
            
            with open(approved_file, 'r', encoding='utf-8') as f:
                approved_data = json.load(f)
                return approved_data.get("user_confirmed", False)
                
        except Exception as e:
            logger.error(f"Error validating project {project_id}: {e}")
            return False
    
    def _ensure_script_generated(self, project_id: str) -> Dict[str, Any]:
        """确保脚本已生成，如果没有则生成"""
        try:
            # 检查是否已有脚本
            project_dir = Path("projects/projects") / project_id
            scripts_dir = project_dir / "scripts"
            
            if (scripts_dir.exists() and 
                (scripts_dir / "detailed_story.json").exists() and 
                (scripts_dir / "video_prompts.json").exists()):
                
                logger.info(f"Scripts already exist for project {project_id}")
                
                # 加载现有脚本结果
                with open(scripts_dir / "script_crew_summary.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.info(f"Generating scripts for project {project_id}")
                return self.script_crew.process_project(project_id)
                
        except Exception as e:
            logger.error(f"Error ensuring script generation for project {project_id}: {e}")
            raise
    
    def _generate_video(self, project_id: str) -> Dict[str, Any]:
        """生成视频"""
        try:
            logger.info(f"Starting video generation for project {project_id}")
            return self.video_crew.process_project(project_id)
            
        except Exception as e:
            logger.error(f"Error generating video for project {project_id}: {e}")
            raise
    
    def _save_pipeline_result(self, project_id: str, result: Dict[str, Any]):
        """保存管道处理结果"""
        try:
            project_dir = Path("projects/projects") / project_id
            result_file = project_dir / "pipeline_result.json"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Pipeline result saved for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error saving pipeline result for project {project_id}: {e}")
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """获取项目状态"""
        try:
            project_dir = Path("projects/projects") / project_id
            
            status = {
                "project_id": project_id,
                "exists": project_dir.exists(),
                "approved": False,
                "script_generated": False,
                "video_generated": False,
                "pipeline_completed": False
            }
            
            if not status["exists"]:
                return status
            
            # 检查确认状态
            approved_file = project_dir / "approved_content.json"
            if approved_file.exists():
                with open(approved_file, 'r', encoding='utf-8') as f:
                    approved_data = json.load(f)
                    status["approved"] = approved_data.get("user_confirmed", False)
            
            # 检查脚本生成状态
            scripts_dir = project_dir / "scripts"
            if (scripts_dir.exists() and 
                (scripts_dir / "detailed_story.json").exists() and 
                (scripts_dir / "video_prompts.json").exists()):
                status["script_generated"] = True
            
            # 检查视频生成状态
            videos_dir = project_dir / "videos"
            final_videos_dir = project_dir / "final_videos"
            if videos_dir.exists() or final_videos_dir.exists():
                status["video_generated"] = True
            
            # 检查管道完成状态
            pipeline_result_file = project_dir / "pipeline_result.json"
            if pipeline_result_file.exists():
                with open(pipeline_result_file, 'r', encoding='utf-8') as f:
                    pipeline_data = json.load(f)
                    status["pipeline_completed"] = pipeline_data.get("pipeline_status") == "completed"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting project status for {project_id}: {e}")
            return {
                "project_id": project_id,
                "error": str(e)
            }
    
    def list_available_projects(self) -> List[Dict[str, Any]]:
        """列出所有可用项目"""
        try:
            projects_dir = Path("projects/projects")
            if not projects_dir.exists():
                return []
            
            projects = []
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    project_id = project_dir.name
                    status = self.get_project_status(project_id)
                    
                    # 获取项目基本信息
                    approved_file = project_dir / "approved_content.json"
                    if approved_file.exists():
                        try:
                            with open(approved_file, 'r', encoding='utf-8') as f:
                                approved_data = json.load(f)
                                status["title"] = approved_data.get("story_outline", {}).get("title", "Untitled")
                                status["created_at"] = approved_data.get("created_at", "")
                        except:
                            pass
                    
                    projects.append(status)
            
            # 按创建时间排序
            projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []


# 创建全局实例
video_pipeline = VideoGenerationPipeline()