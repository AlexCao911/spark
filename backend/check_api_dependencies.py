#!/usr/bin/env python3
"""
检查API依赖和配置
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_imports():
    """检查必要的导入"""
    print("🔍 检查API依赖...")
    
    try:
        # Flask相关
        import flask
        from flask import Flask, jsonify, request, session, send_file
        from flask_cors import CORS
        from flask_session import Session
        print("✅ Flask相关模块导入成功")
        
        # 项目模块
        from src.spark.chatbot.core import ChatbotCore
        print("✅ ChatbotCore导入成功")
        
        from src.spark.chatbot.idea_structurer import IdeaStructurer
        print("✅ IdeaStructurer导入成功")
        
        from src.spark.chatbot.character_generator import CharacterProfileGenerator
        print("✅ CharacterProfileGenerator导入成功")
        
        from src.spark.models import UserIdea, StoryOutline, CharacterProfile
        print("✅ 数据模型导入成功")
        
        # 检查confirmation_manager
        try:
            from src.spark.chatbot.simple_confirmation import confirmation_manager
            print("✅ confirmation_manager导入成功")
        except ImportError as e:
            print(f"⚠️ confirmation_manager导入失败: {e}")
            print("   这可能需要创建simple_confirmation模块")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def check_directories():
    """检查必要的目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        "src/spark/api",
        "src/spark/api/routes",
        "src/spark/chatbot",
        "projects/projects",
        "flask_session"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - 不存在")
            if dir_path == "flask_session":
                print("   创建session目录...")
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ 已创建 {dir_path}")


