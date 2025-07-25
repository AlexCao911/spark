#!/usr/bin/env python3
"""
Spark AI Flask API客户端示例

这个脚本演示如何使用Spark AI Flask API进行完整的视频创意生成流程。
"""

import requests
import json
import time
from typing import Dict, Any


class SparkAIClient:
    """Spark AI API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session_id = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"   错误详情: {error_data}")
                except:
                    print(f"   响应内容: {e.response.text}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict:
        """健康检查"""
        return self._make_request("GET", "/api/health")
    
    def get_session_info(self) -> Dict:
        """获取会话信息"""
        result = self._make_request("GET", "/api/session/info")
        if 'session_id' in result:
            self.session_id = result['session_id']
        return result
    
    def send_message(self, message: str, is_first_message: bool = False) -> Dict:
        """发送消息到聊天机器人"""
        return self._make_request("POST", "/api/chat/send", json={
            "message": message,
            "is_first_message": is_first_message
        })
    
    def get_chat_history(self) -> Dict:
        """获取聊天历史"""
        return self._make_request("GET", "/api/chat/history")
    
    def reset_chat(self) -> Dict:
        """重置聊天会话"""
        return self._make_request("POST", "/api/chat/reset")
    
    def structure_idea(self) -> Dict:
        """结构化用户创意"""
        return self._make_request("POST", "/api/content/structure")
    
    def generate_story_outline(self, user_idea: Dict) -> Dict:
        """生成故事大纲"""
        return self._make_request("POST", "/api/content/story/generate", json={
            "user_idea": user_idea
        })
    
    def generate_characters(self, user_idea: Dict) -> Dict:
        """生成角色档案"""
        return self._make_request("POST", "/api/content/characters/generate", json={
            "user_idea": user_idea
        })
    
    def create_project(self, user_idea: Dict, story_outline: Dict, 
                      character_profiles: list, project_name: str = "") -> Dict:
        """创建项目（确认内容）"""
        return self._make_request("POST", "/api/projects", json={
            "user_idea": user_idea,
            "story_outline": story_outline,
            "character_profiles": character_profiles,
            "project_name": project_name
        })
    
    def list_projects(self, page: int = 1, per_page: int = 10) -> Dict:
        """获取项目列表"""
        return self._make_request("GET", f"/api/projects?page={page}&per_page={per_page}")
    
    def get_project(self, project_id: str) -> Dict:
        """获取特定项目"""
        return self._make_request("GET", f"/api/projects/{project_id}")
    
    def delete_project(self, project_id: str) -> Dict:
        """删除项目"""
        return self._make_request("DELETE", f"/api/projects/{project_id}")


def demo_complete_workflow():
    """演示完整的API工作流程"""
    print("🎬 Spark AI API客户端演示")
    print("=" * 50)
    
    # 创建客户端
    client = SparkAIClient()
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    health = client.health_check()
    if 'error' in health:
        print("❌ API服务器不可用，请确保服务器正在运行")
        return
    
    print(f"✅ API服务器状态: {health['status']}")
    print(f"   版本: {health['version']}")
    
    # 2. 获取会话信息
    print("\n2. 获取会话信息...")
    session_info = client.get_session_info()
    print(f"✅ 会话ID: {session_info.get('session_id', 'N/A')[:8]}...")
    
    # 3. 聊天交互
    print("\n3. 开始聊天交互...")
    
    messages = [
        ("我想制作一个关于太空探索的科幻视频", True),
        ("主角是一名勇敢的女宇航员，她发现了一个神秘的外星信号"),
        ("故事应该包含友谊、勇气和科学发现的主题"),
        ("视频时长大约3分钟，面向成年观众"),
        ("视觉风格要电影级别的，氛围紧张刺激")
    ]
    
    for i, (message, *args) in enumerate(messages, 1):
        is_first = args[0] if args else False
        print(f"   👤 用户: {message}")
        
        response = client.send_message(message, is_first)
        if 'error' not in response:
            print(f"   🤖 助手: {response.get('response', 'N/A')[:100]}...")
            if response.get('is_complete'):
                print("   ✅ 创意信息收集完成！")
                break
        else:
            print(f"   ❌ 错误: {response['error']}")
        
        time.sleep(1)  # 避免请求过快
    
    # 4. 结构化创意
    print("\n4. 结构化用户创意...")
    structure_result = client.structure_idea()
    
    if 'error' not in structure_result:
        user_idea = structure_result['user_idea']
        validation = structure_result['validation']
        
        print(f"✅ 创意结构化成功")
        print(f"   主题: {user_idea.get('theme', 'N/A')}")
        print(f"   类型: {user_idea.get('genre', 'N/A')}")
        print(f"   完整性: {validation.get('completeness_score', 0):.1%}")
    else:
        print(f"❌ 结构化失败: {structure_result['error']}")
        return
    
    # 5. 生成故事大纲
    print("\n5. 生成故事大纲...")
    story_result = client.generate_story_outline(user_idea)
    
    if 'error' not in story_result:
        story_outline = story_result['story_outline']
        print(f"✅ 故事大纲生成成功")
        print(f"   标题: {story_outline.get('title', 'N/A')}")
        print(f"   摘要: {story_outline.get('summary', 'N/A')[:100]}...")
        print(f"   预计时长: {story_outline.get('estimated_duration', 0)}秒")
    else:
        print(f"❌ 生成故事大纲失败: {story_result['error']}")
        return
    
    # 6. 生成角色档案
    print("\n6. 生成角色档案...")
    characters_result = client.generate_characters(user_idea)
    
    if 'error' not in characters_result:
        character_profiles = characters_result['character_profiles']
        print(f"✅ 角色档案生成成功")
        print(f"   角色数量: {len(character_profiles)}")
        
        for char in character_profiles:
            print(f"   - {char.get('name', 'N/A')} ({char.get('role', 'N/A')})")
    else:
        print(f"❌ 生成角色档案失败: {characters_result['error']}")
        return
    
    # 7. 创建项目
    print("\n7. 创建项目...")
    project_result = client.create_project(
        user_idea=user_idea,
        story_outline=story_outline,
        character_profiles=character_profiles,
        project_name="太空探索 - API演示"
    )
    
    if 'error' not in project_result:
        project_id = project_result['project_id']
        print(f"✅ 项目创建成功")
        print(f"   项目ID: {project_id[:8]}...")
        print(f"   项目名称: {project_result['project_name']}")
    else:
        print(f"❌ 创建项目失败: {project_result['error']}")
        return
    
    # 8. 验证项目
    print("\n8. 验证项目...")
    project_data = client.get_project(project_id)
    
    if 'error' not in project_data:
        project = project_data['project']
        print(f"✅ 项目验证成功")
        print(f"   用户确认: {project.get('user_confirmed', False)}")
        print(f"   状态: {project.get('status', 'N/A')}")
    else:
        print(f"❌ 项目验证失败: {project_data['error']}")
    
    # 9. 列出所有项目
    print("\n9. 列出所有项目...")
    projects_result = client.list_projects()
    
    if 'error' not in projects_result:
        projects = projects_result['projects']
        print(f"✅ 找到 {len(projects)} 个项目")
        
        for project in projects:
            print(f"   - {project.get('project_name', 'N/A')} "
                  f"({project.get('project_id', 'N/A')[:8]}...)")
    else:
        print(f"❌ 获取项目列表失败: {projects_result['error']}")
    
    # 10. 清理演示数据
    print(f"\n10. 清理演示数据...")
    cleanup = input(f"是否删除演示项目 '{project_id[:8]}...'? (y/N): ").strip().lower()
    
    if cleanup in ['y', 'yes']:
        delete_result = client.delete_project(project_id)
        if 'error' not in delete_result:
            print("✅ 演示项目已删除")
        else:
            print(f"❌ 删除失败: {delete_result.get('message', 'Unknown error')}")
    else:
        print("📁 演示项目已保留")
    
    print("\n🎉 API演示完成！")


def interactive_chat():
    """交互式聊天演示"""
    print("💬 交互式聊天演示")
    print("输入 'quit' 退出，'reset' 重置会话")
    print("-" * 30)
    
    client = SparkAIClient()
    
    # 健康检查
    health = client.health_check()
    if 'error' in health:
        print("❌ API服务器不可用")
        return
    
    is_first_message = True
    
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'reset':
                result = client.reset_chat()
                print("🔄 会话已重置")
                is_first_message = True
                continue
            elif not user_input:
                continue
            
            response = client.send_message(user_input, is_first_message)
            
            if 'error' not in response:
                print(f"🤖 助手: {response.get('response', 'N/A')}")
                
                if response.get('is_complete'):
                    print("✅ 创意信息收集完成！可以开始生成内容了。")
                elif response.get('missing_elements'):
                    missing = ', '.join(response['missing_elements'])
                    print(f"📝 还需要: {missing}")
                
                is_first_message = False
            else:
                print(f"❌ 错误: {response['error']}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
    
    print("\n👋 再见！")


def main():
    """主函数"""
    print("🚀 Spark AI Flask API 客户端")
    print("选择演示模式:")
    print("1. 完整工作流程演示")
    print("2. 交互式聊天")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-3): ").strip()
            
            if choice == '1':
                demo_complete_workflow()
                break
            elif choice == '2':
                interactive_chat()
                break
            elif choice == '3':
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 1、2 或 3")
        
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")


if __name__ == '__main__':
    main()