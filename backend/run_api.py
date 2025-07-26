#!/usr/bin/env python3
"""
启动Spark AI Flask API服务器
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.api.app import run_app


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动Spark AI Flask API服务器')
    
    parser.add_argument(
        '--config', 
        choices=['development', 'production', 'testing'],
        default='development',
        help='配置环境 (默认: development)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='监听主机地址 (默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='监听端口 (默认: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    args = parser.parse_args()
    
    # 启动服务器
    run_app(
        config_name=args.config,
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()