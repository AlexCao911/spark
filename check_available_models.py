#!/usr/bin/env python3
"""
检查Google AI API中可用的模型
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


def check_available_models():
    """检查可用的模型"""
    print("🔍 检查Google AI API中的可用模型...")
    
    api_key = os.getenv('VIDEO_GENERATE_API_KEY')
    if not api_key:
        print("❌ 未找到VIDEO_GENERATE_API_KEY环境变量")
        return False
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 成功获取模型列表，共 {len(models.get('models', []))} 个模型")
            
            # 分类显示模型
            video_models = []
            vision_models = []
            text_models = []
            other_models = []
            
            for model in models.get('models', []):
                model_name = model.get('name', '')
                display_name = model.get('displayName', '')
                description = model.get('description', '')
                
                if 'video' in model_name.lower() or 'veo' in model_name.lower():
                    video_models.append((model_name, display_name, description))
                elif 'vision' in model_name.lower() or 'pro-vision' in model_name.lower():
                    vision_models.append((model_name, display_name, description))
                elif 'gemini' in model_name.lower():
                    text_models.append((model_name, display_name, description))
                else:
                    other_models.append((model_name, display_name, description))
            
            # 显示视频相关模型
            print("\n🎬 视频相关模型:")
            if video_models:
                for name, display, desc in video_models:
                    print(f"  📹 {name}")
                    if display:
                        print(f"     显示名: {display}")
                    if desc:
                        print(f"     描述: {desc[:100]}...")
            else:
                print("  ❌ 未找到视频相关模型")
            
            # 显示视觉模型
            print("\n👁️ 视觉模型:")
            if vision_models:
                for name, display, desc in vision_models[:5]:  # 只显示前5个
                    print(f"  🖼️  {name}")
                    if display:
                        print(f"     显示名: {display}")
            else:
                print("  ❌ 未找到视觉模型")
            
            # 显示文本模型
            print("\n📝 文本模型:")
            if text_models:
                for name, display, desc in text_models[:5]:  # 只显示前5个
                    print(f"  📄 {name}")
                    if display:
                        print(f"     显示名: {display}")
            else:
                print("  ❌ 未找到文本模型")
            
            # 显示其他模型
            if other_models:
                print(f"\n🔧 其他模型 ({len(other_models)}个):")
                for name, display, desc in other_models[:3]:  # 只显示前3个
                    print(f"  ⚙️  {name}")
            
            # 检查支持的方法
            print("\n🔍 检查模型支持的方法...")
            test_models = [
                "models/gemini-1.5-flash",
                "models/gemini-1.5-pro",
                "models/gemini-pro-vision"
            ]
            
            for model_name in test_models:
                if any(model_name in m[0] for m in text_models + vision_models):
                    print(f"\n测试模型: {model_name}")
                    check_model_methods(model_name, api_key)
            
            return True
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 检查模型时出错: {str(e)}")
        return False


def check_model_methods(model_name, api_key):
    """检查特定模型支持的方法"""
    try:
        # 尝试generateContent方法
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Hello, can you generate video content?"
                }]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ 支持generateContent方法")
            result = response.json()
            if "candidates" in result:
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"  📄 响应示例: {content[:100]}...")
        else:
            print(f"  ❌ 不支持generateContent方法: {response.status_code}")
            if response.status_code == 400:
                error_info = response.json()
                print(f"     错误: {error_info.get('error', {}).get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"  ❌ 测试方法时出错: {str(e)}")


def suggest_alternatives():
    """建议替代方案"""
    print("\n💡 VEO 3.0替代方案建议:")
    print("=" * 50)
    
    print("\n1. 使用现有的视觉模型进行图像到文本描述:")
    print("   - models/gemini-1.5-pro-vision")
    print("   - models/gemini-pro-vision")
    
    print("\n2. 结合其他视频生成服务:")
    print("   - RunwayML Gen-2")
    print("   - Stability AI Video")
    print("   - Pika Labs")
    
    print("\n3. 等待VEO 3.0正式发布:")
    print("   - 关注Google AI更新")
    print("   - 申请早期访问权限")
    
    print("\n4. 使用模拟模式进行开发:")
    print("   - 设置VEO3_MOCK_MODE=true")
    print("   - 完善其他功能模块")


def main():
    """主函数"""
    print("🚀 Google AI API模型检查工具")
    print("=" * 50)
    
    if check_available_models():
        suggest_alternatives()
        
        print("\n📋 下一步建议:")
        print("1. 如果找到了视频模型，更新VEO3工具使用正确的模型名")
        print("2. 如果没有视频模型，考虑使用替代方案")
        print("3. 继续使用模拟模式进行开发")
        
        return True
    else:
        print("\n❌ 模型检查失败")
        print("请检查API密钥和网络连接")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)