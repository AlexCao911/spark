#!/usr/bin/env python3
"""
测试角色生成功能，包括Wanx2.1-t2i-turbo图片生成
"""

import sys
import json
import time
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from spark.chatbot.character_generator import WanxImageGenerator, CharacterProfileGenerator
from spark.models import CharacterProfile, UserIdea
from spark.config import config

def print_banner():
    """Print test banner."""
    print("=" * 80)
    print("🎭 Spark AI - 角色图片生成功能测试")
    print("   使用 Wanx2.1-t2i-turbo 模型")
    print("=" * 80)

def test_api_configuration():
    """Test API configuration."""
    print("📋 第一步: 检查API配置")
    print("-" * 50)
    
    api_key = config.IMAGE_GEN_API_KEY
    if not api_key:
        print("❌ API密钥未配置")
        return False
    
    print(f"✅ API密钥已配置")
    print(f"   长度: {len(api_key)} 字符")
    print(f"   前缀: {api_key[:8]}...")
    print(f"   格式检查: {'✅ 正确' if api_key.startswith('sk-') else '❌ 格式异常'}")
    print(f"   端点: {config.IMAGE_GEN_API_ENDPOINT}")
    
    return api_key.startswith('sk-')

def test_basic_image_generation():
    """Test basic Wanx image generation."""
    print("\n📸 第二步: 测试基础图片生成")
    print("-" * 50)
    
    try:
        generator = WanxImageGenerator()
        
        # Test prompt
        test_prompt = "a beautiful anime girl wizard student, magical academy uniform, holding a magic wand, detailed anime art style, high quality"
        
        print(f"🔄 测试提示词: {test_prompt}")
        print("⏳ 正在调用Wanx2.1-t2i-turbo...")
        
        start_time = time.time()
        image_url = generator.generate_image(
            prompt=test_prompt,
            style="anime",
            size="1024*1024"
        )
        end_time = time.time()
        
        if image_url:
            print(f"✅ 图片生成成功! (耗时: {end_time-start_time:.1f}秒)")
            print(f"🔗 图片URL: {image_url}")
            
            # Test if URL is accessible
            import requests
            try:
                response = requests.head(image_url, timeout=10)
                if response.status_code == 200:
                    print("✅ 图片URL可访问")
                else:
                    print(f"⚠️  图片URL状态: {response.status_code}")
            except:
                print("⚠️  无法验证图片URL")
            
            return image_url
        else:
            print("❌ 图片生成失败")
            return None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_character_profile_generation():
    """Test complete character profile generation with images."""
    print("\n👤 第三步: 测试角色档案生成")
    print("-" * 50)
    
    try:
        # Create test user idea
        user_idea = UserIdea(
            theme="魔法学院奇幻故事",
            genre="奇幻",
            target_audience="青少年",
            duration_preference=180,
            basic_characters=[
                "艾米，一个拥有时间魔法能力的新生魔法师，棕色头发，绿色眼睛",
                "凯尔，神秘的高年级学生导师，银色头发，深蓝色眼睛，擅长空间魔法"
            ],
            visual_style="现代魔法动画风格",
            mood="神秘而温暖"
        )
        
        print(f"📝 用户创意设定:")
        print(f"   主题: {user_idea.theme}")
        print(f"   风格: {user_idea.visual_style}")
        print(f"   角色数量: {len(user_idea.basic_characters)}")
        
        # Generate character profiles
        generator = CharacterProfileGenerator()
        
        print(f"\n🎭 开始生成角色档案...")
        
        start_time = time.time()
        character_profiles = generator.generate_complete_character_profiles(
            user_idea.basic_characters, user_idea
        )
        end_time = time.time()
        
        print(f"⏱️  总耗时: {end_time-start_time:.1f}秒")
        print(f"📊 生成结果: {len(character_profiles)} 个角色")
        
        # Display results
        success_count = 0
        for i, profile in enumerate(character_profiles, 1):
            print(f"\n{'='*60}")
            print(f"👤 角色 {i}: {profile.name}")
            print(f"{'='*60}")
            print(f"🎭 角色类型: {profile.role}")
            print(f"👀 外观描述: {profile.appearance}")
            print(f"🧠 性格特点: {profile.personality}")
            print(f"📜 背景故事: {profile.backstory[:100]}...")
            print(f"🎯 动机目标: {', '.join(profile.motivations)}")
            
            if profile.image_url:
                print(f"🎨 角色图片: ✅ 生成成功")
                print(f"🔗 图片链接: {profile.image_url}")
                success_count += 1
                
                # Test image accessibility
                try:
                    import requests
                    response = requests.head(profile.image_url, timeout=5)
                    if response.status_code == 200:
                        print(f"🌐 图片状态: ✅ 可访问")
                    else:
                        print(f"🌐 图片状态: ⚠️  HTTP {response.status_code}")
                except:
                    print(f"🌐 图片状态: ⚠️  无法验证")
            else:
                print(f"🎨 角色图片: ❌ 生成失败")
        
        print(f"\n📈 成功率: {success_count}/{len(character_profiles)} ({success_count/len(character_profiles)*100:.1f}%)")
        
        return character_profiles
        
    except Exception as e:
        print(f"❌ 角色档案生成失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_different_styles():
    """Test different image styles."""
    print("\n🎨 第四步: 测试不同图片风格")
    print("-" * 50)
    
    try:
        generator = WanxImageGenerator()
        
        styles_to_test = [
            ("anime", "anime style magical student"),
            ("photography", "realistic magical academy student portrait"),
            ("oil painting", "oil painting style wizard character")
        ]
        
        results = []
        for style, prompt_desc in styles_to_test:
            print(f"\n🔄 测试风格: {style}")
            print(f"   描述: {prompt_desc}")
            
            full_prompt = f"a young wizard student, {prompt_desc}, magical robes, high quality, detailed"
            
            image_url = generator.generate_image(
                prompt=full_prompt,
                style=style,
                size="1024*1024"
            )
            
            if image_url:
                print(f"   ✅ 生成成功: {image_url[:60]}...")
                results.append((style, image_url))
            else:
                print(f"   ❌ 生成失败")
        
        print(f"\n🎯 风格测试结果: {len(results)}/{len(styles_to_test)} 成功")
        return results
        
    except Exception as e:
        print(f"❌ 风格测试失败: {e}")
        return []

def save_test_results(character_profiles, style_results):
    """Save test results to files."""
    print("\n💾 第五步: 保存测试结果")
    print("-" * 50)
    
    try:
        # Create output directory
        output_dir = Path("character_test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save character profiles
        if character_profiles:
            profiles_path = output_dir / "character_profiles_with_images.json"
            with open(profiles_path, 'w', encoding='utf-8') as f:
                json.dump([profile.model_dump() for profile in character_profiles], f, ensure_ascii=False, indent=2)
            print(f"✅ 角色档案已保存: {profiles_path}")
            
            # Save image URLs list
            urls_path = output_dir / "character_image_urls.txt"
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write("角色图片生成结果\n")
                f.write("=" * 50 + "\n\n")
                for i, profile in enumerate(character_profiles, 1):
                    f.write(f"角色 {i}: {profile.name}\n")
                    f.write(f"描述: {profile.appearance}\n")
                    f.write(f"图片: {profile.image_url if profile.image_url else '生成失败'}\n\n")
            print(f"✅ 图片URL列表已保存: {urls_path}")
        
        # Save style test results
        if style_results:
            styles_path = output_dir / "style_test_results.txt"
            with open(styles_path, 'w', encoding='utf-8') as f:
                f.write("图片风格测试结果\n")
                f.write("=" * 50 + "\n\n")
                for style, url in style_results:
                    f.write(f"风格: {style}\n")
                    f.write(f"图片: {url}\n\n")
            print(f"✅ 风格测试结果已保存: {styles_path}")
        
        print(f"\n📁 所有结果保存在: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")

def main():
    """Run character image generation tests."""
    print_banner()
    
    # Test sequence
    success_count = 0
    total_tests = 4
    
    # Test 1: API Configuration
    if test_api_configuration():
        success_count += 1
        print("✅ API配置测试通过")
    else:
        print("❌ API配置测试失败 - 无法继续")
        return
    
    # Test 2: Basic image generation
    basic_result = test_basic_image_generation()
    if basic_result:
        success_count += 1
        print("✅ 基础图片生成测试通过")
    
    # Test 3: Character profile generation
    character_profiles = test_character_profile_generation()
    if character_profiles and any(p.image_url for p in character_profiles):
        success_count += 1
        print("✅ 角色档案生成测试通过")
    
    # Test 4: Style variations
    style_results = test_different_styles()
    if style_results:
        success_count += 1
        print("✅ 风格测试通过")
    
    # Save results
    save_test_results(character_profiles, style_results)
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    print(f"🎯 测试通过: {success_count}/{total_tests}")
    print(f"🎭 角色生成: {'成功' if character_profiles else '失败'}")
    image_success = any(p.image_url for p in character_profiles) if character_profiles else False
    print(f"🎨 图片生成: {'成功' if image_success else '失败'}")
    
    image_count = sum(1 for p in character_profiles if p.image_url) if character_profiles else 0
    print(f"📈 图片成功率: {image_count}/{len(character_profiles) if character_profiles else 0}")
    
    if success_count == total_tests:
        print("\n🎉 所有测试通过！Wanx2.1-t2i-turbo图片生成功能正常！")
        print("✨ 角色生成系统已完全就绪，可用于生产环境")
    else:
        print(f"\n⚠️  部分测试失败，请检查API配置和网络连接")
    
    if character_profiles and any(p.image_url for p in character_profiles):
        print("\n🔗 生成的图片可以在浏览器中查看:")
        for i, profile in enumerate(character_profiles, 1):
            if profile.image_url:
                print(f"   角色{i} ({profile.name}): {profile.image_url}")

if __name__ == "__main__":
    main() 