#!/usr/bin/env python3
"""
Terminal interactive chatbot for Spark AI Video Generation.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from spark.chatbot.core import ChatbotCore
from spark.chatbot.idea_structurer import IdeaStructurer
from spark.chatbot.character_generator import CharacterProfileGenerator
from spark.chatbot.simple_confirmation import confirmation_manager
from spark.config import config

def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("🎬 Spark AI Video Generation - Interactive Chatbot")
    print("=" * 60)
    print("欢迎使用视频创意助手！我将帮助您开发视频创意。")
    print("输入 'quit' 或 'exit' 退出，输入 'reset' 重置对话")
    print("=" * 60)

def print_status(result):
    """Print conversation status."""
    if result.get('status') == 'error':
        print(f"\n❌ 错误: {result.get('error', '未知错误')}")
        return
    
    is_complete = result.get('is_complete', False)
    missing = result.get('missing_elements', [])
    found = result.get('found_elements', [])
    
    print(f"\n📊 对话状态:")
    print(f"   完整性: {'✅ 已完成' if is_complete else '⏳ 进行中'}")
    
    if found:
        print(f"   已识别: {', '.join(found)}")
    
    if missing and not is_complete:
        print(f"   待补充: {', '.join(missing)}")

def generate_complete_project(chatbot, idea_structurer, character_generator):
    """Generate complete project after conversation completion."""
    try:
        print("\n🎯 开始生成完整项目...")
        print("=" * 50)
        
        # Step 1: Structure the conversation into UserIdea
        print("📋 步骤1: 结构化用户创意...")
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chatbot.conversation_manager.messages 
            if msg["role"] in ["user", "assistant"]
        ]
        
        user_idea = idea_structurer.structure_conversation(conversation_history)
        if not user_idea:
            print("❌ 创意结构化失败")
            return None
        
        print(f"✅ 创意结构化成功!")
        print(f"   主题: {user_idea.theme}")
        print(f"   类型: {user_idea.genre}")
        print(f"   角色: {', '.join(user_idea.basic_characters)}")
        print(f"   时长偏好: {user_idea.duration_preference}")
        
        # Step 2: Generate story outline
        print("\n📚 步骤2: 生成故事大纲...")
        story_outline = idea_structurer.generate_story_outline(user_idea)
        if not story_outline:
            print("❌ 故事大纲生成失败")
            return None
        
        print(f"✅ 故事大纲生成成功!")
        print(f"   标题: {story_outline.title}")
        print(f"   摘要: {story_outline.summary}")
        print(f"   预计时长: {story_outline.estimated_duration}秒")
        print(f"   故事长度: {len(story_outline.narrative_text)}字符")
        
        # Step 3: Generate character profiles
        print("\n👥 步骤3: 生成角色档案...")
        character_profiles = character_generator.generate_complete_character_profiles(
            user_idea.basic_characters,
            user_idea
        )
        if not character_profiles:
            print("❌ 角色档案生成失败")
            return None
        
        print(f"✅ 角色档案生成成功!")
        for i, char in enumerate(character_profiles, 1):
            print(f"   角色{i}: {char.name} ({char.role})")
            print(f"     外观: {char.appearance[:50]}...")
            print(f"     性格: {char.personality}")
        
        # Step 4: Save project
        print("\n💾 步骤4: 保存项目...")
        project_name = f"{story_outline.title}_项目"
        result = confirmation_manager.save_approved_content(
            user_idea=user_idea,
            story_outline=story_outline,
            character_profiles=character_profiles,
            project_name=project_name
        )
        
        if result.get("status") == "success":
            project_id = result.get("project_id")
            print(f"✅ 项目保存成功!")
            print(f"   项目ID: {project_id}")
            print(f"   项目名称: {project_name}")
            print(f"   保存路径: projects/{project_id}")
            
            # Show what was created
            print(f"\n📁 已创建文件:")
            print(f"   ✅ approved_content.json - 完整项目数据")
            print(f"   ✅ story_outline.json - 故事大纲")
            print(f"   ✅ characters.json - 角色档案")
            
            return {
                "project_id": project_id,
                "user_idea": user_idea,
                "story_outline": story_outline,
                "character_profiles": character_profiles
            }
        else:
            print(f"❌ 项目保存失败: {result.get('error', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"❌ 项目生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main interactive loop."""
    print_banner()
    
    # Check configuration
    missing_keys = config.get_missing_api_keys()
    if missing_keys:
        print(f"❌ 缺少API密钥: {missing_keys}")
        print("请设置环境变量后重试")
        return
    
    # Initialize components
    try:
        chatbot = ChatbotCore()
        idea_structurer = IdeaStructurer()
        character_generator = CharacterProfileGenerator()
        print("✅ Chatbot初始化成功！")
        print("\n请告诉我您的视频创意想法：")
    except Exception as e:
        print(f"❌ Chatbot初始化失败: {e}")
        return
    
    first_message = True
    
    while True:
        try:
            # Get user input
            if first_message:
                user_input = input("\n👤 您: ").strip()
            else:
                user_input = input("\n👤 您: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！期待您的下次使用！")
                break
            elif user_input.lower() in ['reset', '重置']:
                chatbot.reset_conversation()
                print("\n🔄 对话已重置，请重新开始：")
                first_message = True
                continue
            elif not user_input:
                continue
            
            # Process user input
            if first_message:
                result = chatbot.engage_user(user_input)
                first_message = False
            else:
                result = chatbot.continue_conversation(user_input)
            
            # Display response
            response = result.get('response', '抱歉，我没有收到回复。')
            print(f"\n🤖 助手: {response}")
            
            # Display status
            print_status(result)
            
            # If conversation is complete, auto-generate project
            if result.get('is_complete'):
                print("\n🎉 太棒了！我们已经收集到足够的信息来开发您的视频创意！")
                
                # Ask user if they want to proceed
                proceed = input("\n🚀 是否立即生成完整项目（故事大纲+角色档案+保存）？[Y/n]: ").strip().lower()
                
                if proceed in ['', 'y', 'yes', '是', '确定']:
                    project_result = generate_complete_project(chatbot, idea_structurer, character_generator)
                    
                    if project_result:
                        print("\n🎊 完整项目创建成功！")
                        print("=" * 60)
                        print("📋 项目摘要:")
                        print(f"   📖 故事: {project_result['story_outline'].title}")
                        print(f"   👥 角色数量: {len(project_result['character_profiles'])}个")
                        print(f"   ⏱️ 预计时长: {project_result['story_outline'].estimated_duration}秒")
                        print(f"   🆔 项目ID: {project_result['project_id']}")
                        
                        # Ask if user wants to proceed to Script Crew
                        script_proceed = input("\n🎬 是否继续进行Script Crew处理（生成详细故事和VEO3提示词）？[Y/n]: ").strip().lower()
                        
                        if script_proceed in ['', 'y', 'yes', '是', '确定']:
                            print("\n🤖 开始Script Crew处理...")
                            try:
                                from spark.crews.script.src.script.crew import ScriptGenerationCrew
                                script_crew = ScriptGenerationCrew()
                                
                                # Process the project
                                script_results = script_crew.process_project(project_result['project_id'])
                                
                                print("✅ Script Crew处理完成！")
                                print(f"   📚 详细故事: {len(script_results['detailed_story'].full_story_text)}字符")
                                print(f"   🎥 VEO3提示词: {len(script_results['video_prompts'])}个")
                                print(f"   💾 结果已保存至: projects/projects/{project_result['project_id']}/scripts/")
                                
                                # Show sample prompts
                                print(f"\n🎬 VEO3提示词示例:")
                                for i, prompt in enumerate(script_results['video_prompts'][:3], 1):
                                    print(f"   镜头{i}: {prompt.veo3_prompt[:60]}...")
                                
                                print(f"\n🏆 完整的视频创意项目已准备就绪！")
                                print(f"   📁 项目目录: projects/projects/{project_result['project_id']}/")
                                print(f"   📋 下一步: 使用VEO3生成视频片段")
                                
                            except Exception as e:
                                print(f"❌ Script Crew处理失败: {e}")
                        else:
                            print("⏸️ 已保存项目，稍后可手动运行Script Crew")
                    else:
                        print("❌ 项目创建失败，请重试")
                else:
                    print("⏸️ 跳过项目生成")
                
                print("\n💡 下一步选择:")
                print("   - 输入 'reset' 开始新的创意")
                print("   - 继续补充当前创意的细节")
                print("   - 输入 'quit' 退出")
        
        except KeyboardInterrupt:
            print("\n\n👋 收到中断信号，再见！")
            break
        except Exception as e:
            print(f"\n❌ 处理过程中出现错误: {e}")
            print("请重试或输入 'reset' 重新开始")

if __name__ == "__main__":
    main() 