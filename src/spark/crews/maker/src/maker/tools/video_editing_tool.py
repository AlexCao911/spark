"""
Video Editing Tool - 视频编辑工具
使用MoviePy和FFmpeg进行视频拼接和后期处理
"""

import json
import os
import subprocess
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

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
    from moviepy.video.fx import resize, fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("MoviePy not available, using FFmpeg fallback")


class VideoEditingTool(BaseTool):
    """CrewAI工具：视频编辑和拼接"""
    
    name: str = "Video Editing Tool"
    description: str = """
    专业视频编辑工具，用于拼接视频片段并生成最终视频。
    
    输入参数：
    - video_clips: 视频片段信息列表（JSON格式）
    - project_id: 项目ID
    - video_title: 视频标题
    - total_duration: 目标总时长
    
    功能：
    - 视频片段拼接
    - 转场效果添加
    - 音频处理和同步
    - 多格式输出
    - 质量优化
    """
    
    def __init__(self):
        super().__init__()
        self.temp_dir = Path("temp_video_processing")
        self.temp_dir.mkdir(exist_ok=True)
    
    def _run(self, video_clips: str, project_id: str = "", video_title: str = "", total_duration: str = "60") -> str:
        """执行视频编辑任务"""
        try:
            # 解析输入参数
            clips_data = json.loads(video_clips) if isinstance(video_clips, str) else video_clips
            target_duration = int(total_duration) if total_duration else 60
            
            # 验证视频片段文件
            valid_clips = self._validate_video_clips(clips_data)
            if not valid_clips:
                return json.dumps({
                    "error": "No valid video clips found",
                    "status": "failed"
                }, ensure_ascii=False)
            
            # 创建输出目录
            project_dir = Path("projects/projects") / project_id
            output_dir = project_dir / "final_videos"
            output_dir.mkdir(exist_ok=True)
            
            # 生成最终视频
            if MOVIEPY_AVAILABLE:
                result = self._assemble_with_moviepy(valid_clips, output_dir, video_title, target_duration)
            else:
                result = self._assemble_with_ffmpeg(valid_clips, output_dir, video_title, target_duration)
            
            # 添加项目信息
            result["project_id"] = project_id
            result["video_title"] = video_title
            result["target_duration"] = target_duration
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "status": "error",
                "project_id": project_id
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    def _validate_video_clips(self, clips_data: List[Dict]) -> List[Dict]:
        """验证视频片段文件是否存在且有效"""
        valid_clips = []
        
        for clip in clips_data:
            file_path = clip.get("file_path", "")
            if file_path and Path(file_path).exists():
                # 检查文件大小
                file_size = Path(file_path).stat().st_size
                if file_size > 1024:  # 至少1KB
                    valid_clips.append(clip)
                    print(f"有效片段: {file_path}")
                else:
                    print(f"片段文件太小，跳过: {file_path}")
            else:
                print(f"片段文件不存在，跳过: {file_path}")
        
        # 按shot_id排序
        valid_clips.sort(key=lambda x: x.get("shot_id", 0))
        return valid_clips
    
    def _assemble_with_moviepy(self, clips_data: List[Dict], output_dir: Path, video_title: str, target_duration: int) -> Dict:
        """使用MoviePy拼接视频"""
        try:
            # 加载视频片段
            video_clips = []
            total_actual_duration = 0
            
            for clip_info in clips_data:
                file_path = clip_info["file_path"]
                try:
                    clip = VideoFileClip(file_path)
                    
                    # 添加淡入淡出效果
                    if len(video_clips) == 0:
                        # 第一个片段：淡入
                        clip = clip.fx(fadein, 0.5)
                    
                    if clip_info == clips_data[-1]:
                        # 最后一个片段：淡出
                        clip = clip.fx(fadeout, 0.5)
                    
                    video_clips.append(clip)
                    total_actual_duration += clip.duration
                    print(f"加载片段: {file_path}, 时长: {clip.duration:.2f}s")
                    
                except Exception as e:
                    print(f"加载片段失败 {file_path}: {str(e)}")
                    continue
            
            if not video_clips:
                raise Exception("没有有效的视频片段可以拼接")
            
            # 拼接视频
            print("正在拼接视频片段...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # 调整总时长（如果需要）
            if abs(final_video.duration - target_duration) > 2:  # 允许2秒误差
                final_video = final_video.subclip(0, min(final_video.duration, target_duration))
            
            # 生成输出文件名
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_title:
                safe_title = "generated_video"
            
            # 输出不同版本
            outputs = {}
            
            # 高质量版本
            hq_output = output_dir / f"{safe_title}_HQ.mp4"
            print(f"正在生成高质量版本: {hq_output}")
            final_video.write_videofile(
                str(hq_output),
                codec='libx264',
                audio_codec='aac',
                fps=24,
                bitrate="5000k"
            )
            outputs["high_quality"] = str(hq_output)
            
            # 网络优化版本
            web_output = output_dir / f"{safe_title}_Web.mp4"
            print(f"正在生成网络版本: {web_output}")
            final_video.write_videofile(
                str(web_output),
                codec='libx264',
                audio_codec='aac',
                fps=24,
                bitrate="2000k"
            )
            outputs["web_optimized"] = str(web_output)
            
            # 移动版本
            mobile_output = output_dir / f"{safe_title}_Mobile.mp4"
            print(f"正在生成移动版本: {mobile_output}")
            mobile_video = final_video.fx(resize, height=720)  # 720p
            mobile_video.write_videofile(
                str(mobile_output),
                codec='libx264',
                audio_codec='aac',
                fps=24,
                bitrate="1000k"
            )
            outputs["mobile"] = str(mobile_output)
            
            # 清理资源
            for clip in video_clips:
                clip.close()
            final_video.close()
            if 'mobile_video' in locals():
                mobile_video.close()
            
            # 生成缩略图
            thumbnail_path = self._generate_thumbnail(outputs["high_quality"], output_dir, safe_title)
            
            return {
                "status": "completed",
                "outputs": outputs,
                "thumbnail": thumbnail_path,
                "metadata": {
                    "total_clips": len(clips_data),
                    "successful_clips": len(video_clips),
                    "final_duration": final_video.duration if 'final_video' in locals() else 0,
                    "target_duration": target_duration
                }
            }
            
        except Exception as e:
            print(f"MoviePy拼接失败: {str(e)}")
            raise
    
    def _assemble_with_ffmpeg(self, clips_data: List[Dict], output_dir: Path, video_title: str, target_duration: int) -> Dict:
        """使用FFmpeg拼接视频（备用方案）"""
        try:
            # 创建文件列表
            file_list_path = self.temp_dir / "file_list.txt"
            with open(file_list_path, 'w', encoding='utf-8') as f:
                for clip_info in clips_data:
                    file_path = clip_info["file_path"]
                    f.write(f"file '{os.path.abspath(file_path)}'\n")
            
            # 生成输出文件名
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_title:
                safe_title = "generated_video"
            
            outputs = {}
            
            # 高质量版本
            hq_output = output_dir / f"{safe_title}_HQ.mp4"
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', '5000k',
                '-r', '24',
                str(hq_output)
            ]
            
            print(f"正在使用FFmpeg生成高质量版本...")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                outputs["high_quality"] = str(hq_output)
                print(f"高质量版本生成完成: {hq_output}")
            else:
                print(f"FFmpeg错误: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")
            
            # 网络优化版本
            web_output = output_dir / f"{safe_title}_Web.mp4"
            ffmpeg_cmd[ffmpeg_cmd.index('5000k')] = '2000k'
            ffmpeg_cmd[-1] = str(web_output)
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                outputs["web_optimized"] = str(web_output)
            
            # 移动版本（720p）
            mobile_output = output_dir / f"{safe_title}_Mobile.mp4"
            ffmpeg_cmd_mobile = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', '1000k',
                '-vf', 'scale=-2:720',
                '-r', '24',
                str(mobile_output)
            ]
            
            result = subprocess.run(ffmpeg_cmd_mobile, capture_output=True, text=True)
            if result.returncode == 0:
                outputs["mobile"] = str(mobile_output)
            
            # 生成缩略图
            thumbnail_path = self._generate_thumbnail_ffmpeg(outputs["high_quality"], output_dir, safe_title)
            
            return {
                "status": "completed",
                "outputs": outputs,
                "thumbnail": thumbnail_path,
                "metadata": {
                    "total_clips": len(clips_data),
                    "method": "ffmpeg"
                }
            }
            
        except Exception as e:
            print(f"FFmpeg拼接失败: {str(e)}")
            raise
    
    def _generate_thumbnail(self, video_path: str, output_dir: Path, title: str) -> str:
        """使用MoviePy生成缩略图"""
        try:
            if MOVIEPY_AVAILABLE:
                clip = VideoFileClip(video_path)
                thumbnail_path = output_dir / f"{title}_thumbnail.jpg"
                
                # 在视频中间位置截取缩略图
                frame_time = clip.duration / 2
                clip.save_frame(str(thumbnail_path), t=frame_time)
                clip.close()
                
                return str(thumbnail_path)
            else:
                return self._generate_thumbnail_ffmpeg(video_path, output_dir, title)
        except Exception as e:
            print(f"生成缩略图失败: {str(e)}")
            return ""
    
    def _generate_thumbnail_ffmpeg(self, video_path: str, output_dir: Path, title: str) -> str:
        """使用FFmpeg生成缩略图"""
        try:
            thumbnail_path = output_dir / f"{title}_thumbnail.jpg"
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-ss', '00:00:03',  # 3秒处截图
                '-vframes', '1',
                '-q:v', '2',
                str(thumbnail_path)
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return str(thumbnail_path)
            else:
                print(f"FFmpeg缩略图生成失败: {result.stderr}")
                return ""
        except Exception as e:
            print(f"FFmpeg缩略图生成失败: {str(e)}")
            return ""