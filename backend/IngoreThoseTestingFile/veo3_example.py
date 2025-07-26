#!/usr/bin/env python3
"""
VEO3视频生成示例 - 使用更新后的VideoGenerationTool
"""

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.spark.crews.maker.src.maker.tools.video_generation_tool import VideoGenerationTool

def main():
    """主函数：演示VEO3视频生成"""
    print("🎬 VEO3视频生成示例")
    print("=" * 50)
    
    try:
        # 创建VideoGenerationTool实例
        video_tool = VideoGenerationTool()
        print("✅ VideoGenerationTool初始化成功")
        
        # 准备视频提示词
        video_prompts = [
            {
                "shot_id": 1,
                "veo3_prompt": "A cinematic shot of a majestic lion in the savannah at golden hour",
                "duration": 5,
                "character_reference_images": []
            },
            {
                "shot_id": 2,
                "veo3_prompt": "A serene lake surrounded by mountains with morning mist",
                "duration": 5,
                "character_reference_images": []
            }
        ]
        
        # 调用视频生成工具
        print(f"\n🎯 开始生成 {len(video_prompts)} 个视频片段...")
        
        result = video_tool._run(
            video_prompts=json.dumps(video_prompts),
            character_images="[]",
            project_id="veo3_demo"
        )
        
        # 解析结果
        result_data = json.loads(result)
        
        print("\n📊 生成结果:")
        print(f"项目ID: {result_data['project_id']}")
        print(f"总提示词数: {result_data['total_prompts']}")
        print(f"成功生成: {result_data['successful_clips']}")
        print(f"生成失败: {result_data['failed_clips']}")
        print(f"整体状态: {result_data['status']}")
        
        print("\n📁 生成的视频片段:")
        for clip in result_data['clips']:
            print(f"  片段 {clip['shot_id']}: {clip['file_path']} ({clip['status']})")
        
        if result_data['successful_clips'] > 0:
            print(f"\n✅ 成功生成 {result_data['successful_clips']} 个视频片段！")
            print(f"📂 视频保存在: projects/projects/{result_data['project_id']}/videos/")
        else:
            print("\n❌ 没有成功生成任何视频片段")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

if __name__ == "__main__":
    main()