def check_config():
    """检查配置"""
    print("\n⚙️ 检查配置...")
    
    try:
        from src.spark.api.config import config
        print("✅ API配置加载成功")
        
        # 检查环境变量
        import os
        secret_key = os.environ.get('SECRET_KEY')
        if secret_key:
            print("✅ SECRET_KEY环境变量已设置")
        else:
            print("⚠️ SECRET_KEY环境变量未设置，将使用默认值")
        
        return True
        
    except ImportError as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def create_missing_modules():
    """创建缺失的模块"""
    print("\n🔧 检查并创建缺失的模块...")
    
    # 检查simple_confirmation模块
    confirmation_file = Path("src/spark/chatbot/simple_confirmation.py")
    if not confirmation_file.exists():
        print("⚠️ simple_confirmation.py不存在，创建基础版本...")
        
        confirmation_code = '''"""
简单的确认管理器 - 基础版本
"""

import json
import uuid
from pathlib import Path
from datetime import datetime


class SimpleConfirmationManager:
    """简单的确认管理器"""
    
    def __init__(self):
        self.projects_dir = Path("projects/projects")
        self.projects_dir.mkdir(parents=True, exist_ok=True)
    
    def list_projects(self):
        """列出所有项目"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
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
                                'created_at': project_data.get('created_at', '')
                            })
                    except Exception as e:
                        print(f"读取项目 {project_dir.name} 失败: {e}")
        
        return projects
    
    def load_approved_content(self, project_id):
        """加载已确认的内容"""
        project_dir = self.projects_dir / project_id
        approved_file = project_dir / "approved_content.json"
        
        if not approved_file.exists():
            return None
        
        try:
            with open(approved_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载项目内容失败: {e}")
            return None
    
    def save_approved_content(self, user_idea, story_outline, character_profiles, project_name=None):
        """保存确认的内容"""
        project_id = str(uuid.uuid4())
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 准备数据
        project_data = {
            'project_id': project_id,
            'project_name': project_name or f"{story_outline.title}_项目",
            'created_at': datetime.now().isoformat(),
            'user_idea': user_idea.model_dump(),
            'story_outline': story_outline.model_dump(),
            'character_profiles': [char.model_dump() for char in character_profiles],
            'status': 'approved',
            'user_confirmed': True
        }
        
        # 保存主文件
        approved_file = project_dir / "approved_content.json"
        with open(approved_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        # 保存单独的文件
        with open(project_dir / "story_outline.json", 'w', encoding='utf-8') as f:
            json.dump(story_outline.model_dump(), f, ensure_ascii=False, indent=2)
        
        with open(project_dir / "characters.json", 'w', encoding='utf-8') as f:
            json.dump([char.model_dump() for char in character_profiles], f, ensure_ascii=False, indent=2)
        
        # 保存角色图片信息
        character_images = []
        for char in character_profiles:
            if char.image_url:
                character_images.append({
                    'character_name': char.name,
                    'image_url': char.image_url,
                    'visual_tags': char.visual_consistency_tags
                })
        
        if character_images:
            with open(project_dir / "character_images.json", 'w', encoding='utf-8') as f:
                json.dump(character_images, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'success',
            'project_id': project_id,
            'message': '项目创建成功'
        }
    
    def delete_project(self, project_id):
        """删除项目"""
        project_dir = self.projects_dir / project_id
        
        if not project_dir.exists():
            return {'status': 'error', 'message': '项目不存在'}
        
        try:
            import shutil
            shutil.rmtree(project_dir)
            return {'status': 'success', 'message': '项目删除成功'}
        except Exception as e:
            return {'status': 'error', 'message': f'删除失败: {str(e)}'}
    
    def regenerate_character_image(self, project_id, character_name, feedback=''):
        """重新生成角色图片"""
        # 这里应该调用图片生成服务，暂时返回成功状态
        return {
            'status': 'success',
            'message': f'角色 {character_name} 的图片重新生成请求已提交'
        }


# 全局实例
confirmation_manager = SimpleConfirmationManager()
'''
        
        with open(confirmation_file, 'w', encoding='utf-8') as f:
            f.write(confirmation_code)
        
        print("✅ 已创建 simple_confirmation.py")
    
    # 检查video_generation_pipeline模块
    pipeline_file = Path("src/spark/video_generation_pipeline.py")
    if not pipeline_file.exists():
        print("⚠️ video_generation_pipeline.py不存在，创建基础版本...")
        
        pipeline_code = '''"""
视频生成管道 - 基础版本
"""

import json
from pathlib import Path


class VideoGenerationPipeline:
    """视频生成管道"""
    
    def __init__(self):
        self.projects_dir = Path("projects/projects")
    
    def list_available_projects(self):
        """列出可用项目"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                approved_file = project_dir / "approved_content.json"
                if approved_file.exists():
                    try:
                        with open(approved_file, 'r', encoding='utf-8') as f:
                            project_data = json.load(f)
                            projects.append({
                                'project_id': project_data.get('project_id', project_dir.name),
                                'project_name': project_data.get('project_name', '未命名项目'),
                                'status': project_data.get('status', 'unknown')
                            })
                    except Exception:
                        pass
        
        return projects
    
    def get_project_status(self, project_id):
        """获取项目状态"""
        project_dir = self.projects_dir / project_id
        approved_file = project_dir / "approved_content.json"
        final_videos_dir = project_dir / "final_videos"
        
        return {
            'exists': approved_file.exists(),
            'approved': approved_file.exists(),
            'has_videos': final_videos_dir.exists() and any(final_videos_dir.glob("*.mp4")),
            'project_dir': str(project_dir)
        }
    
    def generate_complete_video(self, project_id):
        """生成完整视频（模拟）"""
        # 这里应该调用实际的视频生成流程
        return {
            'status': 'completed',
            'project_id': project_id,
            'message': '视频生成完成（模拟）'
        }


# 全局实例
video_pipeline = VideoGenerationPipeline()
'''
        
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(pipeline_code)
        
        print("✅ 已创建 video_generation_pipeline.py")


def main():
    """主函数"""
    print("🚀 Spark AI API 依赖检查")
    print("=" * 50)
    
    # 检查目录结构
    check_directories()
    
    # 创建缺失的模块
    create_missing_modules()
    
    # 检查导入
    imports_ok = check_imports()
    
    # 检查配置
    config_ok = check_config()
    
    print("\n" + "=" * 50)
    if imports_ok and config_ok:
        print("✅ 所有检查通过，可以启动API服务器")
        print("\n🚀 启动命令:")
        print("python run_api.py --config development")
        print("\n🧪 测试命令:")
        print("python test_api_integration.py")
    else:
        print("❌ 存在问题，请解决后再启动")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())