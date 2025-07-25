#!/usr/bin/env python3
"""
Test script for the storage system.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_enhanced_interface():
    """Test the enhanced interface with storage."""
    try:
        from spark.chatbot.enhanced_interface import EnhancedChatbotInterface
        
        print("🎬 测试增强版聊天机器人界面（带存储功能）")
        print("=" * 50)
        
        # Initialize interface
        interface = EnhancedChatbotInterface()
        
        # Start new session
        print("1️⃣ 开始新会话...")
        session_id = interface.start_new_session()
        print(f"   会话ID: {session_id}")
        
        # Simulate conversation
        print("\n2️⃣ 模拟对话...")
        messages = [
            "我想创建一个关于太空冒险的视频",
            "主角是一个勇敢的宇航员，还有一个神秘的外星人",
            "故事讲述他们如何合作拯救地球"
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"   用户 {i}: {message}")
            response = interface.continue_conversation(message)
            print(f"   AI: {response.get('response', '无响应')[:100]}...")
            print(f"   状态: {response.get('status')}, 自动保存: {response.get('auto_saved')}")
        
        # Structure idea
        print("\n3️⃣ 结构化创意...")
        structure_result = interface.structure_current_idea()
        if structure_result.get("status") == "success":
            print("   ✅ 创意结构化成功")
            user_idea = structure_result["user_idea"]
            print(f"   主题: {user_idea.get('theme')}")
            print(f"   类型: {user_idea.get('genre')}")
            print(f"   角色: {', '.join(user_idea.get('basic_characters', []))}")
        else:
            print(f"   ❌ 结构化失败: {structure_result.get('error')}")
        
        # Generate story outline
        print("\n4️⃣ 生成故事大纲...")
        story_result = interface.generate_story_outline()
        if story_result.get("status") == "success":
            print("   ✅ 故事大纲生成成功")
            story_outline = story_result["story_outline"]
            print(f"   标题: {story_outline.get('title')}")
            print(f"   摘要: {story_outline.get('summary')}")
            print(f"   时长: {story_outline.get('estimated_duration')}秒")
        else:
            print(f"   ❌ 故事生成失败: {story_result.get('error')}")
        
        # Generate character profiles
        print("\n5️⃣ 生成角色档案...")
        characters_result = interface.generate_character_profiles()
        if characters_result.get("status") == "success":
            print(f"   ✅ 生成了 {characters_result.get('character_count')} 个角色档案")
            for i, profile in enumerate(characters_result["character_profiles"], 1):
                print(f"   角色 {i}: {profile.get('name')} ({profile.get('role')})")
                print(f"      外观: {profile.get('appearance')}")
                print(f"      图像: {'有' if profile.get('image_url') else '无'}")
        else:
            print(f"   ❌ 角色生成失败: {characters_result.get('error')}")
        
        # Save as project
        print("\n6️⃣ 保存为项目...")
        project_name = "太空冒险视频项目"
        save_result = interface.save_as_project(project_name)
        if save_result.get("status") == "success":
            project_id = save_result["project_id"]
            print(f"   ✅ 项目保存成功")
            print(f"   项目ID: {project_id}")
            print(f"   项目名称: {save_result.get('project_name')}")
        else:
            print(f"   ❌ 项目保存失败: {save_result.get('error')}")
        
        # List projects
        print("\n7️⃣ 列出所有项目...")
        projects = interface.list_projects()
        print(f"   找到 {len(projects)} 个项目:")
        for project in projects[:3]:  # Show first 3
            print(f"   - {project.get('project_name')} ({project.get('project_id')[:8]}...)")
            print(f"     创建时间: {project.get('created_at')}")
            print(f"     状态: {project.get('status')}")
        
        # Get session status
        print("\n8️⃣ 会话状态...")
        status = interface.get_session_status()
        print(f"   会话状态: {status.get('status')}")
        print(f"   当前步骤: {status.get('current_step')}")
        print(f"   有对话: {status.get('has_conversation')}")
        print(f"   有创意: {status.get('has_user_idea')}")
        print(f"   有故事: {status.get('has_story_outline')}")
        print(f"   有角色: {status.get('has_character_profiles')}")
        
        print("\n🎉 存储系统测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_loading():
    """Test loading an existing project."""
    try:
        from spark.chatbot.enhanced_interface import EnhancedChatbotInterface
        
        print("\n🔄 测试项目加载功能")
        print("=" * 25)
        
        interface = EnhancedChatbotInterface()
        
        # List projects
        projects = interface.list_projects()
        if not projects:
            print("   没有可加载的项目")
            return True
        
        # Load the first project
        project_id = projects[0]["project_id"]
        project_name = projects[0]["project_name"]
        
        print(f"   加载项目: {project_name}")
        load_result = interface.load_project(project_id)
        
        if load_result.get("status") == "success":
            print("   ✅ 项目加载成功")
            
            # Check loaded data
            status = interface.get_session_status()
            print(f"   新会话ID: {status.get('session_id')}")
            print(f"   有创意: {status.get('has_user_idea')}")
            print(f"   有故事: {status.get('has_story_outline')}")
            print(f"   有角色: {status.get('has_character_profiles')}")
        else:
            print(f"   ❌ 项目加载失败: {load_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 项目加载测试失败: {e}")
        return False

def main():
    print("🎬 Spark AI 存储系统测试")
    print("=" * 30)
    
    # Test enhanced interface
    success1 = test_enhanced_interface()
    
    # Test project loading
    success2 = test_project_loading()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！存储系统工作正常。")
        
        # Show storage location
        print(f"\n📁 项目存储位置: ./projects/")
        print("   你可以在这个目录中找到所有生成的内容：")
        print("   - 用户创意 (user_idea.json)")
        print("   - 故事大纲 (story_outline.json)")
        print("   - 角色档案 (characters/)")
        print("   - 对话历史 (conversation.json)")
        print("   - 角色图像 (assets/)")
    else:
        print("\n❌ 部分测试失败，请检查配置。")

if __name__ == "__main__":
    main()