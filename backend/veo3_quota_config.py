#!/usr/bin/env python3
"""
VEO3配额管理配置
用于调整API配额限制和重试策略
"""

import os
from pathlib import Path


class VEO3QuotaConfig:
    """VEO3配额管理配置类"""
    
    def __init__(self):
        # 基本配置
        self.max_retries = int(os.getenv('VEO3_MAX_RETRIES', '3'))
        self.quota_reset_interval = int(os.getenv('VEO3_QUOTA_RESET_INTERVAL', '3600'))  # 1小时
        self.consecutive_failure_threshold = int(os.getenv('VEO3_CONSECUTIVE_FAILURE_THRESHOLD', '3'))
        
        # 等待时间配置（秒）
        self.retry_wait_base = int(os.getenv('VEO3_RETRY_WAIT_BASE', '30'))
        self.quota_wait_time = int(os.getenv('VEO3_QUOTA_WAIT_TIME', '300'))  # 5分钟
        self.success_wait_time = int(os.getenv('VEO3_SUCCESS_WAIT_TIME', '5'))  # 成功后等待
        
        # 超时配置
        self.generation_timeout = int(os.getenv('VEO3_GENERATION_TIMEOUT', '300'))  # 5分钟
        
        # 模拟模式
        self.mock_mode = os.getenv('VEO3_MOCK_MODE', 'false').lower() == 'true'
        
        # 调试模式
        self.debug_mode = os.getenv('VEO3_DEBUG_MODE', 'false').lower() == 'true'
    
    def get_retry_wait_time(self, attempt: int) -> int:
        """获取重试等待时间（递增）"""
        return min(self.retry_wait_base * (attempt + 1), 300)  # 最多5分钟
    
    def get_quota_wait_time(self, consecutive_failures: int) -> int:
        """获取配额限制等待时间（递增）"""
        return min(self.quota_wait_time * consecutive_failures, 1800)  # 最多30分钟
    
    def should_skip_due_to_quota(self, consecutive_failures: int) -> bool:
        """判断是否应该因配额限制跳过"""
        return consecutive_failures >= self.consecutive_failure_threshold
    
    def print_config(self):
        """打印当前配置"""
        print("🔧 VEO3配额管理配置:")
        print(f"   最大重试次数: {self.max_retries}")
        print(f"   配额重置间隔: {self.quota_reset_interval/60:.0f} 分钟")
        print(f"   连续失败阈值: {self.consecutive_failure_threshold}")
        print(f"   基础重试等待: {self.retry_wait_base} 秒")
        print(f"   配额等待时间: {self.quota_wait_time/60:.0f} 分钟")
        print(f"   成功后等待: {self.success_wait_time} 秒")
        print(f"   生成超时: {self.generation_timeout/60:.0f} 分钟")
        print(f"   模拟模式: {'启用' if self.mock_mode else '禁用'}")
        print(f"   调试模式: {'启用' if self.debug_mode else '禁用'}")


def create_env_template():
    """创建环境变量模板文件"""
    template_content = """# VEO3配额管理配置
# 复制这些设置到你的.env文件中并根据需要调整

# 基本重试配置
VEO3_MAX_RETRIES=3                          # 每个视频片段的最大重试次数
VEO3_CONSECUTIVE_FAILURE_THRESHOLD=3        # 连续失败多少次后暂停

# 等待时间配置（秒）
VEO3_RETRY_WAIT_BASE=30                     # 基础重试等待时间
VEO3_QUOTA_WAIT_TIME=300                    # 配额限制等待时间（5分钟）
VEO3_SUCCESS_WAIT_TIME=5                    # 成功后等待时间
VEO3_GENERATION_TIMEOUT=300                 # 单个视频生成超时（5分钟）

# 配额重置配置
VEO3_QUOTA_RESET_INTERVAL=3600              # 配额重置间隔（1小时）

# 模式配置
VEO3_MOCK_MODE=false                        # 是否启用模拟模式
VEO3_DEBUG_MODE=false                       # 是否启用调试模式

# 主要API密钥
VIDEO_GENERATE_API_KEY=your_api_key_here    # 你的VEO3 API密钥
"""
    
    template_path = Path(".env.veo3.template")
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"📄 已创建配置模板: {template_path}")
    print("请复制相关设置到你的.env文件中")


def main():
    """主函数 - 显示当前配置"""
    print("🔧 VEO3配额管理配置工具")
    print("=" * 60)
    
    config = VEO3QuotaConfig()
    config.print_config()
    
    print("\n📋 配置说明:")
    print("- 最大重试次数: 每个视频片段失败后的重试次数")
    print("- 连续失败阈值: 连续失败多少次后开始暂停")
    print("- 配额重置间隔: 配额限制后多久重新尝试")
    print("- 等待时间: 各种情况下的等待时间")
    
    print("\n🛠️  如需调整配置:")
    print("1. 在.env文件中添加相应的环境变量")
    print("2. 或者运行: python veo3_quota_config.py --create-template")
    
    # 检查是否需要创建模板
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--create-template':
        print("\n📄 创建配置模板...")
        create_env_template()


if __name__ == "__main__":
    main()