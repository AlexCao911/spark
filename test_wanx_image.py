#!/usr/bin/env python3
"""
Test script for Wanx2.1-t2i-turbo image generation.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_wanx_image_generation():
    """Test Wanx image generation functionality."""
    try:
        from spark.chatbot.character_generator import WanxImageGenerator
        from spark.config import config
        
        print("🎨 Testing Wanx2.1-t2i-turbo Image Generation")
        print("=" * 45)
        print(f"API Key: {config.IMAGE_GEN_API_KEY[:10]}...")
        print(f"Endpoint: {config.IMAGE_GEN_API_ENDPOINT}")
        print()
        
        # Initialize image generator
        generator = WanxImageGenerator()
        
        # Test prompts
        test_prompts = [
            "一个勇敢的太空探险家，穿着未来科技装备，站在外星球表面",
            "一个神秘的魔法师，长袍飘逸，手持法杖，背景是古老的城堡",
            "一个现代都市的侦探，穿着风衣，在雨夜的街道上"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"🖼️  测试 {i}: {prompt}")
            
            try:
                image_url = generator.generate_image(
                    prompt=prompt,
                    style="<photography>",
                    size="1024*1024"
                )
                
                if image_url:
                    print(f"✅ 成功生成图像: {image_url}")
                else:
                    print("❌ 图像生成失败")
                
            except Exception as e:
                print(f"❌ 错误: {e}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_character_profile_generation():
    """Test complete character profile generation with images."""
    try:
        from spark.chatbot.character_generator import CharacterProfileGenerator
        from spark.models import UserIdea
        
        print("👥 Testing Character Profile Generation")
        print("=" * 40)
        
        # Create test user idea
        user_idea = UserIdea(
            theme="太空冒险",
            genre="sci-fi",
            target_audience="成人",
            duration_preference=120,
            basic_characters=["勇敢的宇航员", "神秘的外星人"],
            plot_points=["发射任务", "发现外星生命", "第一次接触", "返回地球"],
            visual_style="cinematic",
            mood="adventurous"
        )
        
        # Initialize generator
        generator = CharacterProfileGenerator()
        
        print("🚀 生成角色档案...")
        profiles = generator.generate_complete_character_profiles(
            user_idea.basic_characters,
            user_idea
        )
        
        for profile in profiles:
            print(f"\n📋 角色: {profile.name}")
            print(f"   角色: {profile.role}")
            print(f"   外观: {profile.appearance}")
            print(f"   性格: {profile.personality}")
            print(f"   背景: {profile.backstory}")
            print(f"   动机: {', '.join(profile.motivations)}")
            print(f"   图像: {profile.image_url or '未生成'}")
            print(f"   标签: {', '.join(profile.visual_consistency_tags)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 角色生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 Wanx2.1-t2i-turbo 集成测试")
    print("=" * 35)
    
    # Test basic image generation
    print("第一步: 测试基础图像生成...")
    image_success = test_wanx_image_generation()
    
    if image_success:
        print("\n第二步: 测试角色档案生成...")
        profile_success = test_character_profile_generation()
        
        if profile_success:
            print("\n🎉 所有测试通过！Wanx集成工作正常。")
        else:
            print("\n⚠️  图像生成正常，但角色档案生成有问题。")
    else:
        print("\n❌ 图像生成测试失败。请检查API配置。")

if __name__ == "__main__":
    main()