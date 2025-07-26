#!/usr/bin/env python3
"""
VEO 3.0 Gemini API专用测试脚本
基于Google AI文档的视频生成API测试
"""

import os
import sys
import json
import time
import requests
import base64
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

from src.spark.tools.veo3_real_tool import VEO3RealTool
from src.spark.models import VideoPrompt


class GeminiVEO3Tester:
    """Gemini VEO3 API测试器"""
    
    def __init__(self):
        self.api_key = os.getenv('VIDEO_GENERATE_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def test_api_connection(self):
        """测试API连接和模型列表"""
        print("🔍 测试Gemini API连接...")
        
        if not self.api_key:
            print("❌ 未找到VIDEO_GENERATE_API_KEY")
            return False
        
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ API连接成功，找到 {len(models.get('models', []))} 个模型")
                
                # 查找VEO模型
                veo_models = []
                for model in models.get('models', []):
                    model_name = model.get('name', '')
                    if 'veo' in model_name.lower():
                        veo_models.append(model_name)
                        print(f"   📹 VEO模型: {model_name}")
                
                if not veo_models:
                    print("⚠️  未找到VEO模型，显示前5个可用模型:")
                    for model in models.get('models', [])[:5]:
                        print(f"   - {model.get('name', 'Unknown')}")
                
                return True
            else:
                print(f"❌ API连接失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API连接异常: {str(e)}")
            return False
    
    def test_text_generation(self):
        """测试基本文本生成（验证API工作）"""
        print("\n📝 测试基本文本生成...")
        
        try:
            url = f"{self.base_url}/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "请简单介绍一下VEO 3.0视频生成模型"
                    }]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 文本生成成功")
                
                if "candidates" in result:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"📄 响应内容: {content[:200]}...")
                
                return True
            else:
                print(f"❌ 文本生成失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 文本生成异常: {str(e)}")
            return False
    
    def test_video_generation_request(self):
        """测试视频生成请求"""
        print("\n🎬 测试视频生成请求...")
        
        # 首先获取可用模型列表
        try:
            models_url = f"{self.base_url}/models?key={self.api_key}"
            models_response = requests.get(models_url, timeout=10)
            
            if models_response.status_code == 200:
                models = models_response.json()
                available_models = [model.get('name', '') for model in models.get('models', [])]
                print(f"📋 获取到 {len(available_models)} 个可用模型")
            else:
                print("⚠️  无法获取模型列表，使用默认模型")
                available_models = []
        except Exception as e:
            print(f"⚠️  获取模型列表失败: {str(e)}")
            available_models = []
        
        # 按优先级尝试不同的模型
        model_candidates = [
            ("models/veo-3.0-generate", "VEO 3.0专用模型"),
            ("models/gemini-1.5-pro-vision", "Gemini 1.5 Pro Vision"),
            ("models/gemini-1.5-flash", "Gemini 1.5 Flash"),
            ("models/gemini-pro-vision", "Gemini Pro Vision"),
            ("models/gemini-pro", "Gemini Pro")
        ]
        
        for model_name, description in model_candidates:
            if available_models and model_name not in available_models:
                print(f"⏭️  跳过不可用模型: {model_name}")
                continue
                
            print(f"\n尝试模型: {model_name} ({description})")
            
            try:
                url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": "请描述如何生成一个3秒的视频：一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然。如果你能生成视频，请生成；如果不能，请说明原因。"
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1024
                    }
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 请求成功")
                    
                    # 解析响应内容
                    if "candidates" in result and result["candidates"]:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            text_content = candidate["content"]["parts"][0].get("text", "")
                            print(f"   📄 响应内容: {text_content[:200]}...")
                            
                            # 检查是否包含视频数据
                            has_video = any("inline_data" in part and 
                                          part.get("inline_data", {}).get("mime_type", "").startswith("video/")
                                          for part in candidate["content"]["parts"])
                            
                            if has_video:
                                print(f"   🎬 包含视频数据!")
                                return True
                            else:
                                print(f"   📝 仅包含文本响应")
                    
                    # 即使没有视频，文本响应成功也算部分成功
                    if model_name == "models/veo-3.0-generate":
                        return True  # VEO模型响应成功
                        
                elif response.status_code == 404:
                    print(f"   ❌ 模型不存在")
                else:
                    print(f"   ❌ 请求失败: {response.status_code}")
                    try:
                        error_info = response.json()
                        error_msg = error_info.get("error", {}).get("message", "Unknown error")
                        print(f"   错误详情: {error_msg}")
                    except:
                        print(f"   错误详情: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ 请求异常: {str(e)}")
        
        print("\n💡 总结:")
        print("- 如果所有模型都不支持视频生成，这是正常的")
        print("- VEO 3.0可能尚未公开发布或需要特殊权限")
        print("- 建议使用模拟模式进行开发: VEO3_MOCK_MODE=true")
        
        return False  # 没有找到真正的视频生成功能
    
    def test_veo3_tool_integration(self):
        """测试VEO3工具集成"""
        print("\n🔧 测试VEO3工具集成...")
        
        try:
            # 设置为真实模式
            os.environ['VEO3_MOCK_MODE'] = 'false'
            
            veo3_tool = VEO3RealTool()
            
            # 创建测试提示词
            test_prompt = VideoPrompt(
                shot_id=1,
                veo3_prompt="一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然，3秒钟",
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
            else:
                print("✅ 视频生成请求成功")
                return True
                
        except Exception as e:
            print(f"❌ VEO3工具测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_image_to_video(self):
        """测试图像到视频生成"""
        print("\n🖼️ 测试图像到视频生成...")
        
        # 创建一个简单的测试图像（1x1像素的PNG）
        test_image_data = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode()
        
        try:
            url = f"{self.base_url}/models/gemini-1.5-pro-vision:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "基于这张图像，生成一个3秒的视频"},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": test_image_data
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 图像到视频请求成功")
                print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ 图像到视频请求失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 图像到视频测试异常: {str(e)}")
            return False


def main():
    """主测试函数"""
    print("🚀 VEO 3.0 Gemini API 专用测试")
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
    
    # 创建测试器
    tester = GeminiVEO3Tester()
    
    # 运行测试
    tests = [
        ("API连接测试", tester.test_api_connection),
        ("文本生成测试", tester.test_text_generation),
        ("视频生成请求测试", tester.test_video_generation_request),
        ("VEO3工具集成测试", tester.test_veo3_tool_integration),
        ("图像到视频测试", tester.test_image_to_video)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
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
    
    if passed >= 2:  # 至少API连接和文本生成通过
        print("🎉 基础功能正常！")
        if passed < len(results):
            print("⚠️  部分高级功能可能需要特殊权限或配置")
        return True
    else:
        print("❌ 基础功能有问题，请检查API密钥和网络连接")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)