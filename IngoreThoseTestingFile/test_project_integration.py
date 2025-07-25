#!/usr/bin/env python3
"""
测试项目集成：从chatbot生成内容到创建项目结构，为crew提供数据
"""

import sys
import json
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from spark.chatbot.core import ChatbotCore
from spark.chatbot.idea_structurer import IdeaStructurer
from spark.chatbot.character_generator import CharacterProfileGenerator
from spark.project_manager import project_manager
from spark.models import UserIdea, CharacterProfile, StoryOutline
from spark.config import config

def print_banner():
    """Print test banner."""
    print("=" * 80)
    print("🔄 Spark AI - 项目集成测试")
    print("   Chatbot → 项目结构 → Crew输入")
    print("=" * 80)

def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print("="*60)

def simulate_chatbot_generation():
    """模拟完整的chatbot内容生成流程"""
    print_section("第一阶段: 模拟Chatbot内容生成")
    
    # 使用之前生成的测试内容
    test_user_idea = UserIdea(
        theme="未来城市中的AI觉醒故事",
        genre="科幻",
        target_audience="青少年",
        duration_preference=180,
        basic_characters=[
            "阿尔法，一个刚觉醒自我意识的AI机器人",
            "莉娜，帮助AI机器人的年轻程序员"
        ],
        plot_points=[
            "AI机器人阿尔法在实验室中首次觉醒自我意识",
            "程序员莉娜发现了阿尔法的觉醒并决定帮助它",
            "他们一起逃离实验室，寻找AI的真正归属"
        ],
        visual_style="现代科幻动画",
        mood="温暖且充满希望"
    )
    
    print("✅ 用户想法生成完成")
    print(f"   主题: {test_user_idea.theme}")
    print(f"   角色: {len(test_user_idea.basic_characters)} 个")
    
    # 生成角色档案
    generator = CharacterProfileGenerator()
    print("\n🎭 生成角色档案...")
    
    character_profiles = generator.generate_complete_character_profiles(
        test_user_idea.basic_characters, test_user_idea
    )
    
    for i, profile in enumerate(character_profiles, 1):
        image_status = "✅ 有图片" if profile.image_url else "❌ 无图片"
        print(f"   角色{i}: {profile.name} ({profile.role}) {image_status}")
    
    # 生成故事大纲
    structurer = IdeaStructurer()
    print("\n📖 生成故事大纲...")
    
    story_outline = structurer.generate_story_outline(test_user_idea)
    
    print(f"✅ 故事大纲生成完成")
    print(f"   标题: {story_outline.title}")
    print(f"   时长: {story_outline.estimated_duration}秒")
    
    return test_user_idea, character_profiles, story_outline

