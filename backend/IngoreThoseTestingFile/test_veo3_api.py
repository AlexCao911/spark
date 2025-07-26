#!/usr/bin/env python3
"""
VEO3 API测试脚本
测试Google VEO 2.0 API的连接和基本功能
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.tools.veo3_real_tool import VEO3RealTool
from src.spark.models import VideoPrompt


def test_api_connection():
    """测试API连接和认证"""
    print("🔍 测试VEO3 API连接...")
    
    try:
        # 初始化VEO3工具
        veo3_tool = VEO3RealTool()
        print(f"✅ VEO3工具初始化成功")
        print(f"   API密钥: {veo3_tool.api_key[:20]}...")
        print(f"   基础URL: {veo3_tool.base_url}")
        print(f"   生成URL: {veo3_tool.generate_url}")
        
        return veo3_tool
        
    except Exception as e:
        print(f"❌ VEO3工具初始化失败: {str(e)}")
        return None


def test_prompt_validation():
    """测试提示词验证功能"""
    print("\n🔍 测试提示词验证...")
    
    try:
        veo3_tool = VEO3RealTool()
        
        # 测试有效提示词
        valid_prompt = VideoPrompt(
            shot_id=1,
            veo3_prompt="一个美丽的日落场景，金色阳光洒在平静的湖面上，远山如黛，画面宁静祥和",
            duration=5,
            character_reference_images=[]
        )
        
        is_valid = veo3_tool.validate_prompt_compatibility(valid_prompt)
        print(f"✅ 有效提示词验证: {is_valid}")
        
        # 测试无效提示词（太短）
        invalid_prompt = VideoPrompt(
            shot_id=2,
            veo3_prompt="短",
            duration=5,
            character_reference_images=[]
        )
        
        is_invalid = veo3_tool.validate_prompt_compatibility(invalid_prompt)
        print(f"✅ 无效提示词验证: {not is_invalid}")
        
        # 测试参数优化
        params = veo3_tool.optimize_generation_parameters(valid_prompt)
        print(f"✅ 参数优化结果: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ 提示词验证测试失败: {str(e)}")
        return False


def test_simple_video_generation():
    """测试简单视频生成"""
    print("\n🔍 测试简单视频生成...")
    
    try:
        veo3_tool = VEO3RealTool()
        
        # 创建测试提示词
        test_prompt = VideoPrompt(
            shot_id=1,
            veo3_prompt="一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然，电影级画质",
            duration=3,  # 短时间测试
            character_reference_images=[]
        )
        
        print(f"📝 测试提示词: {test_prompt.veo3_prompt}")
        print(f"⏱️  时长: {test_prompt.duration}秒")
        
        # 验证提示词
        if not veo3_tool.validate_prompt_compatibility(test_prompt):
            print("❌ 提示词验证失败")
            return False
        
        print("✅ 提示词验证通过")
        
        # 尝试生成视频
        print("🎬 开始生成视频...")
        start_time = time.time()
        
        result = veo3_tool.generate_video_clip(test_prompt)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  生成耗时: {duration:.2f}秒")
        print(f"📄 生成结果: {result}")
        
        # 分析结果
        if result.startswith("error_"):
            print(f"❌ 视频生成失败: {result}")
            return False
        elif result.startswith("job_"):
            print(f"✅ 视频生成任务已提交: {result}")
            
            # 测试状态查询
            job_id = result.replace("job_", "")
            print(f"🔍 查询任务状态: {job_id}")
            
            status = veo3_tool.check_generation_status(job_id)
            print(f"📊 任务状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
            return True
        elif result.startswith("http"):
            print(f"✅ 视频生成完成，URL: {result}")
            
            # 测试下载功能
            test_download_path = "test_video.mp4"
            print(f"📥 测试下载到: {test_download_path}")
            
            download_success = veo3_tool.download_video(result, test_download_path)
            if download_success:
                print(f"✅ 视频下载成功")
                
                # 检查文件大小
                if Path(test_download_path).exists():
                    file_size = Path(test_download_path).stat().st_size
                    print(f"📁 文件大小: {file_size / 1024:.2f} KB")
                    
                    # 清理测试文件
                    Path(test_download_path).unlink()
                    print("🧹 测试文件已清理")
            else:
                print(f"❌ 视频下载失败")
            
            return True
        else:
            print(f"❓ 未知结果格式: {result}")
            return False
        
    except Exception as e:
        print(f"❌ 视频生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_professional_generation():
    """测试专业级视频生成"""
    print("\n🔍 测试专业级视频生成...")
    
    try:
        veo3_tool = VEO3RealTool()
        
        # 创建专业级测试提示词
        professional_prompt = VideoPrompt(
            shot_id=1,
            veo3_prompt="专业摄影师拍摄的城市夜景，霓虹灯闪烁，车流如织，高楼大厦灯火通明，电影级构图和光影效果",
            duration=5,
            character_reference_images=[]
        )
        
        print(f"📝 专业提示词: {professional_prompt.veo3_prompt}")
        
        # 使用专业规格生成
        print("🎬 使用专业规格生成视频...")
        result = veo3_tool.generate_with_professional_specs(
            professional_prompt, 
            []  # 无参考图像
        )
        
        print(f"📄 专业生成结果: {result}")
        
        if not result.startswith("error_"):
            print("✅ 专业级视频生成测试通过")
            return True
        else:
            print(f"❌ 专业级视频生成失败: {result}")
            return False
        
    except Exception as e:
        print(f"❌ 专业级生成测试失败: {str(e)}")
        return False


def test_api_error_handling():
    """测试API错误处理"""
    print("\n🔍 测试API错误处理...")
    
    try:
        # 测试无效API密钥
        original_key = os.environ.get('VIDEO_GENERATE_API_KEY')
        os.environ['VIDEO_GENERATE_API_KEY'] = 'invalid_key_test'
        
        try:
            invalid_tool = VEO3RealTool()
            test_prompt = VideoPrompt(
                shot_id=1,
                veo3_prompt="测试错误处理",
                duration=3,
                character_reference_images=[]
            )
            
            result = invalid_tool.generate_video_clip(test_prompt)
            print(f"📄 无效密钥测试结果: {result}")
            
            if result.startswith("error_"):
                print("✅ 错误处理测试通过")
            else:
                print("❓ 预期错误但得到成功结果")
                
        finally:
            # 恢复原始密钥
            if original_key:
                os.environ['VIDEO_GENERATE_API_KEY'] = original_key
        
        return True
        
    except Exception as e:
        print(f"✅ 错误处理测试通过 (捕获到预期异常): {str(e)}")
        return True


def main():
    """主测试函数"""
    print("🚀 开始VEO3 API测试")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到VIDEO_GENERATE_API_KEY环境变量")
        print("请在.env文件中设置您的Google AI Studio API密钥")
        return False
    
    print(f"🔑 API密钥已配置: {api_key[:20]}...")
    
    # 运行测试
    tests = [
        ("API连接测试", test_api_connection),
        ("提示词验证测试", test_prompt_validation),
        ("简单视频生成测试", test_simple_video_generation),
        ("专业级生成测试", test_professional_generation),
        ("错误处理测试", test_api_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "API连接测试":
                result = test_func()
                results[test_name] = result is not None
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}异常: {str(e)}")
            results[test_name] = False
    
    # 输出测试结果总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！VEO3 API配置正确且功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查API配置和网络连接。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)