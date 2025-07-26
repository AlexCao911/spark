#!/usr/bin/env python3
"""
API集成测试脚本 - 测试聊天、大纲、角色图片和视频传递功能
"""

import requests
import json
import time
from pathlib import Path

# API配置
API_BASE = "http://localhost:8000/api"
session = requests.Session()


def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = session.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器状态: {data['status']}")
            print(f"   版本: {data['version']}")
            print(f"   环境: {data['environment']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def test_chat_functionality():
    """测试聊天功能"""
    print("\n💬 测试聊天功能...")
    
    # 重置会话
    print("  重置聊天会话...")
    response = session.post(f"{API_BASE}/chat/reset")
    if response.status_code == 200:
        print("  ✅ 会话重置成功")
    
    # 发送第一条消息
    print("  发送第一条消息...")
    message_data = {
        "message": "我想制作一个关于太空探险的科幻视频",
        "is_first_message": True
    }
    
    response = session.post(f"{API_BASE}/chat/send", json=message_data)
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ 机器人回复: {data['response'][:100]}...")
        print(f"     状态: {data['status']}")
        return True
    else:
        print(f"  ❌ 发送消息失败: {response.status_code}")
        return False


def test_projects_list():
    """测试项目列表"""
    print("\n📁 测试项目列表...")
    
    response = session.get(f"{API_BASE}/projects")
    if response.status_code == 200:
        data = response.json()
        projects = data['projects']
        print(f"  ✅ 找到 {len(projects)} 个项目")
        
        if projects:
            # 返回第一个项目ID用于后续测试
            project_id = projects[0]['project_id']
            print(f"     使用项目ID进行测试: {project_id}")
            return project_id
        else:
            print("  ⚠️ 没有找到项目，请先创建一些项目")
            return None
    else:
        print(f"  ❌ 获取项目列表失败: {response.status_code}")
        return None


def test_project_outline(project_id):
    """测试项目大纲获取"""
    print(f"\n📖 测试项目大纲获取 (项目ID: {project_id})...")
    
    response = session.get(f"{API_BASE}/content/project/{project_id}/outline")
    if response.status_code == 200:
        data = response.json()
        outline = data['outline']
        print(f"  ✅ 大纲标题: {outline['title']}")
        print(f"     概要长度: {len(outline['summary'])} 字符")
        print(f"     预计时长: {outline['estimated_duration']} 秒")
        return True
    else:
        print(f"  ❌ 获取大纲失败: {response.status_code}")
        if response.status_code == 404:
            print("     项目大纲不存在")
        return False


def test_project_characters(project_id):
    """测试项目角色获取"""
    print(f"\n👥 测试项目角色获取 (项目ID: {project_id})...")
    
    response = session.get(f"{API_BASE}/content/project/{project_id}/characters")
    if response.status_code == 200:
        data = response.json()
        characters = data['characters']
        print(f"  ✅ 找到 {len(characters)} 个角色")
        
        for i, character in enumerate(characters):
            print(f"     角色 {i+1}: {character['name']}")
            print(f"       外观: {character['appearance']}")
            print(f"       图片: {'有' if character.get('image_url') else '无'}")
            
            # 测试单个角色图片获取
            if character.get('image_url'):
                img_response = session.get(f"{API_BASE}/content/project/{project_id}/character/{character['name']}/image")
                if img_response.status_code == 200:
                    img_data = img_response.json()
                    print(f"       图片URL: {img_data['image_url'][:50]}...")
        
        return True
    else:
        print(f"  ❌ 获取角色失败: {response.status_code}")
        return False


def test_project_videos(project_id):
    """测试项目视频获取"""
    print(f"\n🎥 测试项目视频获取 (项目ID: {project_id})...")
    
    response = session.get(f"{API_BASE}/video/project/{project_id}/videos")
    if response.status_code == 200:
        data = response.json()
        video_info = data['video_info']
        
        if video_info['has_videos']:
            print(f"  ✅ 找到 {video_info['video_count']} 个视频")
            
            for video in video_info['available_videos']:
                print(f"     视频类型: {video['type']}")
                print(f"       文件名: {video['filename']}")
                print(f"       大小: {video['size_mb']} MB")
                print(f"       下载URL: {video['download_url']}")
                print(f"       流媒体URL: {video['stream_url']}")
            
            # 测试视频流媒体访问
            if video_info['available_videos']:
                first_video = video_info['available_videos'][0]
                stream_url = f"{API_BASE}{first_video['stream_url']}"
                
                print(f"  测试视频流媒体访问...")
                stream_response = session.head(stream_url)  # 使用HEAD请求测试
                if stream_response.status_code == 200:
                    print(f"  ✅ 视频流媒体可访问")
                    print(f"     Content-Type: {stream_response.headers.get('Content-Type')}")
                    print(f"     Content-Length: {stream_response.headers.get('Content-Length')} bytes")
                else:
                    print(f"  ❌ 视频流媒体访问失败: {stream_response.status_code}")
            
            return True
        else:
            print("  ⚠️ 该项目没有视频文件")
            return False
    else:
        print(f"  ❌ 获取视频信息失败: {response.status_code}")
        return False


def test_complete_project_content(project_id):
    """测试完整项目内容获取"""
    print(f"\n📦 测试完整项目内容获取 (项目ID: {project_id})...")
    
    response = session.get(f"{API_BASE}/content/project/{project_id}/complete")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ 项目名称: {data['project_name']}")
        print(f"     创建时间: {data['created_at']}")
        print(f"     状态: {data['status']}")
        print(f"     用户创意主题: {data['user_idea'].get('theme', 'N/A')}")
        print(f"     故事大纲标题: {data['story_outline'].get('title', 'N/A')}")
        print(f"     角色数量: {len(data['character_profiles'])}")
        return True
    else:
        print(f"  ❌ 获取完整内容失败: {response.status_code}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始API集成测试")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health_check():
        print("❌ 服务器不可用，请先启动API服务器")
        return
    
    # 2. 测试聊天功能
    test_chat_functionality()
    
    # 3. 获取项目列表
    project_id = test_projects_list()
    if not project_id:
        print("⚠️ 没有可用项目，跳过后续测试")
        return
    
    # 4. 测试项目相关功能
    test_project_outline(project_id)
    test_project_characters(project_id)
    test_project_videos(project_id)
    test_complete_project_content(project_id)
    
    print("\n" + "=" * 50)
    print("🎉 API集成测试完成")
    print("\n📋 前端集成指南:")
    print("1. 聊天对话: POST /api/chat/send")
    print("2. 获取大纲: GET /api/content/project/{id}/outline")
    print("3. 获取角色: GET /api/content/project/{id}/characters")
    print("4. 获取视频: GET /api/video/project/{id}/videos")
    print("5. 视频流媒体: GET /api/video/stream/{id}/{type}")
    print("6. 视频下载: GET /api/video/download/{id}/{type}")
    print(f"\n🌐 前端示例页面: file://{Path('frontend_example.html').absolute()}")


if __name__ == "__main__":
    main()