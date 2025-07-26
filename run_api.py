#!/usr/bin/env python3
"""
启动Spark AI视频生成API服务器
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.api.app import run_app

if __name__ == "__main__":
    print("🚀 启动Spark AI视频生成API服务器...")
    print("📖 API文档: http://localhost:5000/api/docs")
    print("🏥 健康检查: http://localhost:5000/api/health")
    print("🎬 视频生成: http://localhost:5000/api/video/")
    print("\n按 Ctrl+C 停止服务器")
    
    try:
        # 启动服务器
        run_app(
            config_name='default',
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")