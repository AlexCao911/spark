#!/usr/bin/env python3
"""
Spark AI API服务器启动脚本
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.spark.api.app import run_app


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Spark AI API服务器')
    
    parser.add_argument(
        '--config', '-c',
        choices=['development', 'production', 'testing', 'default'],
        default='development',
        help='配置环境 (默认: development)'
    )
    
    parser.add_argument(
        '--host', '-H',
        default='0.0.0.0',
        help='监听主机 (默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='监听端口 (默认: 5000)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='禁用调试模式'
    )
    
    args = parser.parse_args()
    
    # 确定调试模式
    debug = None
    if args.debug:
        debug = True
    elif args.no_debug:
        debug = False
    
    print(f"🚀 启动Spark AI API服务器")
    print(f"📋 配置: {args.config}")
    print(f"🌐 地址: http://{args.host}:{args.port}")
    print(f"📚 API文档: http://{args.host}:{args.port}/api/docs")
    print(f"❤️  健康检查: http://{args.host}:{args.port}/api/health")
    print("-" * 50)
    
    try:
        run_app(
            config_name=args.config,
            host=args.host,
            port=args.port,
            debug=debug
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()