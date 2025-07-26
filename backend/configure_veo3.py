#!/usr/bin/env python3
"""
VEO 3.0交互式配置脚本
帮助用户完成VEO 3.0 Gemini API的配置
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def print_header():
    """打印配置向导标题"""
    print("🎬" + "="*50)
    print("    VEO 3.0 Gemini API 配置向导")
    print("="*50 + "🎬")
    print()


def check_internet_connection():
    """检查网络连接"""
    print("🔍 检查网络连接...")
    
    try:
        import requests
        response = requests.get("https://ai.google.dev", timeout=10)
        if response.status_code == 200:
            print("✅ 网络连接正常")
            return True
        else:
            print("❌ 网络连接异常")
            return False
    except Exception as e:
        print(f"❌ 网络连接失败: {str(e)}")
        return False


def get_api_key_from_user():
    """从用户获取API密钥"""
    print("\n🔐 配置Google AI API密钥:")
    print("请访问 https://aistudio.google.com/app/apikey 获取API密钥")
    
    current_key = os.getenv('VIDEO_GENERATE_API_KEY', '')
    if current_key:
        print(f"当前API密钥: {current_key[:20]}...")
        use_current = input("是否使用当前密钥? (y/n): ").strip().lower()
        if use_current == 'y':
            return current_key
    
    while True:
        new_key = input("请输入Google AI API密钥: ").strip()
        if new_key:
            if len(new_key) < 20:
                print("❌ API密钥长度不足，请检查是否正确")
                continue
            return new_key
        else:
            print("❌ API密钥不能为空")


def check_veo3_access():
    """检查VEO 3.0访问权限"""
    print("\n🤖 检查VEO 3.0访问权限...")
    
    print("请确认以下事项:")
    print("1. 是否已申请VEO 3.0访问权限?")
    print("2. 申请是否已被批准?")
    print("3. API密钥是否有足够的配额?")
    
    access_status = input("\n是否已获得VEO 3.0访问权限? (y/n): ").strip().lower()
    
    if access_status == 'y':
        print("✅ VEO 3.0访问权限确认")
        return True
    else:
        print("❌ 需要先申请VEO 3.0访问权限")
        print("请访问: https://ai.google.dev/gemini-api/docs/video")
        print("查看最新的访问申请流程")
        return False


def test_api_connection(api_key):
    """测试API连接"""
    print("\n🧪 测试API连接...")
    
    try:
        import requests
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API连接成功")
            
            # 检查是否有VEO模型
            models = response.json()
            veo_models = [model for model in models.get('models', []) 
                         if 'veo' in model.get('name', '').lower()]
            
            if veo_models:
                print(f"✅ 找到VEO模型: {len(veo_models)}个")
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


def update_env_file(key, value):
    """更新.env文件"""
    env_file = Path('.env')
    
    if env_file.exists():
        # 读取现有内容
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # 更新或添加键值对
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'{key}={value}\n')
        
        # 写回文件
        with open(env_file, 'w') as f:
            f.writelines(lines)
    else:
        # 创建新文件
        with open(env_file, 'w') as f:
            f.write(f'{key}={value}\n')


def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置...")
    
    # 设置为真实模式
    update_env_file('VEO3_MOCK_MODE', 'false')
    os.environ['VEO3_MOCK_MODE'] = 'false'
    
    try:
        result = subprocess.run([
            'python', 'test_gemini_veo3.py'
        ], capture_output=True, text=True)
        
        print("测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 配置测试成功!")
            return True
        else:
            print("❌ 配置测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return False


def main():
    """主配置流程"""
    print_header()
    
    # 检查网络连接
    if not check_internet_connection():
        print("\n请检查网络连接，然后重新运行此脚本")
        return False
    
    # 获取API密钥
    api_key = get_api_key_from_user()
    if not api_key:
        print("\n❌ API密钥配置失败")
        return False
    
    # 更新环境变量
    update_env_file('VIDEO_GENERATE_API_KEY', api_key)
    os.environ['VIDEO_GENERATE_API_KEY'] = api_key
    print("✅ API密钥已保存到.env文件")
    
    # 设置为真实模式
    update_env_file('VEO3_MOCK_MODE', 'false')
    os.environ['VEO3_MOCK_MODE'] = 'false'
    print("✅ 已切换到真实API模式")
    
    # 测试API连接
    if test_api_connection(api_key):
        print("✅ API连接测试成功")
    else:
        print("⚠️  API连接测试失败，但配置已保存")
    
    # 测试配置
    if test_configuration():
        print("\n🎉 VEO 3.0配置完成!")
        print("\n下一步:")
        print("1. 运行完整管道测试: python test_complete_pipeline.py")
        print("2. 启动API服务器: python run_api.py")
        return True
    else:
        print("\n❌ 配置测试失败，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)