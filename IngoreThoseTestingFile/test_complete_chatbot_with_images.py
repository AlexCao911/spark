#!/usr/bin/env python3
"""
完整的Chatbot流程测试，包含真实的Wanx2.1-t2i-turbo图片生成
"""

import sys
import json
import time
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from spark.chatbot.core import ChatbotCore
from spark.chatbot.idea_structurer import IdeaStructurer
from spark.chatbot.character_generator import CharacterProfileGenerator
from spark.models import UserIdea, CharacterProfile, StoryOutline
from spark.config import config

def print_banner():
    """Print test banner."""
    print("=" * 80)
    print("🎬 Spark AI - 完整Chatbot流程测试")
    print("   包括: 对话 → 想法结构化 → 角色生成(含真实图片) → 剧情outline")
    print("=" * 80)

def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print("="*60)

def simulate_conversation(chatbot):
    """Simulate a complete conversation."""
    print_section("第一阶段: 用户对话交互")
    
    # 更详细的对话模拟
    conversation_steps = [
        "我想制作一个关于星际学院的科幻动画视频",
        "主角是一个叫做星辰的新生，她拥有控制星光的能力",
        "还有一个机械天才同学叫做铁心，他制造各种高科技装备",
        "故事讲述他们在学院中发现了一个古老的外星文明遗迹",
        "我希望这个视频面向年轻人，大约2-3分钟，科幻风格但温暖治愈"
    ]
    
    first_message = True
    
    for i, user_input in enumerate(conversation_steps, 1):
        print(f"\n👤 用户输入 {i}: {user_input}")
        print("-" * 50)
        
        if first_message:
            result = chatbot.engage_user(user_input)
            first_message = False
        else:
            result = chatbot.continue_conversation(user_input)
        
        # Show response (truncated)
        response = result.get('response', 'No response')
        print(f"🤖 AI回复: {response[:200]}...")
        
        # Show analysis
        print(f"\n📊 分析状态:")
        print(f"   已识别元素: {result.get('found_elements', [])}")
        print(f"   是否完整: {result.get('is_complete')}")
        
        if result.get('is_complete'):
            print("\n✅ 对话已完成！收集到足够信息。")
            break
    
    return chatbot.get_conversation_history()

