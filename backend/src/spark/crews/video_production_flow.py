"""
Video Production Flow - 集成Script Crew和Maker Crew的完整视频制作流程
使用CrewAI Flow功能实现两个crew的顺序执行和数据传递
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List

from crewai import Flow, listen, start
from pydantic import BaseModel

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.crews.script.src.script.crew import ScriptGenerationCrew
from src.spark.crews.maker.src.maker.crew import VideoProductionCrew
from src.spark.models import ApprovedContent, DetailedStory, VideoPrompt
from src.spark.project_manager import project_manager

logger = logging.getLogger(__name__)


class ProjectInput(BaseModel):
    """Flow输入数据模型"""
    project_id: str
    video_title: str = ""
    force_regenerate: bool = False


class ScriptResult(BaseModel):
    """Script Crew输出数据模型"""
    project_id: str
    detailed_story: DetailedStory
    video_prompts: List[VideoPrompt]
    processing_status: str


class VideoResult(BaseModel):
    """Video Production结果数据模型"""
    project_id: str
    video_generation: Dict[str, Any]
    video_assembly: Dict[str, Any]
    final_videos: Dict[str, str]
    thumbnail: str
    metadata: Dict[str, Any]
    status: str


class VideoProductionFlow(Flow):
    """完整的视频制作流程Flow"""
    
    def __init__(self):
        """初始化Flow和相关组件"""
        super().__init__()
        
        # 初始化两个crew
        try:
            self.script_crew = ScriptGenerationCrew()
            self.maker_crew = VideoProductionCrew()
            logger.info("Video Production Flow initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize crews: {e}")
            raise
    
    @start()
    def start_production(self) -> ScriptResult:
        """
        Flow的起始点：执行Script Crew生成脚本和提示词
        
        Args:
            inputs: 包含project_id等输入参数
            
        Returns:
            ScriptResult: Script Crew的处理结果
        """
        # 从Flow的状态中获取输入参数
        project_id = self.state.get('project_id')
        force_regenerate = self.state.get('force_regenerate', False)
        
        logger.info(f"🎬 Starting video production flow for project: {project_id}")
        
        try:
            # 检查是否需要重新生成脚本
            if not force_regenerate and self._script_exists(project_id):
                logger.info("� Scnript already exists, loading from cache")
                script_result = self._load_existing_script(project_id)
            else:
                logger.info("📝 Generating new script with Script Crew")
                # 执行Script Crew
                script_data = self.script_crew.process_project(project_id)
                
                script_result = ScriptResult(
                    project_id=project_id,
                    detailed_story=script_data['detailed_story'],
                    video_prompts=script_data['video_prompts'],
                    processing_status=script_data['processing_status']
                )
            
            logger.info(f"✅ Script generation completed: {len(script_result.video_prompts)} prompts generated")
            return script_result
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            raise
    
    @listen(start_production)
    def produce_video(self, script_result: ScriptResult) -> VideoResult:
        """
        监听Script Crew完成事件，执行Maker Crew生成视频
        
        Args:
            script_result: Script Crew的输出结果
            
        Returns:
            VideoResult: 最终的视频制作结果
        """
        logger.info(f"🎥 Starting video production for project: {script_result.project_id}")
        logger.info(f"📊 Processing {len(script_result.video_prompts)} video prompts")
        
        try:
            # 准备Maker Crew的输入数据
            self._prepare_maker_crew_input(script_result)
            
            # 执行Maker Crew
            logger.info("🎬 Executing Maker Crew for video generation")
            video_data = self.maker_crew.process_project(script_result.project_id)
            
            # 构建返回结果
            video_result = VideoResult(
                project_id=script_result.project_id,
                video_generation=video_data.get('video_generation', {}),
                video_assembly=video_data.get('video_assembly', {}),
                final_videos=video_data.get('final_videos', {}),
                thumbnail=video_data.get('thumbnail', ''),
                metadata=video_data.get('metadata', {}),
                status=video_data.get('status', 'unknown')
            )
            
            logger.info(f"✅ Video production completed with status: {video_result.status}")
            
            if video_result.status == 'completed':
                logger.info("📁 Generated video files:")
                for version, path in video_result.final_videos.items():
                    logger.info(f"   {version}: {path}")
            
            return video_result
            
        except Exception as e:
            logger.error(f"❌ Video production failed: {e}")
            # 返回失败结果而不是抛出异常
            return VideoResult(
                project_id=script_result.project_id,
                video_generation={},
                video_assembly={},
                final_videos={},
                thumbnail='',
                metadata={'error': str(e)},
                status='failed'
            )
    
    def _script_exists(self, project_id: str) -> bool:
        """检查脚本文件是否已存在"""
        try:
            project_dir = Path("projects/projects") / project_id
            scripts_dir = project_dir / "scripts"
            
            detailed_story_path = scripts_dir / "detailed_story.json"
            video_prompts_path = scripts_dir / "video_prompts.json"
            
            return detailed_story_path.exists() and video_prompts_path.exists()
        except Exception:
            return False
    
    def _load_existing_script(self, project_id: str) -> ScriptResult:
        """加载已存在的脚本数据"""
        try:
            project_dir = Path("projects/projects") / project_id
            scripts_dir = project_dir / "scripts"
            
            # 加载详细故事
            with open(scripts_dir / "detailed_story.json", 'r', encoding='utf-8') as f:
                story_data = json.load(f)
            detailed_story = DetailedStory(**story_data)
            
            # 加载视频提示词
            with open(scripts_dir / "video_prompts.json", 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            video_prompts = [VideoPrompt(**prompt) for prompt in prompts_data]
            
            return ScriptResult(
                project_id=project_id,
                detailed_story=detailed_story,
                video_prompts=video_prompts,
                processing_status="loaded_from_cache"
            )
            
        except Exception as e:
            logger.error(f"Failed to load existing script: {e}")
            raise
    
    def _prepare_maker_crew_input(self, script_result: ScriptResult):
        """为Maker Crew准备输入数据"""
        try:
            project_dir = Path("projects/projects") / script_result.project_id
            
            # 确保Maker Crew需要的数据结构存在
            # 这里可以添加任何必要的数据转换或准备工作
            
            logger.info(f"📋 Prepared input data for Maker Crew")
            logger.info(f"   Story title: {script_result.detailed_story.title}")
            logger.info(f"   Total prompts: {len(script_result.video_prompts)}")
            logger.info(f"   Estimated duration: {script_result.detailed_story.total_duration}s")
            
        except Exception as e:
            logger.error(f"Failed to prepare Maker Crew input: {e}")
            raise
    
    def run_complete_pipeline(self, project_id: str, video_title: str = "", force_regenerate: bool = False) -> Dict[str, Any]:
        """
        运行完整的视频制作流水线
        
        Args:
            project_id: 项目ID
            video_title: 视频标题（可选）
            force_regenerate: 是否强制重新生成脚本
            
        Returns:
            Dict: 完整的流水线执行结果
        """
        logger.info(f"🚀 Starting complete video production pipeline")
        logger.info(f"📁 Project ID: {project_id}")
        logger.info(f"🎬 Video Title: {video_title or 'Auto-generated'}")
        logger.info(f"🔄 Force Regenerate: {force_regenerate}")
        
        try:
            # 创建输入数据
            inputs = ProjectInput(
                project_id=project_id,
                video_title=video_title or f"Video_{project_id[:8]}",
                force_regenerate=force_regenerate
            )
            
            # 设置Flow状态
            self.state = inputs.model_dump()
            
            # 执行Flow
            logger.info("🎯 Executing CrewAI Flow...")
            final_result = self.kickoff()
            
            # 处理最终结果
            if isinstance(final_result, VideoResult):
                result_dict = {
                    "project_id": final_result.project_id,
                    "status": final_result.status,
                    "final_videos": final_result.final_videos,
                    "thumbnail": final_result.thumbnail,
                    "metadata": final_result.metadata,
                    "video_generation": final_result.video_generation,
                    "video_assembly": final_result.video_assembly,
                    "flow_execution": "completed"
                }
            else:
                # 处理其他类型的结果
                result_dict = {
                    "project_id": project_id,
                    "status": "completed",
                    "result": str(final_result),
                    "flow_execution": "completed"
                }
            
            logger.info(f"🎉 Complete pipeline finished with status: {result_dict.get('status', 'unknown')}")
            return result_dict
            
        except Exception as e:
            logger.error(f"❌ Complete pipeline failed: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e),
                "flow_execution": "failed"
            }


def main():
    """主函数 - 用于测试Flow"""
    print("🎬 Video Production Flow 测试")
    print("=" * 80)
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 初始化Flow
        flow = VideoProductionFlow()
        
        # 选择测试项目
        project_id = "7570de8d-2952-44ba-95ac-f9397c95ac0f"
        video_title = "Flow_Test_Video"
        
        print(f"📁 测试项目: {project_id}")
        print(f"🎬 视频标题: {video_title}")
        
        # 运行完整流水线
        result = flow.run_complete_pipeline(
            project_id=project_id,
            video_title=video_title,
            force_regenerate=False  # 使用缓存的脚本
        )
        
        # 显示结果
        print("\n" + "=" * 80)
        print("🎉 Flow执行结果:")
        print("=" * 80)
        
        print(f"状态: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'completed':
            final_videos = result.get('final_videos', {})
            if final_videos:
                print("\n📁 生成的视频文件:")
                for version, path in final_videos.items():
                    print(f"   {version}: {path}")
            
            thumbnail = result.get('thumbnail', '')
            if thumbnail:
                print(f"\n🖼️  缩略图: {thumbnail}")
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n❌ 错误: {error}")
        
        print(f"\n📊 Flow执行状态: {result.get('flow_execution', 'unknown')}")
        
    except Exception as e:
        print(f"\n❌ Flow测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()