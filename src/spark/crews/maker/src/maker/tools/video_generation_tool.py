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
    
    def _run(self, video_prompts: str, character_images: str = "", project_id: str = "") -> str:
        """执行视频生成任务"""
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
            
            # 生成视频片段
            generated_clips = []
            total_prompts = len(video_prompt_objects)
            
            for i, prompt in enumerate(video_prompt_objects):
                print(f"正在生成视频片段 {i+1}/{total_prompts}: {prompt.veo3_prompt[:50]}...")
                
                # 生成单个片段
                clip = self._generate_single_clip(prompt, project_id)
                if clip:
                    generated_clips.append(clip)
                    print(f"片段 {prompt.shot_id} 生成完成: {clip.status}")
                else:
                    print(f"片段 {prompt.shot_id} 生成失败")
            
            # 返回结果
            result = {
                "project_id": project_id,
                "total_prompts": total_prompts,
                "successful_clips": len([c for c in generated_clips if c.status == "completed"]),
                "failed_clips": len([c for c in generated_clips if c.status == "failed"]),
                "clips": [
                    {
                        "clip_id": clip.clip_id,
                        "shot_id": clip.shot_id,
                        "file_path": clip.file_path,
                        "duration": clip.duration,
                        "status": clip.status
                    }
                    for clip in generated_clips
                ],
                "status": "completed" if generated_clips else "failed"
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "status": "error",
                "project_id": project_id
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)
    
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
            
            # 创建一个简单的测试视频文件（空文件，但有正确的扩展名）
            # 在实际应用中，这里应该创建一个真正的测试视频
            with open(output_path, 'wb') as f:
                # 写入一些测试数据，模拟视频文件
                f.write(b'MOCK_VIDEO_DATA_FOR_TESTING' * 100)
            
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
    
    def _generate_real_clip(self, prompt: VideoPrompt, project_id: str) -> Optional[VideoClip]:
        """使用Google AI SDK生成真实视频片段"""
        try:
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
            while not operation.done:
                print("等待视频生成完成...")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
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
                
                # 使用SDK下载视频
                self.client.files.download(file=generated_video.video)
                generated_video.video.save(str(output_path))
                
                clip.file_path = str(output_path)
                clip.status = "completed"
                
                print(f"✅ 视频已保存到: {output_path}")
                
            else:
                print("❌ 视频生成失败，未找到生成的视频")
                clip.status = "failed"
            
            return clip
            
        except Exception as e:
            print(f"❌ 生成真实视频片段失败: {str(e)}")
            return None
    
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