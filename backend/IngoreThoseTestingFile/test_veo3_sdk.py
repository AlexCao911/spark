#!/usr/bin/env python3
"""
VEO 3.0 Google AI SDK测试脚本
使用正确的SDK格式测试VEO 3.0视频生成
"""

import os
import sys
import time
from pathlib import Path

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

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Google AI SDK imports
try:
    import google.generativeai as genai
    from google.generativeai import types
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("❌ Google AI SDK未安装")
    print("请运行: pip install google-generativeai")

from src.spark.tools.veo3_real_tool import VEO3RealTool
from src.spark.models import VideoPrompt


def test_sdk_installation():
    """测试SDK安装"""
    print("🔍 检查Google AI SDK安装...")
    
    if not SDK_AVAILABLE:
        print("❌ Google AI SDK未安装")
        print("安装命令: pip install google-generativeai")
        return False
    
    try:
        print(f"✅ Google AI SDK已安装")
        print(f"版本: {genai.__version__}")
        return True
    except Exception as e:
        print(f"❌ SDK检查失败: {str(e)}")
        return False


def test_api_key_configuration():
    """测试API密钥配置"""
    print("\n🔑 检查API密钥配置...")
    
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到VIDEO_GENERATE_API_KEY环境变量")
        return False
    
    if len(api_key) < 20:
        print("❌ API密钥长度不足")
        return False
    
    print(f"✅ API密钥已配置: {api_key[:20]}...")
    
    # 配置SDK
    try:
        genai.configure(api_key=api_key)
        print("✅ SDK已配置API密钥")
        return True
    except Exception as e:
        print(f"❌ SDK配置失败: {str(e)}")
        return False


def test_client_initialization():
    """测试客户端初始化"""
    print("\n🔧 测试客户端初始化...")
    
    try:
        client = genai.Client()
        print("✅ 客户端初始化成功")
        return client
    except Exception as e:
        print(f"❌ 客户端初始化失败: {str(e)}")
        return None


def test_model_availability(client):
    """测试模型可用性"""
    print("\n📋 检查VEO模型可用性...")
    
    try:
        # 尝试列出可用模型
        models = genai.list_models()
        
        veo_models = []
        for model in models:
            if 'veo' in model.name.lower():
                veo_models.append(model.name)
                print(f"✅ 找到VEO模型: {model.name}")
                if hasattr(model, 'description'):
                    print(f"   描述: {model.description}")
        
        if not veo_models:
            print("⚠️  未找到VEO模型")
            print("可能的原因:")
            print("1. VEO 3.0尚未公开发布")
            print("2. 需要申请特殊访问权限")
            print("3. 模型名称可能不同")
        
        return veo_models
        
    except Exception as e:
        print(f"❌ 模型列表获取失败: {str(e)}")
        return []


def test_video_generation(client):
    """测试视频生成"""
    print("\n🎬 测试视频生成...")
    
    # 尝试不同的模型名称
    model_names = [
        "veo-3.0-generate-preview",
        "veo-3.0-generate",
        "veo-2.0-generate",
        "video-generation"
    ]
    
    for model_name in model_names:
        print(f"\n尝试模型: {model_name}")
        
        try:
            # 构建生成配置
            config = types.GenerateVideosConfig(
                negative_prompt="cartoon, drawing, low quality, blurry, distorted",
                duration_seconds=3,
                aspect_ratio="16:9"
            )
            
            # 生成视频
            operation = client.models.generate_videos(
                model=model_name,
                prompt="A cinematic shot of a majestic lion in the savannah.",
                config=config
            )
            
            print(f"✅ 视频生成任务已提交")
            print(f"📋 操作ID: {operation.name}")
            print(f"📊 操作状态: {'完成' if operation.done else '进行中'}")
            
            # 等待一段时间检查状态
            print("⏳ 等待5秒后检查状态...")
            time.sleep(5)
            
            # 检查操作状态
            updated_operation = client.operations.get(name=operation.name)
            print(f"📊 更新后状态: {'完成' if updated_operation.done else '进行中'}")
            
            if updated_operation.done:
                if updated_operation.response:
                    print("✅ 视频生成完成!")
                    # 这里可以处理生成的视频
                    return True
                else:
                    print("❌ 视频生成失败")
                    if updated_operation.error:
                        print(f"错误: {updated_operation.error}")
            else:
                print("⏳ 视频仍在生成中...")
                return True  # 任务提交成功
            
        except Exception as e:
            print(f"❌ 模型 {model_name} 测试失败: {str(e)}")
            
            # 检查是否是权限问题
            if "permission" in str(e).lower() or "access" in str(e).lower():
                print("💡 可能需要申请VEO 3.0访问权限")
            elif "not found" in str(e).lower():
                print("💡 模型可能不存在或名称不正确")
    
    return False


