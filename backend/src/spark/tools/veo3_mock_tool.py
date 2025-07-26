"""
VEO3 Mock Tool - 用于演示和测试的模拟VEO3工具
当真实的VEO3 API不可用时，提供模拟功能
"""

import os
import time
import json
import random
from typing import Dict, List, Optional
from pathlib import Path
from ..models import VideoPrompt


class VEO3MockTool:
    """VEO3模拟工具，用于演示和测试"""
    
    def __init__(self):
        self.api_key = os.getenv('VIDEO_GENERATE_API_KEY', 'mock_key')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'mock_project')
        self.location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        # 模拟配置
        self.mock_enabled = os.getenv('VEO3_MOCK_MODE', 'true').lower() == 'true'
        self.mock_delay = float(os.getenv('VEO3_MOCK_DELAY', '2.0'))  # 模拟生成延迟
        
        print(f"🎭 VEO3模拟工具初始化 (模拟模式: {'开启' if self.mock_enabled else '关闭'})")
        
        # 存储生成的任务
        self.mock_jobs = {}
        
        # 创建模拟视频目录
        self.mock_video_dir = Path("mock_videos")
        self.mock_video_dir.mkdir(exist_ok=True)
    
    def validate_prompt_compatibility(self, video_prompt: VideoPrompt) -> bool:
        """验证提示词兼容性"""
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
    
    def optimize_generation_parameters(self, video_prompt: VideoPrompt) -> Dict:
        """优化生成参数"""
        duration = video_prompt.duration
        
        # 根据时长优化参数
        if duration <= 5:
            fps = 24
            resolution = "1080p"
        elif duration <= 15:
            fps = 24
            resolution = "1080p"
        else:
            fps = 24
            resolution = "720p"  # 较长视频使用较低分辨率
        
        return {
            "resolution": resolution,
            "fps": fps,
            "duration": duration,
            "aspectRatio": "16:9",
            "quality": "high"
        }
    
    def generate_video_clip(self, video_prompt: VideoPrompt) -> str:
        """生成视频片段（模拟）"""
        try:
            print(f"🎬 模拟生成视频片段 {video_prompt.shot_id}")
            print(f"📝 提示词: {video_prompt.veo3_prompt}")
            print(f"⏱️  时长: {video_prompt.duration}秒")
            
            # 验证提示词
            if not self.validate_prompt_compatibility(video_prompt):
                return f"error_invalid_prompt_{video_prompt.shot_id}"
            
            # 模拟生成延迟
            time.sleep(self.mock_delay)
            
            # 创建模拟视频文件
            mock_video_path = self._create_mock_video(video_prompt)
            
            if mock_video_path:
                print(f"✅ 模拟视频生成完成: {mock_video_path}")
                return mock_video_path
            else:
                return f"error_generation_failed_{video_prompt.shot_id}"
                
        except Exception as e:
            print(f"❌ 模拟视频生成失败: {str(e)}")
            return f"error_{video_prompt.shot_id}"
    
    def generate_with_professional_specs(
        self, 
        video_prompt: VideoPrompt, 
        reference_images: List[str]
    ) -> str:
        """使用专业规格生成视频（模拟）"""
        try:
            # 增强提示词
            enhanced_prompt = f"{video_prompt.veo3_prompt}, cinematic quality, professional lighting, high resolution"
            
            # 创建增强的提示词对象
            enhanced_video_prompt = VideoPrompt(
                shot_id=video_prompt.shot_id,
                veo3_prompt=enhanced_prompt,
                duration=video_prompt.duration,
                character_reference_images=reference_images
            )
            
            print(f"🎭 使用专业规格模拟生成视频")
            return self.generate_video_clip(enhanced_video_prompt)
            
        except Exception as e:
            print(f"❌ 专业规格模拟生成失败: {str(e)}")
            return f"error_prof_{video_prompt.shot_id}"
    
    def check_generation_status(self, job_id: str) -> Dict:
        """检查生成状态（模拟）"""
        try:
            # 模拟状态检查
            if job_id.startswith("job_"):
                # 模拟异步任务
                if job_id in self.mock_jobs:
                    job_info = self.mock_jobs[job_id]
                    elapsed = time.time() - job_info["start_time"]
                    
                    if elapsed < 5:  # 前5秒显示处理中
                        progress = min(90, elapsed * 18)  # 逐渐增加到90%
                        return {
                            "status": "processing",
                            "progress": progress
                        }
                    else:  # 5秒后完成
                        return {
                            "status": "completed",
                            "url": job_info["video_path"],
                            "progress": 100
                        }
                else:
                    return {
                        "status": "not_found",
                        "error": f"Job {job_id} not found"
                    }
            else:
                # 直接返回的文件路径
                return {
                    "status": "completed",
                    "url": job_id,
                    "progress": 100
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """下载视频文件（模拟）"""
        try:
            # 如果是本地文件路径，直接复制
            if Path(video_url).exists():
                import shutil
                shutil.copy2(video_url, output_path)
                print(f"✅ 模拟视频下载完成: {output_path}")
                return True
            else:
                # 创建一个模拟视频文件
                self._create_mock_video_file(output_path)
                print(f"✅ 创建模拟视频文件: {output_path}")
                return True
                
        except Exception as e:
            print(f"❌ 模拟视频下载失败: {str(e)}")
            return False
    
    def _create_mock_video(self, video_prompt: VideoPrompt) -> str:
        """创建模拟视频文件"""
        try:
            # 生成文件名
            filename = f"mock_shot_{video_prompt.shot_id:03d}_{int(time.time())}.mp4"
            video_path = self.mock_video_dir / filename
            
            # 创建模拟视频文件
            self._create_mock_video_file(str(video_path), video_prompt)
            
            return str(video_path)
            
        except Exception as e:
            print(f"❌ 创建模拟视频失败: {str(e)}")
            return ""
    
    def _create_mock_video_file(self, output_path: str, video_prompt: VideoPrompt = None):
        """创建实际的模拟视频文件"""
        try:
            # 尝试使用FFmpeg创建简单的测试视频
            import subprocess
            
            duration = video_prompt.duration if video_prompt else 5
            
            # 创建一个简单的彩色视频
            color = self._get_color_from_prompt(video_prompt.veo3_prompt if video_prompt else "blue")
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color={color}:size=1920x1080:duration={duration}:rate=24',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 使用FFmpeg创建模拟视频: {output_path}")
            else:
                # FFmpeg失败，创建占位文件
                self._create_placeholder_file(output_path)
                
        except Exception:
            # 如果FFmpeg不可用，创建占位文件
            self._create_placeholder_file(output_path)
    
    def _create_placeholder_file(self, output_path: str):
        """创建占位文件"""
        try:
            # 创建一个小的占位文件
            with open(output_path, 'wb') as f:
                # 写入一些模拟的视频数据
                f.write(b'MOCK_VIDEO_FILE_' + b'0' * 1024)  # 1KB占位文件
            
            print(f"✅ 创建占位视频文件: {output_path}")
            
        except Exception as e:
            print(f"❌ 创建占位文件失败: {str(e)}")
    
    def _get_color_from_prompt(self, prompt: str) -> str:
        """从提示词中提取颜色"""
        color_map = {
            '蓝': 'blue',
            '红': 'red', 
            '绿': 'green',
            '黄': 'yellow',
            '白': 'white',
            '黑': 'black',
            '天空': 'skyblue',
            '云': 'white',
            '夜': 'darkblue',
            '日': 'yellow',
            'blue': 'blue',
            'red': 'red',
            'green': 'green',
            'sky': 'skyblue',
            'cloud': 'white',
            'night': 'darkblue',
            'day': 'yellow'
        }
        
        prompt_lower = prompt.lower()
        for keyword, color in color_map.items():
            if keyword in prompt_lower:
                return color
        
        # 默认颜色
        return 'skyblue'


# 创建全局实例
veo3_mock_tool = VEO3MockTool()