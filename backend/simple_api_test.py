#!/usr/bin/env python3
"""
简单的API测试脚本
"""

import requests
import json

API_BASE = "http://localhost:8001/api"

def test_basic_endpoints():
    """测试基本端点"""
    print("🔍 测试基本API端点...")
    
    # 1. 健康检查
    print("\n1. 健康检查:")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   服务状态: {data['status']}")
            print(f"   版本: {data['version']}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 2. 项目列表
    print("\n2. 项目列表:")
    try:
        response = requests.get(f"{API_BASE}/projects")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            projects = data['projects']
            print(f"   找到 {len(projects)} 个项目")
            if projects:
                project = projects[0]
                print(f"   第一个项目: {project['project_name']} ({project['project_id']})")
                return project['project_id']
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    return None

def test_project_content(project_id):
    """测试项目内容获取"""
    if not project_id:
        print("⚠️ 没有可用的项目ID")
        return
    
    print(f"\n🎯 测试项目内容 (ID: {project_id})")
    
    # 测试大纲
    print("\n3. 项目大纲:")
    try:
        response = requests.get(f"{API_BASE}/content/project/{project_id}/outline")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            outline = data['outline']
            print(f"   标题: {outline['title']}")
            print(f"   概要长度: {len(outline['summary'])} 字符")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 测试角色
    print("\n4. 项目角色:")
    try:
        response = requests.get(f"{API_BASE}/content/project/{project_id}/characters")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            characters = data['characters']
            print(f"   找到 {len(characters)} 个角色")
            for char in characters:
                print(f"     - {char['name']}: {char['appearance']}")
                if char.get('image_url'):
                    print(f"       图片: {char['image_url'][:50]}...")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 测试视频
    print("\n5. 项目视频:")
    try:
        response = requests.get(f"{API_BASE}/video/project/{project_id}/videos")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            video_info = data['video_info']
            if video_info['has_videos']:
                print(f"   找到 {video_info['video_count']} 个视频")
                for video in video_info['available_videos']:
                    print(f"     - {video['type']}: {video['filename']} ({video['size_mb']}MB)")
            else:
                print("   该项目没有视频")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {e}")

def test_chat():
    """测试聊天功能"""
    print("\n💬 测试聊天功能:")
    
    session = requests.Session()
    
    # 重置会话
    try:
        response = session.post(f"{API_BASE}/chat/reset")
        print(f"   重置会话状态码: {response.status_code}")
    except Exception as e:
        print(f"   重置会话异常: {e}")
    
    # 发送消息
    try:
        message_data = {
            "message": "Hello, I want to create a video",
            "is_first_message": True
        }
        response = session.post(f"{API_BASE}/chat/send", json=message_data)
        print(f"   发送消息状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   机器人状态: {data.get('status', 'unknown')}")
            print(f"   回复: {data.get('response', 'no response')[:100]}...")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   发送消息异常: {e}")

def main():
    """主函数"""
    print("🚀 简单API测试")
    print("=" * 50)
    
    # 测试基本端点
    project_id = test_basic_endpoints()
    
    # 测试项目内容
    test_project_content(project_id)
    
    # 测试聊天功能
    test_chat()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print(f"\n🌐 前端示例: file://{__file__.replace('simple_api_test.py', 'frontend_example.html')}")

if __name__ == "__main__":
    main()