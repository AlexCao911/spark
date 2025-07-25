#!/usr/bin/env python3
"""
Simple test for single image generation.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_single_image():
    """Test generating a single image."""
    try:
        from spark.chatbot.character_generator import WanxImageGenerator
        
        print("🎨 测试单个图像生成")
        print("=" * 25)
        
        generator = WanxImageGenerator()
        
        prompt = "一个勇敢的太空探险家，穿着未来科技装备"
        print(f"📝 提示词: {prompt}")
        
        print("🚀 开始生成图像...")
        image_url = generator.generate_image(
            prompt=prompt,
            style="<photography>",
            size="1024*1024"
        )
        
        if image_url:
            print(f"✅ 成功生成图像!")
            print(f"🔗 图像URL: {image_url}")
        else:
            print("❌ 图像生成失败")
        
        return image_url is not None
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_single_image()