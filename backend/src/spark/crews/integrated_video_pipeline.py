"""
集成视频制作流水线
顺序执行Script Crew和Maker Crew，实现完整的视频制作流程
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.crews.script.src.script.crew import ScriptGenerationCrew
from src.spark.crews.maker.src.maker.crew import VideoProductionCrew

logger = logging.getLogger(__name__)


class IntegratedVideoProductionPipeline:
    """集成的视频制作流水线，顺序执行Script Crew和Maker Crew"""
    
    def __init__(self):
        """初始化两个crew"""
        logger.info("🚀 初始化集成视频制作流水线")
        
        try:
            # 初始化Script Crew
            logger.info("📝 初始化Script Crew...")
            self.script_crew = ScriptGenerationCrew()
            
            # 初始化Maker Crew
            logger.info("🎬 初始化Maker Crew...")
            self.maker_crew = VideoProductionCrew()
            
            logger.info("✅ 集成流水线初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 流水线初始化失败: {e}")
            raise
    
    def run_complete_pipeline(self, project_id: str, video_title: str = "", force_regenerate_script: bool = False) -> Dict[str, Any]:
        """
        运行完整的视频制作流水线
        
        Args:
            project_id: 项目ID
            video_title: 视频标题
            force_regenerate_script: 是否强制重新生成脚本
            
        Returns:
            Dict: 完整的流水线执行结果
        """
        logger.info("🎬 启动集成视频制作流水线")
        logger.info("=" * 80)
        logger.info(f"📁 项目ID: {project_id}")
        logger.info(f"🎯 视频标题: {video_title or 'Auto-generated'}")
        logger.info(f"🔄 强制重新生成脚本: {force_regenerate_script}")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # 第一步：执行Script Crew
            logger.info("\n📝 第一步：执行Script Crew生成脚本和提示词")
            logger.info("-" * 60)
            
            script_start_time = time.time()
            
            # 检查是否需要重新生成脚本
            if not force_regenerate_script and self._script_exists(project_id):
                logger.info("📋 发现已存在的脚本文件，跳过Script Crew执行")
                script_result = self._load_existing_script_summary(project_id)
                script_execution_time = 0
            else:
                logger.info("🔄 执行Script Crew生成新脚本...")
                script_result = self.script_crew.process_project(project_id)
                script_execution_time = time.time() - script_start_time
                
                logger.info(f"✅ Script Crew执行完成 (耗时: {script_execution_time:.1f}秒)")
                logger.info(f"📊 生成了 {len(script_result['video_prompts'])} 个视频提示词")
            
            # 第二步：执行Maker Crew
            logger.info("\n🎬 第二步：执行Maker Crew生成视频")
            logger.info("-" * 60)
            
            maker_start_time = time.time()
            
            logger.info("🎥 开始视频片段生成和拼接...")
            maker_result = self.maker_crew.process_project(project_id)
            maker_execution_time = time.time() - maker_start_time
            
            logger.info(f"✅ Maker Crew执行完成 (耗时: {maker_execution_time:.1f}秒)")
            
            # 合并结果
            total_time = time.time() - start_time
            
            final_result = {
                "project_id": project_id,
                "video_title": video_title,
                "pipeline_type": "integrated_crews",
                "execution_summary": {
                    "total_time_seconds": round(total_time, 2),
                    "script_time_seconds": round(script_execution_time, 2),
                    "maker_time_seconds": round(maker_execution_time, 2),
                    "script_regenerated": not (not force_regenerate_script and self._script_exists(project_id))
                },
                "script_crew_result": {
                    "status": script_result.get('processing_status', 'completed'),
                    "detailed_story_title": script_result.get('detailed_story', {}).get('title', ''),
                    "video_prompts_count": len(script_result.get('video_prompts', []))
                },
                "maker_crew_result": maker_result,
                "status": "completed" if maker_result.get('status') == 'completed' else "failed"
            }
            
            # 提取最终视频信息
            if maker_result.get('status') == 'completed':
                final_result.update({
                    "final_videos": maker_result.get('final_videos', {}),
                    "thumbnail": maker_result.get('thumbnail', ''),
                    "video_metadata": maker_result.get('metadata', {})
                })
            
            # 保存流水线执行摘要
            self._save_pipeline_summary(project_id, final_result)
            
            logger.info("\n🎉 集成流水线执行完成!")
            logger.info("=" * 80)
            logger.info(f"⏱️  总耗时: {total_time:.1f} 秒")
            logger.info(f"📝 Script Crew: {script_execution_time:.1f} 秒")
            logger.info(f"🎬 Maker Crew: {maker_execution_time:.1f} 秒")
            logger.info(f"📊 最终状态: {final_result['status']}")
            
            if final_result['status'] == 'completed':
                final_videos = final_result.get('final_videos', {})
                logger.info(f"📁 生成视频: {len(final_videos)} 个版本")
                for version, path in final_videos.items():
                    logger.info(f"   {version}: {path}")
            
            return final_result
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ 集成流水线执行失败: {e}")
            
            error_result = {
                "project_id": project_id,
                "video_title": video_title,
                "pipeline_type": "integrated_crews",
                "status": "failed",
                "error": str(e),
                "execution_summary": {
                    "total_time_seconds": round(error_time, 2),
                    "failed_at": "unknown"
                }
            }
            
            return error_result
    
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
    
    def _load_existing_script_summary(self, project_id: str) -> Dict[str, Any]:
        """加载已存在的脚本摘要信息"""
        try:
            project_dir = Path("projects/projects") / project_id
            scripts_dir = project_dir / "scripts"
            
            # 尝试加载摘要文件
            summary_path = scripts_dir / "script_crew_summary.json"
            if summary_path.exists():
                with open(summary_path, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                return {
                    "processing_status": "loaded_from_cache",
                    "detailed_story": {"title": summary_data.get('detailed_story', {}).get('title', '')},
                    "video_prompts": [{}] * summary_data.get('video_prompts', {}).get('total_shots', 0)
                }
            
            # 如果没有摘要文件，直接加载原始文件
            with open(scripts_dir / "detailed_story.json", 'r', encoding='utf-8') as f:
                story_data = json.load(f)
            
            with open(scripts_dir / "video_prompts.json", 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            return {
                "processing_status": "loaded_from_cache",
                "detailed_story": {"title": story_data.get('title', '')},
                "video_prompts": prompts_data
            }
            
        except Exception as e:
            logger.error(f"加载已存在脚本失败: {e}")
            raise
    
    def _save_pipeline_summary(self, project_id: str, result: Dict[str, Any]):
        """保存流水线执行摘要"""
        try:
            project_dir = Path("projects/projects") / project_id
            summary_path = project_dir / "integrated_pipeline_summary.json"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 流水线摘要已保存: {summary_path}")
            
        except Exception as e:
            logger.warning(f"保存流水线摘要失败: {e}")
    
    def list_available_projects(self) -> list[str]:
        """列出可用的项目"""
        projects_base = Path("projects/projects")
        if not projects_base.exists():
            return []
        
        projects = []
        for project_dir in projects_base.iterdir():
            if project_dir.is_dir():
                # 检查是否有必要的项目文件
                has_story = (project_dir / "story_outline.json").exists()
                has_characters = (project_dir / "characters.json").exists() or (project_dir / "characters").exists()
                has_approved = (project_dir / "approved_content.json").exists()
                
                if has_story or has_characters or has_approved:
                    projects.append(project_dir.name)
        
        return projects
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """获取项目状态信息"""
        project_dir = Path("projects/projects") / project_id
        
        status = {
            "project_id": project_id,
            "project_dir": str(project_dir),
            "exists": project_dir.exists(),
            "files": {},
            "script_ready": False,
            "videos_ready": False
        }
        
        if not project_dir.exists():
            return status
        
        # 检查各种文件
        files_to_check = {
            "story_outline": "story_outline.json",
            "characters": "characters.json",
            "approved_content": "approved_content.json",
            "detailed_story": "scripts/detailed_story.json",
            "video_prompts": "scripts/video_prompts.json",
            "pipeline_summary": "integrated_pipeline_summary.json"
        }
        
        for key, filename in files_to_check.items():
            file_path = project_dir / filename
            status["files"][key] = {
                "exists": file_path.exists(),
                "path": str(file_path)
            }
            
            if file_path.exists():
                try:
                    file_size = file_path.stat().st_size
                    status["files"][key]["size"] = file_size
                except:
                    pass
        
        # 检查脚本是否准备好
        status["script_ready"] = (
            status["files"]["detailed_story"]["exists"] and 
            status["files"]["video_prompts"]["exists"]
        )
        
        # 检查视频文件
        videos_dir = project_dir / "videos"
        final_videos_dir = project_dir / "final_videos"
        
        if videos_dir.exists():
            video_files = list(videos_dir.glob("*.mp4"))
            status["video_clips_count"] = len(video_files)
        else:
            status["video_clips_count"] = 0
        
        if final_videos_dir.exists():
            final_files = list(final_videos_dir.glob("*.mp4"))
            status["final_videos_count"] = len(final_files)
            status["videos_ready"] = len(final_files) > 0
        else:
            status["final_videos_count"] = 0
            status["videos_ready"] = False
        
        return status


def main():
    """主函数 - 用于测试集成流水线"""
    print("🎬 集成视频制作流水线测试")
    print("=" * 80)
    
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # 初始化流水线
        pipeline = IntegratedVideoProductionPipeline()
        
        # 选择测试项目
        available_projects = pipeline.list_available_projects()
        
        if not available_projects:
            print("❌ 没有找到可用的项目")
            return
        
        print(f"📁 找到 {len(available_projects)} 个可用项目:")
        for i, project in enumerate(available_projects, 1):
            print(f"   {i}. {project}")
        
        # 选择第一个项目进行测试
        project_id = available_projects[0]
        print(f"\n🎯 选择项目: {project_id}")
        
        # 显示项目状态
        status = pipeline.get_project_status(project_id)
        print(f"📊 项目状态:")
        print(f"   脚本准备: {'✅' if status['script_ready'] else '❌'}")
        print(f"   视频准备: {'✅' if status['videos_ready'] else '❌'}")
        print(f"   视频片段: {status['video_clips_count']} 个")
        print(f"   最终视频: {status['final_videos_count']} 个")
        
        # 运行完整流水线
        video_title = f"Integrated_Test_{project_id[:8]}"
        
        result = pipeline.run_complete_pipeline(
            project_id=project_id,
            video_title=video_title,
            force_regenerate_script=False
        )
        
        # 显示结果
        print("\n" + "=" * 80)
        print("🎉 集成流水线测试结果:")
        print("=" * 80)
        
        print(f"状态: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'completed':
            final_videos = result.get('final_videos', {})
            if final_videos:
                print("\n📁 生成的视频文件:")
                for version, path in final_videos.items():
                    print(f"   {version}: {path}")
            
            execution_summary = result.get('execution_summary', {})
            print(f"\n⏱️  执行统计:")
            print(f"   总耗时: {execution_summary.get('total_time_seconds', 0):.1f} 秒")
            print(f"   Script Crew: {execution_summary.get('script_time_seconds', 0):.1f} 秒")
            print(f"   Maker Crew: {execution_summary.get('maker_time_seconds', 0):.1f} 秒")
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n❌ 错误: {error}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()