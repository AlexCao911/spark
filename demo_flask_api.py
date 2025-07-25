#!/usr/bin/env python3
"""
Flask API演示脚本

这个脚本演示如何启动和测试Spark AI Flask API。
"""

import subprocess
import time
import requests
import threading
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_api_server():
    """启动API服务器"""
    print("🚀 启动Flask API服务器...")
    
    try:
        # 启动服务器进程
        process = subprocess.Popen([
            sys.executable, 'run_api.py', 
            '--config', 'development',
            '--port', '5001'  # 使用不同端口避免冲突
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(3)
        
        # 检查服务器是否启动成功
        try:
            response = requests.get('http://localhost:5001/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ API服务器启动成功！")
                return process
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                process.terminate()
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到服务器: {str(e)}")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ 启动服务器失败: {str(e)}")
        return None


def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:5001"
    
    print("\n📋 测试API端点...")
    
    # 测试健康检查
    print("\n1. 健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data['status']}")
            print(f"   版本: {data['version']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {str(e)}")
    
    # 测试会话信息
    print("\n2. 会话信息...")
    try:
        response = requests.get(f"{base_url}/api/session/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 会话信息获取成功")
            print(f"   会话ID: {data['session_id'][:8]}...")
            session_id = data['session_id']
        else:
            print(f"❌ 会话信息获取失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 会话信息错误: {str(e)}")
        return
    
    # 测试API文档
    print("\n3. API文档...")
    try:
        response = requests.get(f"{base_url}/api/docs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API文档获取成功")
            print(f"   标题: {data['title']}")
            print(f"   端点数量: {len(data['endpoints'])}")
        else:
            print(f"❌ API文档获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档错误: {str(e)}")
    
    # 测试聊天功能
    print("\n4. 聊天功能...")
    try:
        # 创建会话
        session = requests.Session()
        
        # 发送第一条消息
        response = session.post(f"{base_url}/api/chat/send", json={
            "message": "我想制作一个关于太空探索的科幻视频",
            "is_first_message": True
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 聊天消息发送成功")
            print(f"   响应: {data.get('response', 'N/A')[:100]}...")
            print(f"   状态: {data.get('status', 'N/A')}")
        else:
            print(f"❌ 聊天消息发送失败: {response.status_code}")
            
        # 获取聊天历史
        response = session.get(f"{base_url}/api/chat/history")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 聊天历史获取成功")
            print(f"   消息数量: {len(data.get('history', []))}")
        else:
            print(f"❌ 聊天历史获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 聊天功能错误: {str(e)}")
    
    # 测试项目管理
    print("\n5. 项目管理...")
    try:
        response = requests.get(f"{base_url}/api/projects")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 项目列表获取成功")
            print(f"   项目数量: {len(data.get('projects', []))}")
        else:
            print(f"❌ 项目列表获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 项目管理错误: {str(e)}")
    
    # 测试错误处理
    print("\n6. 错误处理...")
    try:
        response = requests.get(f"{base_url}/api/nonexistent")
        if response.status_code == 404:
            data = response.json()
            print(f"✅ 404错误处理正确")
            print(f"   错误信息: {data.get('error', 'N/A')}")
        else:
            print(f"❌ 404错误处理异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 错误处理测试错误: {str(e)}")


def main():
    """主函数"""
    print("🎬 Spark AI Flask API 演示")
    print("=" * 50)
    
    # 启动API服务器
    server_process = start_api_server()
    
    if not server_process:
        print("❌ 无法启动API服务器，演示终止")
        return
    
    try:
        # 测试API端点
        test_api_endpoints()
        
        print("\n🎉 API演示完成！")
        print("\n💡 你可以通过以下方式继续测试:")
        print("   - 浏览器访问: http://localhost:5001/api/docs")
        print("   - 健康检查: http://localhost:5001/api/health")
        print("   - 使用客户端: python api_client_example.py")
        
        # 询问是否保持服务器运行
        keep_running = input("\n是否保持服务器运行以便进一步测试? (y/N): ").strip().lower()
        
        if keep_running in ['y', 'yes']:
            print("🔄 服务器继续运行中...")
            print("   按 Ctrl+C 停止服务器")
            
            try:
                # 等待用户中断
                server_process.wait()
            except KeyboardInterrupt:
                print("\n👋 用户中断，停止服务器...")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断演示")
    
    finally:
        # 停止服务器
        if server_process:
            print("🛑 停止API服务器...")
            server_process.terminate()
            
            # 等待进程结束
            try:
                server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  强制终止服务器...")
                server_process.kill()


if __name__ == '__main__':
    main()