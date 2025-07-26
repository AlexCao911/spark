#!/usr/bin/env python3
"""
VEO 3.0快速设置脚本
一键配置和测试VEO 3.0 Gemini API
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """打印欢迎横幅"""
    print("🎬" + "="*60)
    print("    VEO 3.0 快速设置向导")
    print("    从Google Cloud迁移到Gemini API")
    print("="*60 + "🎬")
    print()


def check_requirements():
    """检查基本要求"""
    print("🔍 检查基本要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查必要的包
    required_packages = ['requests', 'pathlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必要的包: {', '.join(missing_packages)}")
        print("请运行: pip install requests")
        return False
    
    print("✅ 必要的包已安装")
    
    # 检查Google AI SDK
    try:
        import google.generativeai as genai
        print(f"✅ Google AI SDK已安装 (版本: {genai.__version__})")
    except ImportError:
        print("⚠️  Google AI SDK未安装")
        install_sdk = input("是否安装Google AI SDK? (y/n): ").strip().lower()
        if install_sdk == 'y':
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-generativeai'], 
                             check=True)
                print("✅ Google AI SDK安装成功")
            except subprocess.CalledProcessError:
                print("❌ Google AI SDK安装失败")
                print("请手动运行: pip install google-generativeai")
                return False
        else:
            print("⚠️  将使用REST API模式（功能受限）")
    
    return True


def get_api_key():
    """获取API密钥"""
    print("\n🔑 配置API密钥")
    print("请访问 https://aistudio.google.com/app/apikey 获取API密钥")
    print()
    
    # 检查现有密钥
    current_key = os.getenv('VIDEO_GENERATE_API_KEY', '')
    if current_key:
        print(f"发现现有API密钥: {current_key[:20]}...")
        use_existing = input("是否使用现有密钥? (y/n): ").strip().lower()
        if use_existing == 'y':
            return current_key
    
    # 获取新密钥
    while True:
        api_key = input("请输入Google AI API密钥: ").strip()
        if api_key:
            if len(api_key) < 20:
                print("❌ API密钥长度不足，请检查是否完整")
                continue
            return api_key
        else:
            print("❌ API密钥不能为空")


def update_env_file(api_key):
    """更新.env文件"""
    print("\n📝 更新配置文件...")
    
    env_file = Path('.env')
    
    # 读取现有内容
    lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # 更新或添加配置
    updated_keys = set()
    new_config = {
        'VIDEO_GENERATE_API_KEY': api_key,
        'VEO3_MOCK_MODE': 'false'
    }
    
    for i, line in enumerate(lines):
        for key, value in new_config.items():
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                updated_keys.add(key)
                break
    
    # 添加新的配置项
    for key, value in new_config.items():
        if key not in updated_keys:
            lines.append(f'{key}={value}\n')
    
    # 写回文件
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ 配置文件已更新")


def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    test_scripts = [
        ('SDK测试', 'test_veo3_sdk.py'),
        ('基础API测试', 'test_gemini_veo3.py'),
        ('完整功能测试', 'test_veo3_vertex_ai.py')
    ]
    
    results = {}
    
    for test_name, script in test_scripts:
        print(f"\n运行 {test_name}...")
        
        if not Path(script).exists():
            print(f"⚠️  测试脚本 {script} 不存在，跳过")
            results[test_name] = None
            continue
        
        try:
            result = subprocess.run([
                sys.executable, script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {test_name} 通过")
                results[test_name] = True
            else:
                print(f"❌ {test_name} 失败")
                print("错误输出:")
                print(result.stderr[:500])
                results[test_name] = False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} 超时")
            results[test_name] = False
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
            results[test_name] = False
    
    return results


def show_next_steps():
    """显示后续步骤"""
    print("\n🚀 设置完成！后续步骤:")
    print("=" * 40)
    
    print("\n1. 测试视频生成:")
    print("   python test_gemini_veo3.py")
    
    print("\n2. 运行完整管道测试:")
    print("   python test_complete_pipeline.py")
    
    print("\n3. 启动API服务器:")
    print("   python run_api.py")
    
    print("\n4. 查看文档:")
    print("   - VEO3_SETUP_GUIDE.md")
    print("   - VEO3_MIGRATION_GUIDE.md")
    
    print("\n📚 有用的资源:")
    print("   - Google AI Studio: https://aistudio.google.com/")
    print("   - Gemini API文档: https://ai.google.dev/gemini-api/docs")
    print("   - 视频生成文档: https://ai.google.dev/gemini-api/docs/video")


def main():
    """主函数"""
    print_banner()
    
    # 检查基本要求
    if not check_requirements():
        print("\n❌ 基本要求检查失败，请解决后重试")
        return False
    
    # 获取API密钥
    try:
        api_key = get_api_key()
    except KeyboardInterrupt:
        print("\n\n👋 设置已取消")
        return False
    
    # 更新配置文件
    update_env_file(api_key)
    
    # 设置环境变量
    os.environ['VIDEO_GENERATE_API_KEY'] = api_key
    os.environ['VEO3_MOCK_MODE'] = 'false'
    
    # 运行测试
    test_results = run_tests()
    
    # 显示结果
    print("\n" + "=" * 60)
    print("📊 设置结果总结:")
    
    passed_tests = sum(1 for result in test_results.values() if result is True)
    total_tests = len([r for r in test_results.values() if r is not None])
    
    for test_name, result in test_results.items():
        if result is None:
            status = "⚠️  跳过"
        elif result:
            status = "✅ 通过"
        else:
            status = "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n📈 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests > 0:
        print("🎉 VEO 3.0设置成功！")
        show_next_steps()
        return True
    else:
        print("❌ 设置失败，请检查API密钥和网络连接")
        print("\n💡 故障排除建议:")
        print("1. 确认API密钥正确且有效")
        print("2. 检查网络连接")
        print("3. 确认VEO 3.0访问权限")
        print("4. 查看详细错误信息")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 设置已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 设置过程中发生错误: {str(e)}")
        sys.exit(1)