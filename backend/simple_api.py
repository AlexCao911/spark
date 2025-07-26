#!/usr/bin/env python3
"""
简化的API服务器 - 专注于核心功能
"""

import json
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['*'])

# 项目目录
PROJECTS_DIR = Path("projects/projects")

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-simple',
        'environment': 'development'
    })

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """获取项目列表"""
    try:
        projects = []
        
        for project_dir in PROJECTS_DIR.iterdir():
            if project_dir.is_dir():
                approved_file = project_dir / "approved_content.json"
                if approved_file.exists():
                    try:
                        with open(approved_file, 'r', encoding='utf-8') as f:
                            project_data = json.load(f)
                            projects.append({
                                'project_id': project_data.get('project_id', project_dir.name),
                                'project_name': project_data.get('project_name', '未命名项目'),
                                'status': project_data.get('status', 'unknown'),
                                'created_at': project_data.get('created_at', ''),
                                'character_count': len(project_data.get('character_profiles', []))
                            })
                    except Exception as e:
                        print(f"读取项目 {project_dir.name} 失败: {e}")
        
        return jsonify({
            'status': 'success',
            'projects': projects,
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': len(projects),
                'pages': 1
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/project/<project_id>/outline', methods=['GET'])
def get_project_outline(project_id):
    """获取项目大纲"""
    try:
        project_dir = PROJECTS_DIR / project_id
        outline_file = project_dir / "story_outline.json"
        
        if not outline_file.exists():
            return jsonify({'error': '项目大纲不存在'}), 404
        
        with open(outline_file, 'r', encoding='utf-8') as f:
            outline_data = json.load(f)
        
        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'outline': outline_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/project/<project_id>/characters', methods=['GET'])
def get_project_characters(project_id):
    """获取项目角色"""
    try:
        project_dir = PROJECTS_DIR / project_id
        characters_file = project_dir / "characters.json"
        character_images_file = project_dir / "character_images.json"
        
        if not characters_file.exists():
            return jsonify({'error': '项目角色信息不存在'}), 404
        
        # 读取角色基本信息
        with open(characters_file, 'r', encoding='utf-8') as f:
            characters_data = json.load(f)
        
        # 读取角色图片信息
        character_images = []
        if character_images_file.exists():
            with open(character_images_file, 'r', encoding='utf-8') as f:
                character_images = json.load(f)
        
        # 合并角色信息和图片
        for character in characters_data:
            character_name = character.get('name')
            for img_info in character_images:
                if img_info.get('character_name') == character_name:
                    character['image_url'] = img_info.get('image_url')
                    character['visual_tags'] = img_info.get('visual_tags', [])
                    break
        
        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'characters': characters_data,
            'character_count': len(characters_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/project/<project_id>/complete', methods=['GET'])
def get_complete_project_content(project_id):
    """获取完整项目内容"""
    try:
        project_dir = PROJECTS_DIR / project_id
        approved_content_file = project_dir / "approved_content.json"
        
        if not approved_content_file.exists():
            return jsonify({'error': '项目内容不存在'}), 404
        
        with open(approved_content_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'project_name': project_data.get('project_name', ''),
            'created_at': project_data.get('created_at', ''),
            'user_idea': project_data.get('user_idea', {}),
            'story_outline': project_data.get('story_outline', {}),
            'character_profiles': project_data.get('character_profiles', []),
            'status': project_data.get('status', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/project/<project_id>/videos', methods=['GET'])
def get_project_videos(project_id):
    """获取项目视频信息"""
    try:
        project_dir = PROJECTS_DIR / project_id / "final_videos"
        
        if not project_dir.exists():
            return jsonify({
                'success': False,
                'error': 'No videos found for this project'
            }), 404
        
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
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "video_info": video_info,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/video/stream/<project_id>/<video_type>', methods=['GET'])
def stream_video(project_id, video_type):
    """流式传输视频"""
    try:
        project_dir = PROJECTS_DIR / project_id / "final_videos"
        
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
            conditional=True
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/video/download/<project_id>/<video_type>', methods=['GET'])
def download_video(project_id, video_type):
    """下载视频"""
    try:
        project_dir = PROJECTS_DIR / project_id / "final_videos"
        
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
            as_attachment=True,
            download_name=f"{project_id}_{video_type}.mp4",
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/video/thumbnail/<project_id>', methods=['GET'])
def get_thumbnail(project_id):
    """获取视频缩略图"""
    try:
        project_dir = PROJECTS_DIR / project_id / "final_videos"
        
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
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    """简化的聊天功能"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # 简单的模拟回复
        response_text = f"收到您的消息: '{message}'. 这是一个简化的API演示。要完整的聊天功能，请使用完整版API。"
        
        return jsonify({
            'status': 'engaged',
            'response': response_text,
            'is_complete': False,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    """重置聊天"""
    return jsonify({
        'status': 'success',
        'message': '会话已重置（简化版）',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 启动简化API服务器...")
    print("📍 地址: http://localhost:8001")
    print("📚 端点:")
    print("   GET  /api/health - 健康检查")
    print("   GET  /api/projects - 项目列表")
    print("   GET  /api/content/project/{id}/outline - 项目大纲")
    print("   GET  /api/content/project/{id}/characters - 项目角色")
    print("   GET  /api/video/project/{id}/videos - 项目视频")
    print("   GET  /api/video/stream/{id}/{type} - 视频流")
    print("   GET  /api/video/download/{id}/{type} - 视频下载")
    print("   POST /api/chat/send - 聊天（简化版）")
    
    app.run(host='0.0.0.0', port=8001, debug=True)