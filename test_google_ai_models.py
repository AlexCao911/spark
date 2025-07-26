#!/usr/bin/env python3
"""
测试Google AI Studio可用的模型
"""

import os
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

def list_available_models():
    """列出Google AI Studio可用的模型"""
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到API密钥")
        return
    
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    models_url = f"{base_url}/models"
    
    headers = {
        'x-goog-api-key': api_key
    }
    
    try:
        response = requests.get(models_url, headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ 可用模型列表:")
            
            for model in models.get('models', []):
                model_name = model.get('name', 'Unknown')
                display_name = model.get('displayName', 'Unknown')
                description = model.get('description', 'No description')
                
                print(f"\n📱 模型: {model_name}")
                print(f"   显示名称: {display_name}")
                print(f"   描述: {description}")
                
                # 检查是否支持视频生成
                supported_methods = model.get('supportedGenerationMethods', [])
                if 'generateContent' in supported_methods:
                    print("   ✅ 支持内容生成")
                
                # 检查输入输出类型
                input_types = model.get('inputTokenLimit', 'Unknown')
                output_types = model.get('outputTokenLimit', 'Unknown')
                print(f"   输入限制: {input_types}")
                print(f"   输出限制: {output_types}")
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_gemini_model():
    """测试Gemini模型（可能支持视频）"""
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到API密钥")
        return
    
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    # 尝试不同的模型名称
    model_names = [
        "gemini-1.5-pro",
        "gemini-1.5-flash", 
        "gemini-pro-vision",
        "gemini-pro"
    ]
    
    for model_name in model_names:
        print(f"\n🧪 测试模型: {model_name}")
        
        generate_url = f"{base_url}/models/{model_name}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": "生成一个简单的视频描述：蓝天白云"
                }]
            }]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key
        }
        
        try:
            response = requests.post(generate_url, headers=headers, json=payload, timeout=10)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ 模型可用")
                
                # 提取生成的内容
                if 'candidates' in result:
                    for candidate in result['candidates']:
                        if 'content' in candidate:
                            parts = candidate['content'].get('parts', [])
                            for part in parts:
                                if 'text' in part:
                                    print(f"   📝 生成内容: {part['text'][:100]}...")
            else:
                print(f"   ❌ 模型不可用")
                error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"   错误: {error_info}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    print("🔍 Google AI Studio模型测试")
    print("=" * 50)
    
    print("\n1. 列出所有可用模型:")
    list_available_models()
    
    print("\n2. 测试常见模型:")
    test_gemini_model()
    
    print("\n📝 结论:")
    print("- Google AI Studio目前可能不直接支持VEO 2.0视频生成")
    print("- 建议使用Gemini模型进行文本生成，然后结合其他视频生成服务")
    print("- 或者考虑使用Google Cloud Video AI API")