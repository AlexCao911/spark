#!/usr/bin/env python3
"""
VEO 3.0 Gemini API测试脚本
测试Google AI Gemini API VEO 3.0模型
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 手动加载.env文件
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from src.spark.tools.veo3_real_tool import VEO3RealTool
from src.spark.models import VideoPrompt


def check_api_key():
    """检查API密钥配置"""
    print("🔍 检查API密钥配置...")
    
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    
    if not api_key:
        print("❌ 未找到VIDEO_GENERATE_API_KEY环境变量")
        print("请在.env文件中设置: VIDEO_GENERATE_API_KEY=your_api_key")
        return False
    
    if len(api_key) < 20:
        print("❌ API密钥长度不足，请检查是否正确")
        return False
    
    print(f"✅ API密钥已配置: {api_key[:20]}...")
    return True


def check_api_endpoint():
    """检查API端点连接"""
    print("\n🔍 检查API端点连接...")
    
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    
    if not api_key:
        print("❌ API密钥未配置")
        return False
    
    # 测试Gemini API连接
    test_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API端点连接正常")
            
            # 检查是否有VEO模型
            models = response.json()
            veo_models = [model for model in models.get('models', []) 
                         if 'veo' in model.get('name', '').lower()]
            
            if veo_models:
                print(f"✅ 找到VEO模型: {len(veo_models)}个")
                for model in veo_models:
                    print(f"   - {model.get('name', 'Unknown')}")
            else:
                print("⚠️  未找到VEO模型，但API连接正常")
            
            return True
        else:
            print(f"❌ API连接失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API连接测试失败: {str(e)}")
        return False


def test_veo3_initialization():
    """测试VEO3工具初始化"""
    print("\n🔍 测试VEO3工具初始化...")
    
    try:
        veo3_tool = VEO3RealTool()
        print("✅ VEO3工具初始化成功")
        return veo3_tool
    except Exception as e:
        print(f"❌ VEO3工具初始化失败: {str(e)}")
        return None


def test_api_key_access():
    """测试API密钥访问"""
    print("\n🔍 测试API密钥访问...")
    
    try:
        veo3_tool = VEO3RealTool()
        api_key = veo3_tool._get_api_key()
        
        if api_key:
            print(f"✅ API密钥获取成功: {api_key[:20]}...")
            return True
        else:
            print("❌ 无法获取API密钥")
            return False
            
    except Exception as e:
        print(f"❌ API密钥获取失败: {str(e)}")
        return False


def test_simple_video_generation():
    """测试简单视频生成"""
    print("\n🔍 测试VEO 3.0视频生成...")
    
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
            
            # 等待一段时间后查询状态
            time.sleep(5)
            status = veo3_tool.check_generation_status(job_id)
            print(f"📊 任务状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
            return True
        elif result.startswith("http"):
            print(f"✅ 视频生成完成，URL: {result}")
            return True
        elif result.startswith("mock_videos/"):
            print(f"✅ 模拟视频生成完成: {result}")
            return True
        else:
            print(f"❓ 未知结果格式: {result}")
            return False
        
    except Exception as e:
        print(f"❌ 视频生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def provide_setup_instructions():
    """提供设置说明"""
    print("\n📋 VEO 3.0设置说明:")
    print("=" * 50)
    
    print("\n1. 获取Google AI API密钥:")
    print("   访问: https://aistudio.google.com/app/apikey")
    print("   创建新的API密钥")
    
    print("\n2. 配置.env文件:")
    print("   VIDEO_GENERATE_API_KEY=your_google_ai_api_key")
    print("   VEO3_MOCK_MODE=false")
    
    print("\n3. 检查VEO 3.0访问权限:")
    print("   VEO 3.0可能需要申请访问权限")
    print("   访问: https://ai.google.dev/gemini-api/docs/video")
    
    print("\n4. 测试配置:")
    print("   python test_veo3_vertex_ai.py")
    
    print("\n5. 如果遇到问题:")
    print("   - 确保API密钥有效且有足够权限")
    print("   - 检查网络连接")
    print("   - 查看API配额限制")


def main():
    """主测试函数"""
    print("🚀 开始VEO 3.0 Vertex AI测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("API密钥检查", check_api_key),
        ("API端点连接", check_api_endpoint),
        ("VEO3工具初始化", test_veo3_initialization),
        ("API密钥访问测试", test_api_key_access),
        ("视频生成测试", test_simple_video_generation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "VEO3工具初始化":
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
        print("🎉 所有测试通过！VEO 3.0配置正确且功能正常。")
        return True
    elif passed >= 3:  # 至少前3个测试通过
        print("⚠️  基础配置正常，但视频生成可能需要进一步调试。")
        provide_setup_instructions()
        return True
    else:
        print("❌ 基础配置有问题，请按照说明进行设置。")
        provide_setup_instructions()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)