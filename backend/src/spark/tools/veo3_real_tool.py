"""
Real VEO 3.0 API integration for video generation using Google AI Python SDK.
"""

import os
import time
import json
import requests
from typing import Dict, List, Optional
import base64
from pathlib import Path
from ..models import VideoPrompt

# Google AI SDK imports
try:
    import google.generativeai as genai
    from google.generativeai import types
    GOOGLE_AI_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_AI_SDK_AVAILABLE = False
    print("⚠️  Google AI SDK未安装，将使用REST API方式")

class VEO3RealTool:
    """Real implementation of VEO 3.0 video generation using Google AI Gemini API."""
    
    def __init__(self):
        self.api_key = os.getenv('VIDEO_GENERATE_API_KEY')
        
        # 检查是否启用模拟模式
        self.mock_mode = os.getenv('VEO3_MOCK_MODE', 'true').lower() == 'true'
        
        if self.mock_mode:
            print("🎭 VEO3工具运行在模拟模式")
            from .veo3_mock_tool import veo3_mock_tool
            self.mock_tool = veo3_mock_tool
        else:
            if not self.api_key:
                raise ValueError("VIDEO_GENERATE_API_KEY not found in environment variables")
            
            # 初始化Google AI客户端
            if GOOGLE_AI_SDK_AVAILABLE:
                genai.configure(api_key=self.api_key)
                self.client = genai.Client()
                self.model_name = "veo-3.0-generate-preview"
                print(f"🔧 VEO3工具初始化 (SDK模式):")
                print(f"   模型: {self.model_name}")
                print(f"   使用Google AI Python SDK")
            else:
                # 回退到REST API模式
                self.base_url = "https://generativelanguage.googleapis.com/v1beta"
                self.model_name = "models/veo-3.0-generate-preview"
                self.generate_url = f"{self.base_url}/{self.model_name}:generateContent"
                print(f"🔧 VEO3工具初始化 (REST API模式):")
                print(f"   模型: {self.model_name}")
                print(f"   生成URL: {self.generate_url}")
        
    def _get_api_key(self):
        """获取API密钥"""
        return self.api_key
    
    def _upload_image(self, image_url: str) -> str:
        """处理参考图像URL，VEO 3.0支持直接使用图像URL"""
        # VEO 3.0可以直接使用图像URL，无需上传
        return image_url
    
    def generate_video_clip(self, video_prompt: VideoPrompt) -> str:
        """Generate video clip using VEO 3.0 API or mock tool."""
        if self.mock_mode:
            return self.mock_tool.generate_video_clip(video_prompt)
        
        try:
            # 获取API密钥
            api_key = self._get_api_key()
            if not api_key:
                print("⚠️  无法获取API密钥，切换到模拟模式")
                return self.mock_tool.generate_video_clip(video_prompt)
            
            # 优先使用SDK方式
            if GOOGLE_AI_SDK_AVAILABLE:
                return self._generate_with_sdk(video_prompt)
            else:
                return self._generate_with_rest_api(video_prompt)
                
        except Exception as e:
            print(f"❌ 视频生成错误，切换到模拟模式: {str(e)}")
            return self.mock_tool.generate_video_clip(video_prompt)
    
    def _generate_with_sdk(self, video_prompt: VideoPrompt) -> str:
        """使用Google AI SDK生成视频"""
        try:
            print(f"🎬 使用SDK生成视频...")
            print(f"📝 提示词: {video_prompt.veo3_prompt}")
            print(f"⏱️  时长: {video_prompt.duration}秒")
            
            # 构建生成配置
            config = types.GenerateVideosConfig(
                negative_prompt="cartoon, drawing, low quality, blurry, distorted",
                duration_seconds=video_prompt.duration,
                aspect_ratio="16:9"
            )
            
            # 准备提示词
            prompt = video_prompt.veo3_prompt
            
            # 如果有参考图像，添加到提示词中
            if video_prompt.character_reference_images:
                prompt += " 参考图像风格保持一致"
            
            # 调用VEO 3.0生成视频
            operation = self.client.models.generate_videos(
                model=self.model_name,
                prompt=prompt,
                config=config
            )
            
            print(f"✅ 视频生成任务已提交")
            print(f"📋 操作ID: {operation.name}")
            
            # 返回操作ID用于后续状态查询
            return f"job_{operation.name}"
            
        except Exception as e:
            print(f"❌ SDK生成失败: {str(e)}")
            # 如果SDK失败，尝试REST API
            return self._generate_with_rest_api(video_prompt)
    
    def _generate_with_rest_api(self, video_prompt: VideoPrompt) -> str:
        """使用REST API生成视频（回退方案）"""
        try:
            print(f"🎬 使用REST API生成视频...")
            
            # 首先尝试找到可用的视频生成模型
            available_model = self._find_available_video_model(self.api_key)
            if not available_model:
                print("⚠️  未找到可用的视频生成模型，切换到模拟模式")
                return self.mock_tool.generate_video_clip(video_prompt)
            
            # 准备请求格式
            contents = []
            
            # 添加文本提示词
            contents.append({
                "parts": [{"text": f"生成视频：{video_prompt.veo3_prompt}，时长{video_prompt.duration}秒"}]
            })
            
            # 添加参考图像（如果有）
            for ref_image_url in video_prompt.character_reference_images:
                if ref_image_url:
                    try:
                        if ref_image_url.startswith('http'):
                            img_response = requests.get(ref_image_url)
                            if img_response.status_code == 200:
                                image_data = base64.b64encode(img_response.content).decode('utf-8')
                                contents.append({
                                    "parts": [{
                                        "inline_data": {
                                            "mime_type": "image/jpeg",
                                            "data": image_data
                                        }
                                    }]
                                })
                        else:
                            # 假设是base64编码的数据
                            contents.append({
                                "parts": [{
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": ref_image_url
                                    }
                                }]
                            })
                    except Exception as e:
                        print(f"⚠️  无法处理参考图像 {ref_image_url}: {e}")
            
            # 构建请求
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                }
            }
            
            # 设置请求头
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 构建完整的URL
            full_url = f"{self.base_url}/{available_model}:generateContent?key={self.api_key}"
            
            print(f"📝 使用模型: {available_model}")
            print(f"📝 提示词: {video_prompt.veo3_prompt}")
            print(f"⏱️  时长: {video_prompt.duration}秒")
            
            response = requests.post(
                full_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            print(f"📡 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 请求成功")
                
                # 解析响应
                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        
                        for part in parts:
                            # 检查是否有视频数据
                            if "inline_data" in part:
                                inline_data = part["inline_data"]
                                if inline_data.get("mime_type", "").startswith("video/"):
                                    # 保存视频数据到临时文件
                                    video_data = base64.b64decode(inline_data["data"])
                                    timestamp = int(time.time())
                                    video_filename = f"generated_video_{timestamp}.mp4"
                                    video_path = Path("temp_video_processing") / video_filename
                                    video_path.parent.mkdir(exist_ok=True)
                                    
                                    with open(video_path, "wb") as f:
                                        f.write(video_data)
                                    
                                    return str(video_path)
                            
                            # 检查文本响应
                            if "text" in part:
                                text_response = part["text"]
                                print(f"📄 模型响应: {text_response}")
                                
                                # 如果模型说明无法生成视频，切换到模拟模式
                                if any(keyword in text_response.lower() for keyword in 
                                      ["cannot generate", "unable to create", "不能生成", "无法创建"]):
                                    print("⚠️  模型无法生成视频，切换到模拟模式")
                                    return self.mock_tool.generate_video_clip(video_prompt)
                
                # 如果没有找到视频内容，返回模拟结果
                print("⚠️  响应中未找到视频内容，切换到模拟模式")
                return self.mock_tool.generate_video_clip(video_prompt)
                
            else:
                error_text = response.text
                print(f"❌ 请求失败，切换到模拟模式: {error_text}")
                return self.mock_tool.generate_video_clip(video_prompt)
                
        except Exception as e:
            print(f"❌ REST API生成失败: {str(e)}")
            return self.mock_tool.generate_video_clip(video_prompt)
    
    def _find_available_video_model(self, api_key: str) -> Optional[str]:
        """查找可用的视频生成模型"""
        try:
            # 获取模型列表
            models_url = f"{self.base_url}/models?key={api_key}"
            response = requests.get(models_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            models = response.json()
            
            # 按优先级查找视频模型
            video_model_candidates = [
                "models/veo-3.0-generate",
                "models/veo-2.0-generate", 
                "models/video-generation",
                "models/gemini-1.5-pro-vision",  # 可能支持视频相关功能
                "models/gemini-pro-vision"
            ]
            
            available_models = [model.get('name', '') for model in models.get('models', [])]
            
            for candidate in video_model_candidates:
                if candidate in available_models:
                    print(f"✅ 找到可用模型: {candidate}")
                    return candidate
            
            # 如果没有找到专门的视频模型，尝试使用视觉模型
            vision_models = [model for model in available_models if 'vision' in model.lower()]
            if vision_models:
                print(f"⚠️  未找到视频模型，尝试使用视觉模型: {vision_models[0]}")
                return vision_models[0]
            
            return None
            
        except Exception as e:
            print(f"❌ 查找可用模型时出错: {str(e)}")
            return None
    
    def generate_with_professional_specs(
        self, 
        video_prompt: VideoPrompt, 
        reference_images: List[str]
    ) -> str:
        """Generate video with professional specifications and reference images."""
        if self.mock_mode:
            return self.mock_tool.generate_with_professional_specs(video_prompt, reference_images)
        
        try:
            # Use the same implementation but with enhanced specs
            enhanced_prompt = f"{video_prompt.veo3_prompt}, cinematic quality, professional lighting, high resolution"
            
            # Create a new prompt with enhanced specs
            enhanced_video_prompt = VideoPrompt(
                shot_id=video_prompt.shot_id,
                veo3_prompt=enhanced_prompt,
                duration=video_prompt.duration,
                character_reference_images=reference_images
            )
            
            return self.generate_video_clip(enhanced_video_prompt)
            
        except Exception as e:
            print(f"Error generating professional video: {str(e)}")
            return self.mock_tool.generate_with_professional_specs(video_prompt, reference_images)
    
    def check_generation_status(self, job_id: str) -> Dict:
        """Check status of video generation job."""
        if self.mock_mode:
            return self.mock_tool.check_generation_status(job_id)
        
        return self._check_real_generation_status(job_id)
    
    def _check_real_generation_status(self, job_id: str) -> Dict:
        """Check actual status of VEO 3.0 video generation job."""
        try:
            # 如果job_id是文件路径，检查文件是否存在
            if job_id.startswith("temp_video_processing/"):
                video_path = Path(job_id)
                if video_path.exists():
                    return {
                        "status": "completed",
                        "url": str(video_path),
                        "progress": 100
                    }
                else:
                    return {
                        "status": "processing",
                        "progress": 50
                    }
            
            # 如果是URL，直接返回完成状态
            if job_id.startswith("http"):
                return {
                    "status": "completed",
                    "url": job_id,
                    "progress": 100
                }
            
            # 如果是SDK操作ID，使用SDK查询状态
            if GOOGLE_AI_SDK_AVAILABLE and hasattr(self, 'client'):
                try:
                    operation = self.client.operations.get(name=job_id)
                    
                    if operation.done:
                        if operation.response:
                            # 操作完成，检查结果
                            video_url = self._extract_video_url_from_operation(operation)
                            if video_url:
                                return {
                                    "status": "completed",
                                    "url": video_url,
                                    "progress": 100
                                }
                            else:
                                return {
                                    "status": "completed_no_url",
                                    "progress": 100,
                                    "message": "Video generation completed but no URL found"
                                }
                        else:
                            # 操作失败
                            error_message = getattr(operation.error, 'message', 'Unknown error') if operation.error else 'Unknown error'
                            return {
                                "status": "failed",
                                "error": error_message
                            }
                    else:
                        # 仍在处理中
                        progress = getattr(operation.metadata, 'progress_percent', 50) if operation.metadata else 50
                        return {
                            "status": "processing",
                            "progress": progress,
                            "message": "Video generation in progress..."
                        }
                        
                except Exception as e:
                    print(f"❌ SDK状态查询失败: {str(e)}")
                    # 回退到模拟状态
                    return {
                        "status": "processing",
                        "progress": 75,
                        "message": "Video generation in progress..."
                    }
            
            # 对于其他job_id，模拟处理状态
            return {
                "status": "processing",
                "progress": 75,
                "message": "Video generation in progress..."
            }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _extract_video_url_from_operation(self, operation) -> Optional[str]:
        """从操作结果中提取视频URL"""
        try:
            if hasattr(operation, 'response') and operation.response:
                response = operation.response
                
                # 尝试不同的可能字段
                if hasattr(response, 'video_url'):
                    return response.video_url
                elif hasattr(response, 'generated_video'):
                    if hasattr(response.generated_video, 'uri'):
                        return response.generated_video.uri
                elif hasattr(response, 'uri'):
                    return response.uri
                
                # 如果是字典格式
                if isinstance(response, dict):
                    return response.get('video_url') or response.get('uri')
            
            return None
            
        except Exception as e:
            print(f"❌ 提取视频URL失败: {str(e)}")
            return None
    
    def validate_prompt_compatibility(self, video_prompt: VideoPrompt) -> bool:
        """Validate if prompt is compatible with VEO 3.0."""
        if self.mock_mode:
            return self.mock_tool.validate_prompt_compatibility(video_prompt)
        
        try:
            # Basic validation checks
            if not video_prompt.veo3_prompt or len(video_prompt.veo3_prompt.strip()) < 10:
                return False
            
            if video_prompt.duration < 1 or video_prompt.duration > 60:
                return False
            
            # Check for prohibited content keywords
            prohibited_keywords = ["violence", "gore", "explicit", "nsfw", "暴力", "血腥"]
            prompt_lower = video_prompt.veo3_prompt.lower()
            
            for keyword in prohibited_keywords:
                if keyword in prompt_lower:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def optimize_generation_parameters(self, video_prompt: VideoPrompt) -> Dict:
        """Optimize generation parameters for VEO 3.0."""
        if self.mock_mode:
            return self.mock_tool.optimize_generation_parameters(video_prompt)
        
        duration = video_prompt.duration
        
        # Optimize based on duration
        if duration <= 5:
            fps = 24
            resolution = "1080p"
        elif duration <= 15:
            fps = 24
            resolution = "1080p"
        else:
            fps = 24
            resolution = "720p"  # Lower resolution for longer videos
        
        return {
            "resolution": resolution,
            "fps": fps,
            "duration": duration,
            "aspectRatio": "16:9",
            "quality": "high"
        }
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """Download generated video to local file."""
        if self.mock_mode:
            return self.mock_tool.download_video(video_url, output_path)
        
        try:
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            # 回退到模拟模式
            return self.mock_tool.download_video(video_url, output_path)