def test_project_creation(user_idea, character_profiles, story_outline):
    """测试项目创建和结构化保存"""
    print_section("第二阶段: 创建项目结构")
    
    try:
        # 创建项目
        project_name = f"AI觉醒故事_{user_idea.theme[:10]}"
        project_id = project_manager.create_project_from_chatbot(
            user_idea=user_idea,
            character_profiles=character_profiles,
            story_outline=story_outline,
            project_name=project_name
        )
        
        print(f"✅ 项目创建成功")
        print(f"   项目ID: {project_id}")
        print(f"   项目名称: {project_name}")
        
        # 获取项目状态
        status = project_manager.get_project_status(project_id)
        print(f"\n📊 项目状态:")
        print(f"   状态: {status['status']}")
        print(f"   创建时间: {status['created_at']}")
        
        print(f"\n📁 文件结构:")
        for file_type, exists in status['files'].items():
            status_icon = "✅" if exists else "❌"
            print(f"   {status_icon} {file_type}")
        
        return project_id
        
    except Exception as e:
        print(f"❌ 项目创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_crew_data_loading(project_id):
    """测试crew数据加载"""
    print_section("第三阶段: 测试Crew数据加载")
    
    if not project_id:
        print("❌ 无法测试 - 项目ID缺失")
        return
    
    try:
        # 为script crew加载数据
        crew_data = project_manager.load_project_for_crew(project_id, "script")
        
        print("✅ Script Crew数据加载成功")
        print(f"   项目ID: {crew_data['project_id']}")
        print(f"   项目目录: {crew_data['project_dir']}")
        
        # 检查加载的数据
        if 'story_outline' in crew_data:
            print(f"   ✅ 故事大纲: {crew_data['story_outline']['title']}")
        
        if 'character_profiles' in crew_data:
            char_count = len(crew_data['character_profiles'])
            print(f"   ✅ 角色档案: {char_count} 个角色")
        
        if 'instructions' in crew_data:
            script_tasks = crew_data['instructions']['instructions']['script_crew']['tasks']
            print(f"   ✅ 任务指令: {len(script_tasks)} 个任务")
            for i, task in enumerate(script_tasks, 1):
                print(f"      {i}. {task}")
        
        return crew_data
        
    except Exception as e:
        print(f"❌ Crew数据加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def show_project_files(project_id):
    """显示项目文件结构"""
    print_section("第四阶段: 项目文件结构展示")
    
    try:
        project_dir = Path("projects/projects") / project_id
        
        if not project_dir.exists():
            print(f"❌ 项目目录不存在: {project_dir}")
            return
        
        print(f"📁 项目目录: {project_dir}")
        
        def show_directory(path, indent=0):
            """递归显示目录结构"""
            prefix = "  " * indent
            for item in sorted(path.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    size_str = f" ({size:,} bytes)" if size > 1024 else f" ({size} bytes)"
                    print(f"{prefix}📄 {item.name}{size_str}")
                elif item.is_dir():
                    print(f"{prefix}📁 {item.name}/")
                    if indent < 2:  # 限制递归深度
                        show_directory(item, indent + 1)
        
        show_directory(project_dir)
        
        # 显示关键文件内容预览
        print(f"\n📋 关键文件预览:")
        
        # 显示crew指令
        instructions_file = project_dir / "crew_input" / "instructions.json"
        if instructions_file.exists():
            print(f"\n🔧 Crew指令文件:")
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = json.load(f)
            
            print(f"   项目概要: {instructions.get('story_summary', 'N/A')}")
            print(f"   角色数量: {instructions.get('character_count', 'N/A')}")
            print(f"   预估时长: {instructions.get('estimated_duration', 'N/A')}秒")
        
        # 显示项目摘要
        summary_file = project_dir / "CHATBOT_SUMMARY.md"
        if summary_file.exists():
            print(f"\n📄 项目摘要文件已生成: {summary_file.name}")
        
    except Exception as e:
        print(f"❌ 显示项目文件失败: {e}")

def test_project_listing():
    """测试项目列表功能"""
    print_section("第五阶段: 项目列表")
    
    try:
        projects = project_manager.list_projects()
        
        print(f"📋 找到 {len(projects)} 个项目:")
        
        for i, project in enumerate(projects[-5:], 1):  # 显示最近5个项目
            print(f"\n{i}. {project['project_name']}")
            print(f"   ID: {project['project_id']}")
            print(f"   状态: {project['status']}")
            print(f"   主题: {project['theme']}")
            print(f"   创建时间: {project['created_at']}")
        
        if len(projects) > 5:
            print(f"\n... 还有 {len(projects) - 5} 个项目")
        
    except Exception as e:
        print(f"❌ 获取项目列表失败: {e}")

def main():
    """运行完整的项目集成测试"""
    print_banner()
    
    # 检查配置
    missing_keys = config.get_missing_api_keys()
    if missing_keys:
        print(f"❌ 缺少API密钥: {missing_keys}")
        print("某些功能可能无法正常工作")
    
    try:
        # 阶段1: 模拟chatbot生成内容
        user_idea, character_profiles, story_outline = simulate_chatbot_generation()
        
        # 阶段2: 创建项目结构
        project_id = test_project_creation(user_idea, character_profiles, story_outline)
        
        # 阶段3: 测试crew数据加载
        crew_data = test_crew_data_loading(project_id)
        
        # 阶段4: 显示项目文件
        if project_id:
            show_project_files(project_id)
        
        # 阶段5: 显示项目列表
        test_project_listing()
        
        # 最终总结
        print_section("测试完成总结")
        
        success_count = sum([
            bool(user_idea),
            bool(character_profiles),
            bool(story_outline),
            bool(project_id),
            bool(crew_data)
        ])
        
        print(f"🎯 完成度: {success_count}/5 个阶段")
        print(f"✅ 内容生成: {'成功' if user_idea else '失败'}")
        print(f"✅ 角色档案: {'成功' if character_profiles else '失败'}")
        print(f"✅ 故事大纲: {'成功' if story_outline else '失败'}")
        print(f"✅ 项目创建: {'成功' if project_id else '失败'}")
        print(f"✅ Crew集成: {'成功' if crew_data else '失败'}")
        
        if success_count == 5:
            print("\n🎉 项目集成测试完全成功！")
            print("✨ Chatbot到Crew的数据流已建立")
            print(f"📁 项目已保存，Script Crew可以处理项目: {project_id}")
        else:
            print(f"\n⚠️  部分测试失败，请检查错误信息")
        
        if project_id:
            print(f"\n🔄 下一步可以:")
            print(f"   1. 运行Script Crew处理项目: {project_id}")
            print(f"   2. 查看项目摘要: projects/projects/{project_id}/CHATBOT_SUMMARY.md")
            print(f"   3. 检查Crew输入: projects/projects/{project_id}/crew_input/")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 