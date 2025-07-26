#!/usr/bin/env python3
"""
VEO 3.0配置状态检查脚本
快速检查当前的VEO 3.0配置状态
"""

import os
import sys
import subprocess
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


def check_environment_variables():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    required_vars = {
        'VIDEO_GENERATE_API_KEY': '视频生成API密钥',
        'GOOGLE_CLOUD_PROJECT_ID': 'Google Cloud项目ID',
        'GOOGLE_CLOUD_LOCATION': 'Google Cloud区域',
        'VEO3_MOCK_MODE': 'VEO3模拟模式'
    }
    
    all_configured = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'VIDEO_GENERATE_API_KEY':
                print(f"✅ {description}: {value[:20]}...")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: 未配置")
            all_configured = False
    
    return all_configured


def check_gcloud_status():
    """检查gcloud状态"""
    print("\n🔍 检查Google Cloud CLI状态...")
    
    try:
        # 检查gcloud安装
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Google Cloud CLI未安装")
            return False
        
        print("✅ Google Cloud CLI已安装")
        
        # 检查认证状态
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ gcloud认证状态:")
            # 只显示活跃账户
            lines = result.stdout.split('\n')
            for line in lines:
                if '*' in line:  # 活跃账户标记
                    print(f"   {line.strip()}")
        else:
            print("❌ gcloud认证失败")
            return False
        
        # 检查当前项目
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            project = result.stdout.strip()
            print(f"✅ 当前项目: {project}")
        else:
            print("❌ 无法获取当前项目")
        
        return True
        
    except FileNotFoundError:
        print("❌ Google Cloud CLI未安装")
        return False
    except Exception as e:
        print(f"❌ 检查gcloud状态失败: {e}")
        return False


def check_service_account():
    """检查服务账户配置"""
    print("\n🔍 检查服务账户配置...")
    
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path:
        if Path(credentials_path).exists():
            print(f"✅ 服务账户密钥文件: {credentials_path}")
            return True
        else:
            print(f"❌ 服务账户密钥文件不存在: {credentials_path}")
            return False
    else:
        print("⚠️  未配置服务账户密钥 (可能使用用户认证)")
        return True


def check_api_access():
    """检查API访问权限"""
    print("\n🔍 检查API访问权限...")
    
    try:
        # 检查Vertex AI API是否启用
        result = subprocess.run([
            'gcloud', 'services', 'list', '--enabled', 
            '--filter=name:aiplatform.googleapis.com'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and 'aiplatform.googleapis.com' in result.stdout:
            print("✅ Vertex AI API已启用")
        else:
            print("❌ Vertex AI API未启用")
            print("   运行: gcloud services enable aiplatform.googleapis.com")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查API访问权限失败: {e}")
        return False


def check_veo3_model_access():
    """检查VEO 3.0模型访问权限"""
    print("\n🔍 检查VEO 3.0模型访问权限...")
    
    print("📋 VEO 3.0访问检查清单:")
    print("1. 是否已申请VEO 3.0预览版访问权限?")
    print("2. 申请是否已被Google批准?")
    print("3. 项目是否有足够的API配额?")
    print("4. 是否在支持的区域 (us-central1)?")
    
    print("\n🔗 相关链接:")
    print("- VEO 3.0模型页面: https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/veo-3.0-generate-preview")
    print("- 申请访问权限: 在模型页面点击 'Request Access'")
    print("- 查看配额: https://console.cloud.google.com/iam-admin/quotas")
    
    return True


def provide_next_steps():
    """提供下一步操作建议"""
    print("\n📋 下一步操作建议:")
    
    mock_mode = os.getenv('VEO3_MOCK_MODE', 'true').lower()
    
    if mock_mode == 'true':
        print("🎭 当前运行在模拟模式")
        print("   - 优点: 可以测试完整流程")
        print("   - 缺点: 生成的是模拟视频文件")
        print("\n要启用真实VEO 3.0 API:")
        print("1. 完成上述所有配置检查")
        print("2. 运行配置向导: python configure_veo3.py")
        print("3. 或手动设置: VEO3_MOCK_MODE=false")
    else:
        print("🎬 当前配置为真实VEO 3.0模式")
        print("   - 需要确保所有配置都正确")
        print("   - 需要有VEO 3.0访问权限")
        print("\n测试配置:")
        print("1. 运行: python test_veo3_vertex_ai.py")
        print("2. 运行完整测试: python test_complete_pipeline.py")
    
    print("\n🚀 启动服务:")
    print("   python run_api.py")


def main():
    """主检查流程"""
    print("🔍" + "="*50)
    print("    VEO 3.0 配置状态检查")
    print("="*50 + "🔍")
    print()
    
    checks = [
        ("环境变量", check_environment_variables),
        ("Google Cloud CLI", check_gcloud_status),
        ("服务账户", check_service_account),
        ("API访问权限", check_api_access),
        ("VEO 3.0模型访问", check_veo3_model_access)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name}检查失败: {e}")
            results[check_name] = False
    
    # 总结
    print("\n" + "="*60)
    print("📊 检查结果总结:")
    
    passed = 0
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 所有检查通过！VEO 3.0配置就绪。")
    elif passed >= 3:
        print("⚠️  基础配置正常，但可能需要完善部分设置。")
    else:
        print("❌ 配置不完整，建议运行配置向导。")
    
    # 提供下一步建议
    provide_next_steps()
    
    return passed >= 3


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)