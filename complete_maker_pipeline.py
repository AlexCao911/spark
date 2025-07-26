#!/usr/bin/env python3
"""
完整的Maker Crew视频生成流水线
从projects/project下提取prompt -> 生成视频片段 -> 剪辑成长视频

使用流程：
1. 从项目中提取视频提示词
2. 使用VEO3生成每个视频片段
3. 使用视频编辑工具拼接成最终视频
"""

import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.models import VideoPrompt, VideoClip
from src.spark.tools.veo3_real_tool import VEO3RealTool
from src.spark.crews.maker.src.maker.tools.video_generation_tool import VideoGenerationTool
from src.spark.crews.maker.src.maker.tools.video_editing_tool import VideoEditingTool


class CompleteMakerPipeline:
    """完整的Maker视频生成流水线"""
    
    def __init__(self):
        """初始化流水线组件"""
        print("🚀 初始化Maker视频生成流水线...")
        
        # 初始化工具
        try:
            self.veo3_tool = VEO3RealTool()
            self.video_generation_tool = VideoGenerationTool()
            self.video_editing_tool = VideoEditingTool()
            print("✅ 所有工具初始化完成")
        except Exception as e:
            print(f"❌ 工具初始化失败: {e}")
            raise
    
    def extract_project_prompts(self, project_id: str) -> List[Dict[str, Any]]:
        """从项目中提取视频提示词"""
        print(f"\n📋 步骤1: 从项目 {project_id} 提取视频提示词")
        print("=" * 60)
        
        try:
            # 构建文件路径
            prompts_path = Path("projects/projects") / project_id / "scripts" / "video_prompts.json"
            
            if not prompts_path.exists():
                print(f"❌ 提示词文件不存在: {prompts_path}")
                return []
            
            # 读取原始数据
            with open(prompts_path, 'r', encoding='utf-8') as f:
                raw_prompts = json.load(f)
            
            # 转换为标准格式
            formatted_prompts = []
            
            for prompt in raw_prompts:
                formatted_prompt = {
                    "shot_id": prompt.get("shot_id"),
                    "veo3_prompt": prompt.get("veo3_prompt", ""),
                    "duration": prompt.get("duration", 5),
                    "character_reference_images": prompt.get("character_reference_images", [])
                }
                formatted_prompts.append(formatted_prompt)
            
            # 按shot_id排序
            formatted_prompts.sort(key=lambda x: x["shot_id"])
            
            print(f"✅ 成功提取 {len(formatted_prompts)} 个视频提示词")
            
            # 显示提取的提示词概览
            total_duration = sum(p["duration"] for p in formatted_prompts)
            print(f"📊 总镜头数: {len(formatted_prompts)}")
            print(f"⏱️  预计总时长: {total_duration} 秒")
            
            for i, prompt in enumerate(formatted_prompts[:3]):  # 显示前3个
                print(f"   镜头 {prompt['shot_id']}: {prompt['veo3_prompt'][:50]}...")
            
            if len(formatted_prompts) > 3:
                print(f"   ... 还有 {len(formatted_prompts) - 3} 个镜头")
            
            return formatted_prompts
            
        except Exception as e:
            print(f"❌ 提取提示词失败: {e}")
            return []
    
    def generate_video_clips(self, project_id: str, video_prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成所有视频片段"""
        print(f"\n🎬 步骤2: 生成视频片段")
        print("=" * 60)
        
        if not video_prompts:
            print("❌ 没有视频提示词可以生成")
            return []
        
        generated_clips = []
        total_prompts = len(video_prompts)
        
        # 创建项目视频目录
        project_dir = Path("projects/projects") / project_id
        videos_dir = project_dir / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 视频将保存到: {videos_dir}")
        
        for i, prompt_data in enumerate(video_prompts):
            print(f"\n🎥 生成片段 {i+1}/{total_prompts}")
            print(f"   镜头ID: {prompt_data['shot_id']}")
            print(f"   提示词: {prompt_data['veo3_prompt'][:80]}...")
            print(f"   时长: {prompt_data['duration']} 秒")
            
            try:
                # 创建VideoPrompt对象
                video_prompt = VideoPrompt(**prompt_data)
                
                # 使用VEO3工具生成视频
                print("   🔄 正在调用VEO3生成视频...")
                job_id = self.veo3_tool.generate_video_clip(video_prompt)
                
                if job_id:
                    print(f"   ✅ 生成任务已提交: {job_id}")
                    
                    # 等待生成完成（简化版本，实际应该有更复杂的状态检查）
                    clip_info = self._wait_for_generation(job_id, prompt_data['shot_id'], videos_dir)
                    
                    if clip_info:
                        generated_clips.append(clip_info)
                        print(f"   ✅ 片段生成完成: {clip_info['file_path']}")
                    else:
                        print(f"   ❌ 片段生成失败")
                        # 创建失败记录
                        failed_clip = {
                            "clip_id": prompt_data['shot_id'],
                            "shot_id": prompt_data['shot_id'],
                            "file_path": "",
                            "duration": prompt_data['duration'],
                            "status": "failed"
                        }
                        generated_clips.append(failed_clip)
                else:
                    print(f"   ❌ 无法提交生成任务")
                    
            except Exception as e:
                print(f"   ❌ 生成片段时出错: {e}")
                continue
        
        # 统计结果
        successful_clips = [c for c in generated_clips if c.get("status") == "completed"]
        failed_clips = [c for c in generated_clips if c.get("status") == "failed"]
        
        print(f"\n📊 视频片段生成结果:")
        print(f"   ✅ 成功: {len(successful_clips)} 个")
        print(f"   ❌ 失败: {len(failed_clips)} 个")
        print(f"   📁 总计: {len(generated_clips)} 个")
        
        return generated_clips
    
    def _wait_for_generation(self, job_id: str, shot_id: int, videos_dir: Path, max_wait: int = 300) -> Optional[Dict]:
        """等待视频生成完成"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # 检查生成状态
                status = self.veo3_tool.check_generation_status(job_id)
                
                if status.get("status") == "completed":
                    video_url = status.get("url", "")
                    
                    if video_url:
                        # 下载视频到本地
                        video_filename = f"shot_{shot_id:03d}.mp4"
                        local_path = videos_dir / video_filename
                        
                        if self.veo3_tool.download_video(video_url, str(local_path)):
                            return {
                                "clip_id": shot_id,
                                "shot_id": shot_id,
                                "file_path": str(local_path),
                                "duration": 5,  # 默认5秒
                                "status": "completed"
                            }
                    else:
                        # 如果URL是本地路径，直接使用
                        if job_id.startswith("temp_video_processing/") or job_id.startswith("/"):
                            source_path = Path(job_id)
                            if source_path.exists():
                                video_filename = f"shot_{shot_id:03d}.mp4"
                                local_path = videos_dir / video_filename
                                
                                # 复制文件
                                import shutil
                                shutil.copy2(source_path, local_path)
                                
                                return {
                                    "clip_id": shot_id,
                                    "shot_id": shot_id,
                                    "file_path": str(local_path),
                                    "duration": 5,
                                    "status": "completed"
                                }
                
                elif status.get("status") == "failed":
                    print(f"   ❌ 生成失败: {status.get('error', 'Unknown error')}")
                    return None
                
                elif status.get("status") == "processing":
                    progress = status.get("progress", 0)
                    print(f"   🔄 生成中... {progress}%")
                    time.sleep(10)
                
                else:
                    print(f"   ⏳ 等待生成状态更新...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"   ⚠️  状态检查出错: {e}")
                time.sleep(5)
        
        print(f"   ⏰ 等待超时 ({max_wait}秒)")
        return None
    
    def assemble_final_video(self, project_id: str, video_clips: List[Dict[str, Any]], video_title: str = "") -> Dict[str, Any]:
        """拼接最终视频"""
        print(f"\n🎞️  步骤3: 拼接最终视频")
        print("=" * 60)
        
        if not video_clips:
            print("❌ 没有视频片段可以拼接")
            return {"status": "failed", "error": "No video clips"}
        
        # 过滤出成功生成的片段
        valid_clips = [clip for clip in video_clips if clip.get("status") == "completed" and clip.get("file_path")]
        
        if not valid_clips:
            print("❌ 没有有效的视频片段")
            return {"status": "failed", "error": "No valid clips"}
        
        print(f"📊 有效片段数: {len(valid_clips)}/{len(video_clips)}")
        
        # 计算总时长
        total_duration = sum(clip.get("duration", 5) for clip in valid_clips)
        
        if not video_title:
            video_title = f"Project_{project_id}_Video"
        
        print(f"🎬 视频标题: {video_title}")
        print(f"⏱️  预计时长: {total_duration} 秒")
        
        try:
            # 使用视频编辑工具拼接
            clips_json = json.dumps(valid_clips)
            
            result = self.video_editing_tool._run(
                video_clips=clips_json,
                project_id=project_id,
                video_title=video_title,
                total_duration=str(total_duration)
            )
            
            # 解析结果
            result_data = json.loads(result)
            
            if result_data.get("status") == "completed":
                print("✅ 视频拼接完成!")
                
                outputs = result_data.get("outputs", {})
                for version, path in outputs.items():
                    print(f"   📁 {version}: {path}")
                
                thumbnail = result_data.get("thumbnail", "")
                if thumbnail:
                    print(f"   🖼️  缩略图: {thumbnail}")
                
                metadata = result_data.get("metadata", {})
                final_duration = metadata.get("final_duration", 0)
                print(f"   ⏱️  最终时长: {final_duration:.2f} 秒")
                
                return result_data
            else:
                print(f"❌ 视频拼接失败: {result_data.get('error', 'Unknown error')}")
                return result_data
                
        except Exception as e:
            print(f"❌ 拼接过程出错: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_complete_pipeline(self, project_id: str, video_title: str = "") -> Dict[str, Any]:
        """运行完整的视频生成流水线"""
        print("🎬 启动完整的Maker视频生成流水线")
        print("=" * 80)
        print(f"📁 项目ID: {project_id}")
        print(f"🎯 目标: 从项目提取 -> 生成片段 -> 拼接视频")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # 步骤1: 提取项目提示词
            video_prompts = self.extract_project_prompts(project_id)
            if not video_prompts:
                return {
                    "status": "failed",
                    "error": "Failed to extract video prompts",
                    "project_id": project_id
                }
            
            # 步骤2: 生成视频片段
            video_clips = self.generate_video_clips(project_id, video_prompts)
            if not video_clips:
                return {
                    "status": "failed", 
                    "error": "Failed to generate video clips",
                    "project_id": project_id
                }
            
            # 步骤3: 拼接最终视频
            final_result = self.assemble_final_video(project_id, video_clips, video_title)
            
            # 计算总耗时
            total_time = time.time() - start_time
            
            # 添加流水线统计信息
            final_result.update({
                "pipeline_stats": {
                    "project_id": project_id,
                    "total_prompts": len(video_prompts),
                    "generated_clips": len(video_clips),
                    "successful_clips": len([c for c in video_clips if c.get("status") == "completed"]),
                    "total_time_seconds": round(total_time, 2),
                    "pipeline_status": "completed" if final_result.get("status") == "completed" else "partial"
                }
            })
            
            # 打印最终统计
            print(f"\n🏁 流水线执行完成!")
            print("=" * 60)
            print(f"⏱️  总耗时: {total_time:.2f} 秒")
            print(f"📊 处理统计:")
            print(f"   提示词: {len(video_prompts)} 个")
            print(f"   生成片段: {len(video_clips)} 个")
            print(f"   成功片段: {len([c for c in video_clips if c.get('status') == 'completed'])} 个")
            print(f"   最终状态: {final_result.get('status', 'unknown')}")
            
            return final_result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "project_id": project_id,
                "pipeline_stats": {
                    "total_time_seconds": time.time() - start_time,
                    "pipeline_status": "failed"
                }
            }
            print(f"\n❌ 流水线执行失败: {e}")
            return error_result
    
    def list_available_projects(self) -> List[str]:
        """列出可用的项目"""
        projects_base = Path("projects/projects")
        if not projects_base.exists():
            return []
        
        projects = []
        for project_dir in projects_base.iterdir():
            if project_dir.is_dir():
                # 检查是否有video_prompts.json文件
                prompts_file = project_dir / "scripts" / "video_prompts.json"
                if prompts_file.exists():
                    projects.append(project_dir.name)
        
        return projects


def main():
    """主函数 - 交互式运行"""
    print("🎬 Maker Crew 完整视频生成流水线")
    print("=" * 80)
    
    try:
        # 初始化流水线
        pipeline = CompleteMakerPipeline()
        
        # 列出可用项目
        available_projects = pipeline.list_available_projects()
        
        if not available_projects:
            print("❌ 没有找到可用的项目")
            print("请确保在 projects/projects/ 目录下有包含 scripts/video_prompts.json 的项目")
            return
        
        print(f"📁 找到 {len(available_projects)} 个可用项目:")
        for i, project in enumerate(available_projects, 1):
            print(f"   {i}. {project}")
        
        # 选择项目
        while True:
            try:
                choice = input(f"\n请选择项目 (1-{len(available_projects)}) 或输入项目ID: ").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(available_projects):
                    project_id = available_projects[int(choice) - 1]
                    break
                elif choice in available_projects:
                    project_id = choice
                    break
                else:
                    print("❌ 无效选择，请重试")
            except KeyboardInterrupt:
                print("\n👋 退出程序")
                return
        
        # 输入视频标题（可选）
        video_title = input(f"\n请输入视频标题 (默认: Project_{project_id}_Video): ").strip()
        if not video_title:
            video_title = f"Project_{project_id}_Video"
        
        print(f"\n🚀 开始处理项目: {project_id}")
        print(f"🎬 视频标题: {video_title}")
        
        # 运行完整流水线
        result = pipeline.run_complete_pipeline(project_id, video_title)
        
        # 显示最终结果
        print("\n" + "=" * 80)
        print("🎉 流水线执行结果:")
        print("=" * 80)
        
        if result.get("status") == "completed":
            print("✅ 成功完成视频生成!")
            
            outputs = result.get("outputs", {})
            if outputs:
                print("\n📁 生成的视频文件:")
                for version, path in outputs.items():
                    print(f"   {version}: {path}")
            
            thumbnail = result.get("thumbnail", "")
            if thumbnail:
                print(f"\n🖼️  缩略图: {thumbnail}")
            
        else:
            print(f"❌ 流水线执行失败: {result.get('error', 'Unknown error')}")
        
        # 显示统计信息
        stats = result.get("pipeline_stats", {})
        if stats:
            print(f"\n📊 执行统计:")
            print(f"   总耗时: {stats.get('total_time_seconds', 0):.2f} 秒")
            print(f"   处理提示词: {stats.get('total_prompts', 0)} 个")
            print(f"   生成片段: {stats.get('generated_clips', 0)} 个")
            print(f"   成功片段: {stats.get('successful_clips', 0)} 个")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()