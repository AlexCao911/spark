#!/usr/bin/env python3
"""
测试视频编辑工具 - 将已生成的视频片段拼接成最终视频
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.crews.maker.src.maker.tools.video_editing_tool import VideoEditingTool


def test_video_editing():
    """测试视频编辑功能"""
    print("🎞️  测试视频编辑工具")
    print("=" * 60)
    
    project_id = "7570de8d-2952-44ba-95ac-f9397c95ac0f"
    
    # 检查视频文件
    videos_dir = Path("projects/projects") / project_id / "videos"
    
    if not videos_dir.exists():
        print(f"❌ 视频目录不存在: {videos_dir}")
        return
    
    # 收集所有视频片段信息
    video_clips = []
    for i in range(1, 13):  # 12个片段
        video_file = videos_dir / f"shot_{i:03d}.mp4"
        if video_file.exists():
            file_size = video_file.stat().st_size
            print(f"✅ 找到片段 {i}: {video_file} ({file_size} bytes)")
            
            video_clips.append({
                "clip_id": i,
                "shot_id": i,
                "file_path": str(video_file),
                "duration": 5,
                "status": "completed"
            })
        else:
            print(f"❌ 缺少片段 {i}: {video_file}")
    
    if not video_clips:
        print("❌ 没有找到有效的视频片段")
        return
    
    print(f"\n📊 找到 {len(video_clips)} 个有效视频片段")
    
    # 初始化视频编辑工具
    try:
        video_editor = VideoEditingTool()
        print("✅ 视频编辑工具初始化成功")
    except Exception as e:
        print(f"❌ 视频编辑工具初始化失败: {e}")
        return
    
    # 执行视频拼接
    print("\n🎬 开始拼接视频...")
    
    try:
        result = video_editor._run(
            video_clips=json.dumps(video_clips),
            project_id=project_id,
            video_title="Maker_Crew_Test_Video",
            total_duration="60"
        )
        
        # 解析结果
        result_data = json.loads(result)
        
        print(f"\n📊 拼接结果:")
        print(f"状态: {result_data.get('status', 'unknown')}")
        
        if result_data.get('status') == 'completed':
            print("✅ 视频拼接成功!")
            
            outputs = result_data.get('outputs', {})
            if outputs:
                print("\n📁 生成的视频文件:")
                for version, path in outputs.items():
                    file_path = Path(path)
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        print(f"   {version}: {path} ({file_size} bytes)")
                    else:
                        print(f"   {version}: {path} (文件不存在)")
            
            thumbnail = result_data.get('thumbnail', '')
            if thumbnail:
                print(f"\n🖼️  缩略图: {thumbnail}")
            
            metadata = result_data.get('metadata', {})
            if metadata:
                print(f"\n📊 元数据:")
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
        
        else:
            print(f"❌ 视频拼接失败: {result_data.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ 视频拼接过程出错: {e}")


def main():
    """主函数"""
    print("🎬 Maker Crew 视频编辑测试")
    print("=" * 80)
    
    test_video_editing()
    
    print("\n🏁 测试完成!")


if __name__ == "__main__":
    main()