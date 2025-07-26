#!/usr/bin/env python3
"""
测试VEO3集成 - 使用Google AI Python SDK
"""

import os
import time
import json
from pathlib import Path

# 设置环境变量
os.environ['VIDEO_GENERATE_API_KEY'] = 'AIzaSyAne1mlhDdmgSw8LyCL2rGK0T1yfh5HFpU'

try:
    from google import genai
    from google.genai import types
    print("✅ Google AI SDK导入成功")
except ImportError as e:
    print(f"❌ Google AI SDK导入失败: {e}")
    print("请运行: pip install google-generativeai")
    exit(1)

def test_veo3_basic():
    """测试基本的VEO3调用"""
    print("\n🧪 测试基本VEO3调用...")
    
    try:
        # 初始化客户端
        api_key = os.getenv('VIDEO_GENERATE_API_KEY')
        client = genai.Client(api_key=api_key)
        
        print(f"🔧 客户端初始化成功")
        
        # 生成视频
        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt="A cinematic shot of a majestic lion in the savannah.",
            config=types.GenerateVideosConfig(
                negative_prompt="cartoon, drawing, low quality"
            ),
        )
        
        print(f"✅ 视频生成任务已提交")
        print(f"📋 操作ID: {operation.name}")
        
        # 等待完成
        while not operation.done:
            print("等待视频生成完成...")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        # 下载生成的视频
        if operation.response and hasattr(operation.response, 'generated_videos'):
            generated_video = operation.response.generated_videos[0]
            
            # 创建输出目录
            output_dir = Path("test_videos")
            output_dir.mkdir(exist_ok=True)
            
            # 下载视频
            client.files.download(file=generated_video.video)
            output_path = output_dir / "test_veo3_basic.mp4"
            generated_video.video.save(str(output_path))
            
            print(f"✅ 视频已保存到: {output_path}")
            return True
        else:
            print("❌ 未找到生成的视频")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_video_generation_tool():
    """测试VideoGenerationTool"""
    print("\n🧪 测试VideoGenerationTool...")
    
    try:
        # 添加项目路径
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.spark.crews.maker.src.maker.tools.video_generation_tool import VideoGenerationTool
        
        # 创建工具实例
        tool = VideoGenerationTool()
        print("✅ VideoGenerationTool初始化成功")
        
        # 准备测试数据
        test_prompts = [
            {
                "shot_id": 1,
                "veo3_prompt": "A beautiful sunset over the ocean with gentle waves",
                "duration": 5,
                "character_reference_images": []
            }
        ]
        
        # 调用工具
        result = tool._run(
            video_prompts=json.dumps(test_prompts),
            character_images="[]",
            project_id="test_project"
        )
        
        print("✅ 工具调用成功")
        print(f"📄 结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始VEO3集成测试...")
    
    # 检查API密钥
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到VIDEO_GENERATE_API_KEY环境变量")
        return
    
    print(f"🔑 API密钥: {api_key[:20]}...")
    
    # 运行测试
    tests = [
        ("基本VEO3调用", test_veo3_basic),
        ("VideoGenerationTool", test_video_generation_tool),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"测试: {test_name}")
        print(f"{'='*50}")
        
        success = test_func()
        results.append((test_name, success))
    
    # 输出测试结果
    print(f"\n{'='*50}")
    print("测试结果汇总:")
    print(f"{'='*50}")
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")

if __name__ == "__main__":
    main()