def test_idea_structuring(conversation_history):
    """Test idea structuring."""
    print_section("第二阶段: 想法结构化")
    
    try:
        structurer = IdeaStructurer()
        
        print(f"📝 处理对话历史 ({len(conversation_history)} 条消息)")
        
        user_idea = structurer.structure_conversation(conversation_history)
        
        if user_idea:
            print(f"\n✅ 想法结构化成功!")
            print(f"📋 结构化结果:")
            print(f"   主题: {user_idea.theme}")
            print(f"   类型: {user_idea.genre}")
            print(f"   目标观众: {user_idea.target_audience}")
            print(f"   时长: {user_idea.duration_preference}秒")
            print(f"   视觉风格: {user_idea.visual_style}")
            print(f"   情绪基调: {user_idea.mood}")
            
            print(f"\n📖 角色信息:")
            for i, char in enumerate(user_idea.basic_characters, 1):
                print(f"   角色{i}: {char}")
            
            print(f"\n📖 情节要点:")
            for i, plot in enumerate(user_idea.plot_points, 1):
                print(f"   情节{i}: {plot}")
        
        return user_idea
        
    except Exception as e:
        print(f"❌ 想法结构化失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_character_generation_with_real_images(user_idea):
    """Test character generation with real Wanx images."""
    print_section("第三阶段: 角色档案生成 (含真实图片)")
    
    if not user_idea:
        print("❌ 无法进行角色生成 - 缺少用户想法数据")
        return []
    
    try:
        generator = CharacterProfileGenerator()
        
        print(f"🎭 准备生成 {len(user_idea.basic_characters)} 个角色档案...")
        print("🎨 使用Wanx2.1-t2i-turbo生成真实图片")
        
        start_time = time.time()
        character_profiles = generator.generate_complete_character_profiles(
            user_idea.basic_characters, user_idea
        )
        end_time = time.time()
        
        print(f"\n⏱️  总生成时间: {end_time-start_time:.1f}秒")
        print(f"📊 生成结果: {len(character_profiles)} 个角色")
        
        # Display detailed results
        success_count = 0
        for i, profile in enumerate(character_profiles, 1):
            print(f"\n{'='*60}")
            print(f"👤 角色 {i}: {profile.name}")
            print(f"{'='*60}")
            print(f"🎭 角色类型: {profile.role}")
            print(f"👀 外观描述: {profile.appearance}")
            print(f"🧠 性格特点: {profile.personality}")
            print(f"📜 背景故事: {profile.backstory[:150]}...")
            print(f"🎯 动机目标: {', '.join(profile.motivations[:3])}")
            print(f"🏷️  视觉标签: {', '.join(profile.visual_consistency_tags)}")
            
            if profile.image_url:
                print(f"🎨 角色图片: ✅ 生成成功")
                print(f"🔗 图片链接: {profile.image_url}")
                success_count += 1
                
                # Verify image URL
                try:
                    import requests
                    response = requests.head(profile.image_url, timeout=10)
                    status = "✅ 可访问" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
                except:
                    status = "⚠️ 无法验证"
                
                print(f"🌐 图片状态: {status}")
            else:
                print(f"🎨 角色图片: ❌ 生成失败")
        
        success_rate = success_count / len(character_profiles) * 100 if character_profiles else 0
        print(f"\n📈 图片生成成功率: {success_count}/{len(character_profiles)} ({success_rate:.1f}%)")
        
        if success_count > 0:
            print("🎉 角色图片生成成功！可以在浏览器中查看生成的图片")
        
        return character_profiles
        
    except Exception as e:
        print(f"❌ 角色生成失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_story_outline_generation(user_idea, character_profiles):
    """Test story outline generation."""
    print_section("第四阶段: 剧情大纲生成")
    
    if not user_idea:
        print("❌ 无法生成剧情大纲 - 缺少用户想法数据")
        return None
    
    try:
        structurer = IdeaStructurer()
        
        print("📖 根据角色档案生成完整故事大纲...")
        
        story_outline = structurer.generate_story_outline(user_idea)
        
        if story_outline:
            print(f"\n✅ 剧情大纲生成成功!")
            print(f"📋 大纲信息:")
            print(f"   🎬 标题: {story_outline.title}")
            print(f"   ⏱️  预估时长: {story_outline.estimated_duration}秒")
            print(f"   📝 摘要: {story_outline.summary}")
            
            print(f"\n📜 完整故事大纲:")
            # 分段显示故事
            story_text = story_outline.narrative_text
            paragraphs = story_text.split('\n\n')
            for i, paragraph in enumerate(paragraphs[:3], 1):  # 显示前3段
                print(f"   段落{i}: {paragraph.strip()}")
                if i < len(paragraphs):
                    print()
            
            if len(paragraphs) > 3:
                print(f"   ... (共{len(paragraphs)}段，总长度{len(story_text)}字符)")
        
        return story_outline
        
    except Exception as e:
        print(f"❌ 剧情大纲生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_complete_results(user_idea, character_profiles, story_outline):
    """Save all results with comprehensive information."""
    print_section("第五阶段: 保存完整结果")
    
    try:
        # Create output directory
        output_dir = Path("complete_chatbot_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save user idea
        if user_idea:
            idea_path = output_dir / "user_idea.json"
            with open(idea_path, 'w', encoding='utf-8') as f:
                json.dump(user_idea.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"✅ 用户想法已保存: {idea_path}")
        
        # Save character profiles with images
        if character_profiles:
            characters_path = output_dir / "character_profiles_with_images.json"
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump([char.model_dump() for char in character_profiles], f, ensure_ascii=False, indent=2)
            print(f"✅ 角色档案(含图片)已保存: {characters_path}")
            
            # Create an HTML file for easy image viewing
            html_path = output_dir / "character_gallery.html"
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Spark AI - 角色图片画廊</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .character { margin: 30px 0; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .character h2 { color: #333; margin-top: 0; }
        .character img { max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
        .info { margin: 15px 0; }
        .label { font-weight: bold; color: #666; }
    </style>
</head>
<body>
    <h1>🎭 Spark AI 角色图片画廊</h1>
    <p>以下是使用Wanx2.1-t2i-turbo生成的角色图片：</p>
"""
            
            for i, profile in enumerate(character_profiles, 1):
                html_content += f"""
    <div class="character">
        <h2>👤 角色 {i}: {profile.name}</h2>
        <div class="info"><span class="label">角色类型:</span> {profile.role}</div>
        <div class="info"><span class="label">外观描述:</span> {profile.appearance}</div>
        <div class="info"><span class="label">性格特点:</span> {profile.personality}</div>
        {"<img src='" + profile.image_url + "' alt='" + profile.name + "' onerror='this.style.display=\"none\"'>" if profile.image_url else "<p>❌ 图片生成失败</p>"}
        <div class="info"><span class="label">图片链接:</span> <a href="{profile.image_url or '#'}" target="_blank">{profile.image_url or '无'}</a></div>
    </div>
"""
            
            html_content += """
</body>
</html>"""
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ 角色图片画廊已保存: {html_path}")
            print(f"   在浏览器中打开此文件可查看所有角色图片")
        
        # Save story outline
        if story_outline:
            story_path = output_dir / "story_outline.json"
            with open(story_path, 'w', encoding='utf-8') as f:
                json.dump(story_outline.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"✅ 剧情大纲已保存: {story_path}")
        
        print(f"\n📁 所有结果已保存到: {output_dir.absolute()}")
        
        # Generate summary
        summary_path = output_dir / "SUMMARY.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("Spark AI 完整流程测试结果总结\n")
            f.write("=" * 50 + "\n\n")
            
            if user_idea:
                f.write(f"📝 用户创意: {user_idea.theme}\n")
                f.write(f"🎭 角色数量: {len(user_idea.basic_characters)}\n")
                f.write(f"🎨 视觉风格: {user_idea.visual_style}\n\n")
            
            if character_profiles:
                f.write(f"👤 生成角色: {len(character_profiles)} 个\n")
                image_count = sum(1 for p in character_profiles if p.image_url)
                f.write(f"🎨 图片成功: {image_count}/{len(character_profiles)}\n\n")
                
                for i, profile in enumerate(character_profiles, 1):
                    f.write(f"角色 {i}: {profile.name}\n")
                    f.write(f"图片: {profile.image_url or '生成失败'}\n\n")
            
            if story_outline:
                f.write(f"📖 故事标题: {story_outline.title}\n")
                f.write(f"⏱️  故事时长: {story_outline.estimated_duration}秒\n")
        
        print(f"✅ 测试总结已保存: {summary_path}")
        
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")

def main():
    """Run complete chatbot flow test with real images."""
    print_banner()
    
    # Check configuration
    missing_keys = config.get_missing_api_keys()
    if missing_keys:
        print(f"❌ 缺少API密钥: {missing_keys}")
        print("请设置环境变量后重试")
        return
    
    print("✅ 所有API密钥配置正常，开始完整流程测试...")
    print(f"🎨 图片生成: 使用Wanx2.1-t2i-turbo ({config.IMAGE_GEN_MODEL})")
    
    try:
        # Initialize chatbot
        chatbot = ChatbotCore()
        
        # Stage 1: Conversation
        conversation_history = simulate_conversation(chatbot)
        
        # Stage 2: Idea structuring
        user_idea = test_idea_structuring(conversation_history)
        
        # Stage 3: Character generation with real images
        character_profiles = test_character_generation_with_real_images(user_idea)
        
        # Stage 4: Story outline generation
        story_outline = test_story_outline_generation(user_idea, character_profiles)
        
        # Stage 5: Save comprehensive results
        save_complete_results(user_idea, character_profiles, story_outline)
        
        # Final summary
        print_section("测试完成总结")
        success_count = sum([
            bool(conversation_history),
            bool(user_idea),
            bool(character_profiles),
            bool(story_outline)
        ])
        
        image_count = sum(1 for p in character_profiles if p.image_url) if character_profiles else 0
        
        print(f"🎯 完成度: {success_count}/4 个阶段")
        print(f"✅ 对话交互: {'成功' if conversation_history else '失败'}")
        print(f"✅ 想法结构化: {'成功' if user_idea else '失败'}")
        print(f"✅ 角色生成: {'成功' if character_profiles else '失败'} ({len(character_profiles) if character_profiles else 0} 个角色)")
        print(f"✅ 真实图片生成: {'成功' if image_count > 0 else '失败'} ({image_count} 张图片)")
        print(f"✅ 剧情大纲: {'成功' if story_outline else '失败'}")
        
        if success_count == 4 and image_count > 0:
            print("\n🎉 完整流程测试成功！所有功能正常运行！")
            print("✨ Spark AI Chatbot系统已完全就绪，包含真实图片生成")
            print(f"🔗 查看结果: complete_chatbot_output/character_gallery.html")
        else:
            print(f"\n⚠️  测试完成，部分功能可能需要检查")
        
        if image_count > 0:
            print(f"\n🎨 生成的角色图片:")
            for i, profile in enumerate(character_profiles, 1):
                if profile.image_url:
                    print(f"   角色{i} ({profile.name}): {profile.image_url}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现严重错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 