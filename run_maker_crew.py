#!/usr/bin/env python3
"""
Maker Crew 视频生成流水线启动脚本
简化版本，直接运行完整流程
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from complete_maker_pipeline import CompleteMakerPipeline


def main():
    """主函数"""
    print("🎬 Maker Crew 视频生成流水线")
    print("=" * 80)
    print("从项目提取prompt → VEO3生成视频片段 → 拼接最终视频")
    print("=" * 80)
    
    try:
        # 初始化流水线
        pipeline = CompleteMakerPipeline()
        
        # 列出可用项目
        available_projects = pipeline.list_available_projects()
        
        if not available_projects:
            print("❌ 没有找到可用的项目")
            print("请确保在 projects/projects/ 目录下有包含 scripts/video_prompts.json 的项目")
            return
        
        print(f"📁 找到 {len(available_projects)} 个可用项目:")
        for i, project in enumerate(available_projects, 1):
            print(f"   {i}. {project}")
        
        # 选择项目
        if len(available_projects) == 1:
            project_id = available_projects[0]
            print(f"\n🎯 自动选择唯一项目: {project_id}")
        else:
            while True:
                try:
                    choice = input(f"\n请选择项目 (1-{len(available_projects)}): ").strip()
                    
                    if choice.isdigit() and 1 <= int(choice) <= len(available_projects):
                        project_id = available_projects[int(choice) - 1]
                        break
                    else:
                        print("❌ 无效选择，请重试")
                except KeyboardInterrupt:
                    print("\n👋 退出程序")
                    return
        
        # 输入视频标题（可选）
        try:
            video_title = input(f"\n请输入视频标题 (回车使用默认): ").strip()
            if not video_title:
                video_title = f"Maker_Video_{project_id[:8]}"
        except KeyboardInterrupt:
            print("\n👋 退出程序")
            return
        
        print(f"\n🚀 开始处理项目: {project_id}")
        print(f"🎬 视频标题: {video_title}")
        print("⏳ 这可能需要几分钟时间，请耐心等待...")
        
        # 运行完整流水线
        result = pipeline.run_complete_pipeline(project_id, video_title)
        
        # 显示结果
        print("\n" + "=" * 80)
        print("🎉 流水线执行结果")
        print("=" * 80)
        
        if result.get("status") == "completed":
            print("✅ 视频生成成功!")
            
            outputs = result.get("outputs", {})
            if outputs:
                print("\n📁 生成的视频文件:")
                for version, path in outputs.items():
                    file_path = Path(path)
                    if file_path.exists():
                        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                        print(f"   📹 {version}: {path} ({file_size:.1f}MB)")
                    else:
                        print(f"   ❌ {version}: {path} (文件不存在)")
            
            thumbnail = result.get("thumbnail", "")
            if thumbnail and Path(thumbnail).exists():
                print(f"\n🖼️  缩略图: {thumbnail}")
            
            # 显示统计信息
            stats = result.get("pipeline_stats", {})
            if stats:
                print(f"\n📊 处理统计:")
                print(f"   ⏱️  总耗时: {stats.get('total_time_seconds', 0):.1f} 秒")
                print(f"   📝 处理提示词: {stats.get('total_prompts', 0)} 个")
                print(f"   🎬 生成片段: {stats.get('generated_clips', 0)} 个")
                print(f"   ✅ 成功片段: {stats.get('successful_clips', 0)} 个")
        
        else:
            print(f"❌ 视频生成失败")
            error = result.get('error', 'Unknown error')
            print(f"错误信息: {error}")
            
            # 显示部分统计信息
            stats = result.get("pipeline_stats", {})
            if stats:
                print(f"\n📊 执行统计:")
                print(f"   ⏱️  耗时: {stats.get('total_time_seconds', 0):.1f} 秒")
        
        print(f"\n📁 项目目录: projects/projects/{project_id}/")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()