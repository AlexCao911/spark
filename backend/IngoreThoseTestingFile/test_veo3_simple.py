#!/usr/bin/env python3
"""
简单的VEO 3.0 Gemini API测试脚本
"""

import os
import sys
import json
import requests
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


def test_gemini_api():
    """测试Gemini API基本连接"""
    print("🔍 测试Gemini API连接...")
    
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到VIDEO_GENERATE_API_KEY环境变量")
        return False
    
    # 测试基本API连接
    test_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Gemini API连接成功")
            
            models = response.json()
            print(f"📋 可用模型数量: {len(models.get('models', []))}")
            
            # 查找VEO相关模型
            veo_models = []
            for model in models.get('models', []):
                model_name = model.get('name', '')
                if 'veo' in model_name.lower():
                    veo_models.append(model_name)
            
            if veo_models:
                print("✅ 找到VEO模型:")
                for model in veo_models:
                    print(f"   - {model}")
            else:
                print("⚠️  未找到VEO模型")
                print("📝 可用模型示例:")
                for i, model in enumerate(models.get('models', [])[:5]):
                    print(f"   - {model.get('name', 'Unknown')}")
                if len(models.get('models', [])) > 5:
                    print(f"   ... 还有 {len(models.get('models', [])) - 5} 个模型")
            
            return True
        else:
            print(f"❌ API连接失败: {response.status_code}")
            try:
                error_info = response.json()
                print(f"错误详情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API连接异常: {str(e)}")
        return False


def test_video_generation():
    """测试视频生成请求"""
    print("\n🎬 测试视频生成请求...")
    
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到API密钥")
        return False
    
    # 构建请求
    url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.0-generate:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然，电影级画质，3秒钟"
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print("📤 发送视频生成请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 请求成功")
            print(f"📄 响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            try:
                error_info = response.json()
                print(f"错误详情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 VEO 3.0 Gemini API 简单测试")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    mock_mode = os.getenv('VEO3_MOCK_MODE', 'true').lower()
    
    print(f"🔑 API密钥: {api_key[:20] if api_key else 'None'}...")
    print(f"🎭 模拟模式: {mock_mode}")
    
    if mock_mode == 'true':
        print("⚠️  当前处于模拟模式，请设置 VEO3_MOCK_MODE=false 进行真实测试")
        return True
    
    # 运行测试
    tests = [
        ("Gemini API连接", test_gemini_api),
        ("视频生成请求", test_video_generation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)