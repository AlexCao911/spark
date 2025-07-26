"""
Video Generation Tool - VEO3视频生成工具
使用Google AI Python SDK直接调用VEO3 API
"""

import json
import time
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from crewai_tools import BaseTool
except ImportError:
    # Fallback if crewai_tools is not available or BaseTool doesn't exist
    class BaseTool:
        name: str = ""
        description: str = ""
        
        def _run(self, *args, **kwargs):
            raise NotImplementedError

# Google AI SDK imports
try:
    from google import genai
    from google.genai import types
    GOOGLE_AI_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_AI_SDK_AVAILABLE = False
    print("⚠️  Google AI SDK未安装，请运行: pip install google-generativeai")

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.models import VideoPrompt, VideoClip
from veo3_quota_config import VEO3QuotaConfig


class VideoGenerationTool(BaseTool):
    """CrewAI工具：使用VEO3生成视频片段"""
    
    name: str = "Video Generation Tool"
    description: str = """
    使用VEO3 API生成高质量视频片段的专业工具。
    
    输入参数：
    - video_prompts: 视频提示词列表（JSON格式）
    - character_images: 角色参考图像URL列表
    - project_id: 项目ID
    
    功能：
    - 批量生成视频片段
    - 维持角色视觉一致性
    - 简洁的错误处理
    - 进度跟踪和状态报告
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('VIDEO_GENERATE_API_KEY')
        
        # 检查是否启用模拟模式
        self.mock_mode = os.getenv('VEO3_MOCK_MODE', 'true').lower() == 'true'
        
        # 加载配额管理配置
        self.quota_config = VEO3QuotaConfig()
        
        # 配额管理状态
        self.quota_exhausted = False
        self.last_quota_check = 0
        
        if self.mock_mode:
            print("🎭 VideoGenerationTool运行在模拟模式")
            # 在模拟模式下不需要API密钥
            self.model_name = "veo-3.0-generate-preview"
            print(f"🔧 VEO3工具初始化完成 (模拟模式):")
            print(f"   模型: {self.model_name}")
            return
        
        if not self.api_key:
            raise ValueError("VIDEO_GENERATE_API_KEY not found in environment variables")
        
        if not GOOGLE_AI_SDK_AVAILABLE:
            raise ImportError("Google AI SDK not available. Please install: pip install google-generativeai")
        
        # 初始化Google AI客户端
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "veo-3.0-generate-preview"
        
        print(f"🔧 VEO3工具初始化完成:")
        print(f"   模型: {self.model_name}")
        print(f"   使用Google AI Python SDK")
        print(f"   配额管理: 启用")
        
        # 显示配额配置（如果启用调试模式）
        if self.quota_config.debug_mode:
            self.quota_config.print_config()
    
    def _run(self, video_prompts: str, character_images: str = "", project_id: str = "") -> str:
        """执行视频生成任务，带智能配额管理"""
        try:
            # 解析输入参数
            prompts_data = json.loads(video_prompts) if isinstance(video_prompts, str) else video_prompts
            char_images = json.loads(character_images) if isinstance(character_images, str) else []
            
            # 转换为VideoPrompt对象
            video_prompt_objects = []
            for prompt_data in prompts_data:
                if isinstance(prompt_data, dict):
                    # 确保包含角色参考图像
                    if char_images and 'character_reference_images' not in prompt_data:
                        prompt_data['character_reference_images'] = char_images
                    
                    video_prompt_objects.append(VideoPrompt(**prompt_data))
                else:
                    # 如果是字符串，创建基本的VideoPrompt
                    video_prompt_objects.append(VideoPrompt(
                        shot_id=len(video_prompt_objects) + 1,
                        veo3_prompt=str(prompt_data),
                        duration=5,
                        character_reference_images=char_images
                    ))
            
            # 生成视频片段，带智能配额管理
            generated_clips = self._generate_clips_with_quota_management(video_prompt_objects, project_id)
            
            # 统计结果
            successful_clips = [c for c in generated_clips if c.status == "completed"]
            failed_clips = [c for c in generated_clips if c.status == "failed"]
            
            # 返回结果
            result = {
                "project_id": project_id,
                "total_prompts": len(video_prompt_objects),
                "successful_clips": len(successful_clips),
                "failed_clips": len(failed_clips),
                "clips": [
                    {
                        "clip_id": clip.clip_id,
                        "shot_id": clip.shot_id,
                        "file_path": clip.file_path,
                        "duration": clip.duration,
                        "status": clip.status,
                        "error_message": getattr(clip, 'error_message', None),
                        "retry_count": getattr(clip, 'retry_count', 0)
                    }
                    for clip in generated_clips
                ],
                "status": "completed" if successful_clips else "failed",
                "quota_issues": len([c for c in failed_clips if c.error_message and "quota" in c.error_message.lower()]),
                "generation_summary": {
                    "success_rate": f"{len(successful_clips)}/{len(video_prompt_objects)}",
                    "total_retries": sum(getattr(c, 'retry_count', 0) for c in generated_clips)
                }
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "status": "error",
                "project_id": project_id
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    def _generate_clips_with_quota_management(self, video_prompts: List[VideoPrompt], project_id: str) -> List[VideoClip]:
        """智能配额管理的视频片段生成"""
        generated_clips = []
        total_prompts = len(video_prompts)
        consecutive_quota_failures = 0
        
        print(f"🎬 开始生成 {total_prompts} 个视频片段")
        print("📊 启用智能配额管理和错误恢复")
        
        for i, prompt in enumerate(video_prompts):
            print(f"\n正在生成视频片段 {i+1}/{total_prompts}: {prompt.veo3_prompt[:50]}...")
            
            # 检查配额状态
            if not self._check_quota_status():
                print(f"⏸️  配额限制中，跳过片段 {prompt.shot_id}")
                failed_clip = VideoClip(
                    clip_id=prompt.shot_id,
                    shot_id=prompt.shot_id,
                    file_path="",
                    duration=prompt.duration,
                    status="failed",
                    generation_job_id=f"quota_skip_{prompt.shot_id}",
                    error_message="Skipped due to quota exhaustion",
                    retry_count=0
                )
                generated_clips.append(failed_clip)
                continue
            
            # 检查是否需要暂停（连续配额失败）
            if self.quota_config.should_skip_due_to_quota(consecutive_quota_failures):
                wait_time = self.quota_config.get_quota_wait_time(consecutive_quota_failures)
                print(f"⏸️  检测到连续配额失败，暂停 {wait_time/60:.1f} 分钟...")
                time.sleep(wait_time)
                consecutive_quota_failures = 0
            
            # 生成单个片段
            clip = self._generate_single_clip(prompt, project_id)
            
            if clip:
                generated_clips.append(clip)
                
                if clip.status == "completed":
                    print(f"✅ 片段 {prompt.shot_id} 生成成功")
                    consecutive_quota_failures = 0  # 重置连续失败计数
                    
                    # 成功后短暂暂停，避免过快请求
                    time.sleep(self.quota_config.success_wait_time)
                    
                elif clip.status == "failed":
                    print(f"❌ 片段 {prompt.shot_id} 生成失败: {clip.error_message}")
                    
                    # 检查是否是配额问题
                    if clip.error_message and self._is_quota_error(clip.error_message):
                        consecutive_quota_failures += 1
                        print(f"🚫 配额限制失败计数: {consecutive_quota_failures}")
                        
                        # 如果连续失败太多次，标记配额耗尽
                        if consecutive_quota_failures >= self.quota_config.consecutive_failure_threshold:
                            self._mark_quota_exhausted()
                    else:
                        consecutive_quota_failures = 0
            else:
                # 创建失败的clip记录
                failed_clip = VideoClip(
                    clip_id=prompt.shot_id,
                    shot_id=prompt.shot_id,
                    file_path="",
                    duration=prompt.duration,
                    status="failed",
                    generation_job_id=f"failed_{prompt.shot_id}",
                    error_message="Generation returned None",
                    retry_count=0
                )
                generated_clips.append(failed_clip)
                print(f"❌ 片段 {prompt.shot_id} 生成失败: 未知错误")
        
        # 生成摘要
        successful_count = len([c for c in generated_clips if c.status == "completed"])
        failed_count = len([c for c in generated_clips if c.status == "failed"])
        
        print(f"\n📊 视频生成完成摘要:")
        print(f"   ✅ 成功: {successful_count}/{total_prompts}")
        print(f"   ❌ 失败: {failed_count}/{total_prompts}")
        print(f"   📈 成功率: {successful_count/total_prompts*100:.1f}%")
        
        return generated_clips
    
    def _check_quota_status(self) -> bool:
        """检查API配额状态"""
        current_time = time.time()
        
        # 如果配额已耗尽且未到重置时间，返回False
        if self.quota_exhausted and (current_time - self.last_quota_check) < self.quota_config.quota_reset_interval:
            remaining_time = self.quota_config.quota_reset_interval - (current_time - self.last_quota_check)
            print(f"🚫 配额仍在限制中，剩余等待时间: {remaining_time/60:.1f} 分钟")
            return False
        
        # 如果已过重置时间，重置配额状态
        if self.quota_exhausted and (current_time - self.last_quota_check) >= self.quota_config.quota_reset_interval:
            print("🔄 配额重置时间已到，重新尝试")
            self.quota_exhausted = False
        
        return True
    
    def _mark_quota_exhausted(self):
        """标记配额已耗尽"""
        self.quota_exhausted = True
        self.last_quota_check = time.time()
        print(f"🚫 标记配额已耗尽，将在 {self.quota_config.quota_reset_interval/60:.0f} 分钟后重试")
    
    def _is_quota_error(self, error_str: str) -> bool:
        """检查是否是配额限制错误"""
        quota_indicators = [
            "429", "RESOURCE_EXHAUSTED", "quota", "rate limit", 
            "exceeded", "billing", "plan"
        ]
        error_lower = error_str.lower()
        return any(indicator.lower() in error_lower for indicator in quota_indicators)
    
    def _generate_single_clip(self, prompt: VideoPrompt, project_id: str) -> Optional[VideoClip]:
        """生成单个视频片段"""
        try:
            print(f"🎬 生成视频片段...")
            print(f"📝 提示词: {prompt.veo3_prompt}")
            print(f"⏱️  时长: {prompt.duration}秒")
            
            if self.mock_mode:
                return self._generate_mock_clip(prompt, project_id)
            else:
                return self._generate_real_clip(prompt, project_id)
            
        except Exception as e:
            print(f"❌ 生成视频片段失败: {str(e)}")
            return None
    
    def _generate_mock_clip(self, prompt: VideoPrompt, project_id: str) -> Optional[VideoClip]:
        """生成模拟视频片段"""
        try:
            # 创建项目目录
            project_dir = Path("projects/projects") / project_id
            videos_dir = project_dir / "videos"
            videos_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成模拟视频文件
            video_filename = f"shot_{prompt.shot_id:03d}.mp4"
            output_path = videos_dir / video_filename
            
            # 创建一个简单的测试视频文件
            # 使用FFmpeg创建一个真正的测试视频文件
            try:
                import subprocess
                # 创建一个5秒的纯色测试视频
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=blue:size=640x480:duration=5',
                    '-c:v', 'libx264',
                    '-t', '5',
                    str(output_path)
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    # 如果FFmpeg失败，创建一个最小的MP4文件头
                    # 这是一个最小的有效MP4文件头
                    mp4_header = bytes([
                        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
                        0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
                        0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
                        0x61, 0x76, 0x63, 0x31, 0x6D, 0x70, 0x34, 0x31
                    ])
                    with open(output_path, 'wb') as f:
                        f.write(mp4_header)
                        f.write(b'\x00' * 1024)  # 填充一些数据
                        
            except Exception as e:
                # 最后的备用方案：创建基本的MP4文件头
                mp4_header = bytes([
                    0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
                    0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
                    0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
                    0x61, 0x76, 0x63, 0x31, 0x6D, 0x70, 0x34, 0x31
                ])
                with open(output_path, 'wb') as f:
                    f.write(mp4_header)
                    f.write(b'\x00' * 1024)
            
            print(f"🎭 模拟视频已创建: {output_path}")
            
            # 创建VideoClip对象
            clip = VideoClip(
                clip_id=prompt.shot_id,
                shot_id=prompt.shot_id,
                file_path=str(output_path),
                duration=prompt.duration,
                status="completed",
                generation_job_id=f"mock_job_{prompt.shot_id}"
            )
            
            return clip
            
        except Exception as e:
            print(f"❌ 生成模拟片段失败: {str(e)}")
            return None
    
    def _generate_real_clip(self, prompt: VideoPrompt, project_id: str, max_retries: int = None) -> Optional[VideoClip]:
        """使用Google AI SDK生成真实视频片段，带重试和错误处理"""
        
        if max_retries is None:
            max_retries = self.quota_config.max_retries
        
        # 创建失败的VideoClip对象
        def create_failed_clip(error_msg: str, retry_count: int = max_retries) -> VideoClip:
            return VideoClip(
                clip_id=prompt.shot_id,
                shot_id=prompt.shot_id,
                file_path="",
                duration=prompt.duration,
                status="failed",
                generation_job_id=f"failed_{prompt.shot_id}",
                error_message=error_msg,
                retry_count=retry_count
            )
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 尝试 {attempt + 1}/{max_retries}")
                
                # 构建生成配置
                config = types.GenerateVideosConfig(
                    negative_prompt="cartoon, drawing, low quality, blurry, distorted"
                )
                
                # 准备提示词
                veo3_prompt = prompt.veo3_prompt
                
                # 如果有参考图像，添加到提示词中
                if prompt.character_reference_images:
                    veo3_prompt += " 参考图像风格保持一致"
                
                # 调用VEO 3.0生成视频
                operation = self.client.models.generate_videos(
                    model=self.model_name,
                    prompt=veo3_prompt,
                    config=config
                )
                
                print(f"✅ 视频生成任务已提交")
                print(f"📋 操作ID: {operation.name}")
                
                # 等待视频生成完成
                max_wait_time = self.quota_config.generation_timeout
                wait_time = 0
                
                while not operation.done and wait_time < max_wait_time:
                    print("等待视频生成完成...")
                    time.sleep(10)
                    wait_time += 10
                    try:
                        operation = self.client.operations.get(operation)
                    except Exception as e:
                        print(f"⚠️  检查操作状态时出错: {e}")
                        break
                
                if wait_time >= max_wait_time:
                    print("⏰ 视频生成超时")
                    if attempt < max_retries - 1:
                        print(f"🔄 将在 30 秒后重试...")
                        time.sleep(30)
                        continue
                    else:
                        return create_failed_clip("Generation timeout", attempt + 1)
                
                # 创建VideoClip对象
                clip = VideoClip(
                    clip_id=prompt.shot_id,
                    shot_id=prompt.shot_id,
                    file_path="",
                    duration=prompt.duration,
                    status="generating",
                    generation_job_id=operation.name
                )
                
                # 检查生成结果
                if operation.response and hasattr(operation.response, 'generated_videos'):
                    generated_video = operation.response.generated_videos[0]
                    
                    # 下载生成的视频
                    video_filename = f"shot_{prompt.shot_id:03d}.mp4"
                    project_dir = Path("projects/projects") / project_id
                    videos_dir = project_dir / "videos"
                    videos_dir.mkdir(parents=True, exist_ok=True)
                    output_path = videos_dir / video_filename
                    
                    try:
                        # 使用SDK下载视频
                        self.client.files.download(file=generated_video.video)
                        generated_video.video.save(str(output_path))
                        
                        clip.file_path = str(output_path)
                        clip.status = "completed"
                        clip.retry_count = attempt
                        
                        print(f"✅ 视频已保存到: {output_path}")
                        return clip
                        
                    except Exception as download_error:
                        print(f"❌ 下载视频失败: {download_error}")
                        if attempt < max_retries - 1:
                            print(f"🔄 将在 30 秒后重试...")
                            time.sleep(30)
                            continue
                        else:
                            return create_failed_clip(f"Download failed: {download_error}", attempt + 1)
                
                else:
                    print("❌ 视频生成失败，未找到生成的视频")
                    if attempt < max_retries - 1:
                        print(f"🔄 将在 30 秒后重试...")
                        time.sleep(30)
                        continue
                    else:
                        return create_failed_clip("No generated video found", attempt + 1)
                
            except Exception as e:
                error_str = str(e)
                print(f"❌ 生成真实视频片段失败: {error_str}")
                
                # 检查是否是配额限制错误
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    print("🚫 检测到API配额限制")
                    
                    if attempt < max_retries - 1:
                        # 配额限制时等待更长时间
                        wait_time = self.quota_config.get_retry_wait_time(attempt)
                        print(f"⏳ 等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("❌ 达到最大重试次数，配额限制无法解决")
                        return create_failed_clip(f"Quota exhausted: {error_str}", attempt + 1)
                
                # 检查是否是网络错误
                elif "network" in error_str.lower() or "connection" in error_str.lower() or "timeout" in error_str.lower():
                    print("🌐 检测到网络错误")
                    
                    if attempt < max_retries - 1:
                        wait_time = self.quota_config.retry_wait_base
                        print(f"⏳ 等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return create_failed_clip(f"Network error: {error_str}", attempt + 1)
                
                # 其他错误
                else:
                    if attempt < max_retries - 1:
                        wait_time = self.quota_config.retry_wait_base // 2  # 其他错误等待时间较短
                        print(f"⏳ 等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return create_failed_clip(f"Generation error: {error_str}", attempt + 1)
        
        # 如果所有重试都失败了
        return create_failed_clip("All retry attempts failed", max_retries)
    
    def validate_prompt_compatibility(self, video_prompt: VideoPrompt) -> bool:
        """验证提示词是否兼容VEO3"""
        try:
            # 基本验证检查
            if not video_prompt.veo3_prompt or len(video_prompt.veo3_prompt.strip()) < 10:
                return False
            
            if video_prompt.duration < 1 or video_prompt.duration > 60:
                return False
            
            # 检查禁止内容关键词
            prohibited_keywords = ["violence", "gore", "explicit", "nsfw", "暴力", "血腥"]
            prompt_lower = video_prompt.veo3_prompt.lower()
            
            for keyword in prohibited_keywords:
                if keyword in prompt_lower:
                    return False
            
            return True
            
        except Exception:
            return False