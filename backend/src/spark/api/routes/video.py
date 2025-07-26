"""
视频生成相关的API路由 - 增强版本支持final_video传递
"""

import json
import logging
import threading
import time
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, session

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.spark.video_generation_pipeline import video_pipeline

logger = logging.getLogger(__name__)

# 创建蓝图
video_bp = Blueprint('video', __name__, url_prefix='/api/video')

# 全局任务跟踪
active_jobs = {}


@video_bp.route('/generate', methods=['POST'])
def start_video_generation():
    """启动视频生成流程"""
    try:
        data = request.get_json()
        project_id = data.get('project_id', '')
        
        if not project_id:
            return jsonify({
                "success": False,
                "error": "Project ID is required"
            }), 400
        
        # 检查项目是否存在且已确认
        project_status = video_pipeline.get_project_status(project_id)
        if not project_status.get('exists'):
            return jsonify({
                "success": False,
                "error": "Project not found"
            }), 404
        
        if not project_status.get('approved'):
            return jsonify({
                "success": False,
                "error": "Project not approved yet"
            }), 400
        
        # 创建任务ID
        job_id = f"video_job_{project_id}_{int(time.time())}"
        
        # 初始化任务状态
        active_jobs[job_id] = {
            "project_id": project_id,
            "status": "started",
            "progress": 0.0,
            "current_step": "Initializing video generation",
            "start_time": time.time(),
            "result": None,
            "error": None
        }
        
        # 启动后台线程
        thread = threading.Thread(
            target=_generate_video_background,
            args=(job_id, project_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "status": "started",
            "estimated_time": 300
        })
        
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/status/<job_id>', methods=['GET'])
def get_generation_status(job_id):
    """获取视频生成状态"""
    try:
        if job_id not in active_jobs:
            return jsonify({
                "success": False,
                "error": "Job not found"
            }), 404
        
        job_info = active_jobs[job_id]
        
        response = {
            "success": True,
            "job_id": job_id,
            "project_id": job_info["project_id"],
            "status": job_info["status"],
            "progress": job_info["progress"],
            "current_step": job_info["current_step"],
            "elapsed_time": time.time() - job_info["start_time"]
        }
        
        if job_info["status"] == "completed":
            response["result"] = job_info["result"]
            # 添加视频文件信息
            project_id = job_info["project_id"]
            video_info = _get_project_video_info(project_id)
            response["videos"] = video_info
        elif job_info["status"] == "failed":
            response["error"] = job_info["error"]
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/download/<project_id>/<video_type>', methods=['GET'])
def download_video(project_id, video_type):
    """下载生成的视频"""
    try:
        project_dir = Path("projects/projects") / project_id / "final_videos"
        
        # 映射视频类型到文件模式
        type_mapping = {
            "hq": "_HQ.mp4",
            "web": "_Web.mp4", 
            "mobile": "_Mobile.mp4",
            "final": ".mp4"  # 支持通用final视频
        }
        
        if video_type not in type_mapping:
            return jsonify({
                "success": False,
                "error": "Invalid video type. Use: hq, web, mobile, or final"
            }), 400
        
        # 查找视频文件
        if video_type == "final":
            # 查找任何mp4文件
            video_files = list(project_dir.glob("*.mp4"))
        else:
            pattern = f"*{type_mapping[video_type]}"
            video_files = list(project_dir.glob(pattern))
        
        if not video_files:
            return jsonify({
                "success": False,
                "error": "Video file not found"
            }), 404
        
        video_file = video_files[0]
        
        return send_file(
            video_file,
            as_attachment=True,
            download_name=f"{project_id}_{video_type}.mp4",
            mimetype='video/mp4'
        )
        
    except Exception as e:
        logger.error(f"Video download error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/stream/<project_id>/<video_type>', methods=['GET'])
def stream_video(project_id, video_type):
    """流式传输视频（用于在线播放）"""
    try:
        project_dir = Path("projects/projects") / project_id / "final_videos"
        
        # 映射视频类型到文件模式
        type_mapping = {
            "hq": "_HQ.mp4",
            "web": "_Web.mp4", 
            "mobile": "_Mobile.mp4",
            "final": ".mp4"
        }
        
        if video_type not in type_mapping:
            return jsonify({
                "success": False,
                "error": "Invalid video type"
            }), 400
        
        # 查找视频文件
        if video_type == "final":
            video_files = list(project_dir.glob("*.mp4"))
        else:
            pattern = f"*{type_mapping[video_type]}"
            video_files = list(project_dir.glob(pattern))
        
        if not video_files:
            return jsonify({
                "success": False,
                "error": "Video file not found"
            }), 404
        
        video_file = video_files[0]
        
        return send_file(
            video_file,
            mimetype='video/mp4',
            as_attachment=False,
            conditional=True  # 支持范围请求，用于视频流
        )
        
    except Exception as e:
        logger.error(f"Video streaming error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/project/<project_id>/videos', methods=['GET'])
def get_project_videos():
    """获取项目的所有视频信息"""
    try:
        video_info = _get_project_video_info(project_id)
        
        if not video_info['available_videos']:
            return jsonify({
                "success": False,
                "error": "No videos found for this project"
            }), 404
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "video_info": video_info,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Get project videos error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/thumbnail/<project_id>', methods=['GET'])
def get_thumbnail(project_id):
    """获取视频缩略图"""
    try:
        project_dir = Path("projects/projects") / project_id / "final_videos"
        
        # 查找缩略图文件
        thumbnail_files = list(project_dir.glob("*_thumbnail.jpg"))
        if not thumbnail_files:
            thumbnail_files = list(project_dir.glob("*thumbnail*"))
        
        if not thumbnail_files:
            return jsonify({
                "success": False,
                "error": "Thumbnail not found"
            }), 404
        
        thumbnail_file = thumbnail_files[0]
        
        return send_file(
            thumbnail_file,
            mimetype='image/jpeg'
        )
        
    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/projects', methods=['GET'])
def list_projects():
    """列出所有可用项目"""
    try:
        projects = video_pipeline.list_available_projects()
        return jsonify({
            "success": True,
            "projects": projects
        })
        
    except Exception as e:
        logger.error(f"List projects error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/project/<project_id>/status', methods=['GET'])
def get_project_status(project_id):
    """获取详细项目状态"""
    try:
        status = video_pipeline.get_project_status(project_id)
        
        # 添加视频信息
        if status.get('exists'):
            video_info = _get_project_video_info(project_id)
            status['video_info'] = video_info
        
        return jsonify({
            "success": True,
            "status": status
        })
        
    except Exception as e:
        logger.error(f"Project status error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@video_bp.route('/jobs', methods=['GET'])
def list_active_jobs():
    """列出所有活跃的视频生成任务"""
    try:
        jobs_info = {}
        for job_id, job_data in active_jobs.items():
            jobs_info[job_id] = {
                "project_id": job_data["project_id"],
                "status": job_data["status"],
                "progress": job_data["progress"],
                "current_step": job_data["current_step"],
                "elapsed_time": time.time() - job_data["start_time"]
            }
        
        return jsonify({
            "success": True,
            "active_jobs": jobs_info
        })
        
    except Exception as e:
        logger.error(f"List jobs error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def _get_project_video_info(project_id):
    """获取项目视频信息的辅助函数"""
    try:
        project_dir = Path("projects/projects") / project_id / "final_videos"
        
        if not project_dir.exists():
            return {
                "available_videos": [],
                "has_videos": False,
                "video_count": 0
            }
        
        # 查找所有视频文件
        video_files = list(project_dir.glob("*.mp4"))
        
        video_info = {
            "available_videos": [],
            "has_videos": len(video_files) > 0,
            "video_count": len(video_files)
        }
        
        for video_file in video_files:
            file_name = video_file.name
            file_size = video_file.stat().st_size
            
            # 确定视频类型
            video_type = "final"
            if "_HQ.mp4" in file_name:
                video_type = "hq"
            elif "_Web.mp4" in file_name:
                video_type = "web"
            elif "_Mobile.mp4" in file_name:
                video_type = "mobile"
            
            video_info["available_videos"].append({
                "type": video_type,
                "filename": file_name,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "download_url": f"/api/video/download/{project_id}/{video_type}",
                "stream_url": f"/api/video/stream/{project_id}/{video_type}"
            })
        
        # 查找缩略图
        thumbnail_files = list(project_dir.glob("*_thumbnail.jpg"))
        if thumbnail_files:
            video_info["thumbnail_url"] = f"/api/video/thumbnail/{project_id}"
        
        return video_info
        
    except Exception as e:
        logger.error(f"Get video info error: {e}")
        return {
            "available_videos": [],
            "has_videos": False,
            "video_count": 0,
            "error": str(e)
        }


def _generate_video_background(job_id: str, project_id: str):
    """后台视频生成任务"""
    try:
        # 更新任务状态
        active_jobs[job_id]["status"] = "processing"
        active_jobs[job_id]["current_step"] = "Generating script"
        active_jobs[job_id]["progress"] = 0.1
        
        # 生成完整视频
        result = video_pipeline.generate_complete_video(project_id)
        
        # 更新任务状态
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["current_step"] = "Video generation completed"
        active_jobs[job_id]["progress"] = 1.0
        active_jobs[job_id]["result"] = result
        
        logger.info(f"Video generation completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Background video generation failed for job {job_id}: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)