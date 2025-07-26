#!/usr/bin/env python3
"""
Test script for Video Production Crew
测试视频制作团队的功能
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.spark.crews.maker.src.maker.crew import VideoProductionCrew


def test_video_production_crew():
    """测试视频制作团队"""
    try:
        # 使用现有项目进行测试
        project_id = "7570de8d-2952-44ba-95ac-f9397c95ac0f"
        
        print(f"开始测试视频制作团队，项目ID: {project_id}")
        
        # 初始化crew
        crew = VideoProductionCrew()
        
        # 处理项目
        result = crew.process_project(project_id)
        
        print("视频制作完成！")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_video_production_crew()