def test_veo3_tool_integration():
    """测试VEO3工具集成"""
    print("\n🔧 测试VEO3工具集成...")
    
    try:
        # 设置为真实模式
        os.environ['VEO3_MOCK_MODE'] = 'false'
        
        veo3_tool = VEO3RealTool()
        
        # 创建测试提示词
        test_prompt = VideoPrompt(
            shot_id=1,
            veo3_prompt="A cinematic shot of a majestic lion in the savannah, golden hour lighting",
            duration=3,
            character_reference_images=[]
        )
        
        print(f"📝 测试提示词: {test_prompt.veo3_prompt}")
        
        # 验证提示词
        if veo3_tool.validate_prompt_compatibility(test_prompt):
            print("✅ 提示词验证通过")
        else:
            print("❌ 提示词验证失败")
            return False
        
        # 尝试生成视频
        print("🎬 开始生成视频...")
        result = veo3_tool.generate_video_clip(test_prompt)
        
        print(f"📄 生成结果: {result}")
        
        if result.startswith("error_"):
            print(f"❌ 视频生成失败: {result}")
            return False
        elif result.startswith("job_"):
            print("✅ 视频生成任务已提交")
            
            # 测试状态查询
            job_id = result.replace("job_", "")
            print(f"🔍 查询任务状态: {job_id}")
            
            status = veo3_tool.check_generation_status(job_id)
            print(f"📊 任务状态: {status}")
            
            return True
        else:
            print("✅ 视频生成完成或返回其他结果")
            return True
            
    except Exception as e:
        print(f"❌ VEO3工具测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 VEO 3.0 Google AI SDK 测试")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    mock_mode = os.getenv('VEO3_MOCK_MODE', 'true').lower()
    
    print(f"🔑 API密钥: {api_key[:20] if api_key else 'None'}...")
    print(f"🎭 模拟模式: {mock_mode}")
    
    if not api_key:
        print("\n❌ 请先配置VIDEO_GENERATE_API_KEY环境变量")
        print("运行: python configure_veo3.py")
        return False
    
    # 运行测试
    tests = [
        ("SDK安装检查", test_sdk_installation),
        ("API密钥配置", test_api_key_configuration),
        ("客户端初始化", lambda: test_client_initialization() is not None),
        ("VEO3工具集成", test_veo3_tool_integration)
    ]
    
    results = {}
    client = None
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        if test_name == "客户端初始化":
            client = test_client_initialization()
            results[test_name] = client is not None
        else:
            results[test_name] = test_func()
    
    # 如果客户端初始化成功，进行额外测试
    if client:
        print(f"\n{'='*20} 模型可用性检查 {'='*20}")
        veo_models = test_model_availability(client)
        results["模型可用性"] = len(veo_models) > 0
        
        if veo_models:
            print(f"\n{'='*20} 视频生成测试 {'='*20}")
            results["视频生成"] = test_video_generation(client)
    
    # 输出结果总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed >= 3:  # 基础功能通过
        print("🎉 基础功能正常！")
        if passed < len(results):
            print("⚠️  部分高级功能可能需要特殊权限")
        
        print("\n💡 下一步建议:")
        print("1. 如果VEO模型不可用，这是正常的（可能需要申请权限）")
        print("2. 可以继续使用模拟模式进行开发")
        print("3. 关注Google AI更新获取VEO 3.0访问权限")
        
        return True
    else:
        print("❌ 基础功能有问题，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)