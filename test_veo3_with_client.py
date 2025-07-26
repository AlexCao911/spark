#!/usr/bin/env python3
"""
使用Google Cloud客户端库测试VEO 3.0
"""

import sys
import os
import json
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


def test_with_google_client():
    """使用Google Cloud客户端库测试VEO 3.0"""
    print("🔍 测试Google Cloud客户端库...")
    
    try:
        # 尝试导入Google Cloud客户端库
        from google.cloud import aiplatform
        from google.oauth2 import service_account
        import google.auth
        
        print("✅ Google Cloud客户端库已安装")
        
        # 获取项目配置
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'central-diode-467003-e0')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        print(f"📋 项目ID: {project_id}")
        print(f"📍 位置: {location}")
        
        # 初始化AI Platform
        aiplatform.init(project=project_id, location=location)
        print("✅ AI Platform初始化成功")
        
        # 尝试获取默认凭据
        try:
            credentials, project = google.auth.default()
            print(f"✅ 获取到默认凭据，项目: {project}")
        except Exception as e:
            print(f"❌ 无法获取默认凭据: {str(e)}")
            print("请运行: gcloud auth application-default login")
            return False
        
        # 测试VEO 3.0模型访问
        try:
            # ��建模型端点
            endpoint_name = f"projects/{project_id}/locations/{location}/publishers/google/models/veo-3.0-generate-preview"
            
            print(f"🤖 测试模型端点: {endpoint_name}")
            
            # 创建预测请求
            instances = [{
                "prompt": {
                    "parts": [{
                        "text": "一朵白云在蓝天中缓缓飘过，阳光明媚，画面清新自然"
                    }]
                },
                "generation_config": {
                    "duration_seconds": 3,
                    "aspect_ratio": "16:9",
                    "fps": 24
                }
            }]
            
            # 使用Vertex AI客户端进行预测
            from google.cloud.aiplatform.gapic import PredictionServiceClient
            from google.cloud.aiplatform_v1.types import PredictRequest
            
            client = PredictionServiceClient()
            
            request = PredictRequest(
                endpoint=endpoint_name,
                instances=[aiplatform.utils.to_value(instance) for instance in instances]
            )
            
            print("🎬 发送VEO 3.0预测请求...")
            response = client.predict(request=request)
            
            print("✅ VEO 3.0请求成功!")
            print(f"📄 响应: {response}")
            
            return True
            
        except Exception as e:
            print(f"❌ VEO 3.0模型测试失败: {str(e)}")
            
            # 检查是否是权限问题
            if "403" in str(e) or "permission" in str(e).lower():
                print("💡 可能的解决方案:")
                print("1. 确保您有VEO 3.0模型的访问权限")
                print("2. 访问模型页面申请访问: https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/veo-3.0-generate-preview")
                print("3. 检查项目是否启用了必要的API")
            
            return False
        
    except ImportError as e:
        print(f"❌ Google Cloud客户端库未安装: {str(e)}")
        print("请安装: pip install google-cloud-aiplatform")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_alternative_approach():
    """测试替代方案"""
    print("\n🔍 测试替代方案...")
    
    print("💡 VEO 3.0替代方案:")
    print("1. 使用Runway ML API")
    print("2. 使用Stable Video Diffusion")
    print("3. 使用Pika Labs API")
    print("4. 等待VEO 3.0公开访问")
    
    # 检查是否有其他视频生成API配置
    runway_key = os.getenv('RUNWAY_API_KEY')
    pika_key = os.getenv('PIKA_API_KEY')
    
    if runway_key:
        print(f"✅ 发现Runway API密钥: {runway_key[:20]}...")
    if pika_key:
        print(f"✅ 发现Pika API密钥: {pika_key[:20]}...")
    
    if not runway_key and not pika_key:
        print("💡 建议配置替代视频生成API:")
        print("   RUNWAY_API_KEY=your_runway_key")
        print("   PIKA_API_KEY=your_pika_key")


def main():
    """主函数"""
    print("🚀 VEO 3.0客户端库测试")
    print("=" * 40)
    
    # 测试Google Cloud客户端库
    success = test_with_google_client()
    
    # 如果失败，提供替代方案
    if not success:
        test_alternative_approach()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 VEO 3.0配置成功！")
    else:
        print("⚠️  VEO 3.0暂时不可用，建议使用替代方案")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)