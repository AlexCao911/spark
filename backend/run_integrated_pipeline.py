#!/usr/bin/env python3
"""
集成视频制作流水线启动脚本
顺序执行Script Crew和Maker Crew的完整视频制作流程
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.crews.integrated_video_pipeline import IntegratedVideoProductionPipeline


def show_project_status(pipeline: IntegratedVideoProductionPipeline, project_id: str):
    """显示项目详细状态"""
    status = pipeline.get_project_status(project_id)
    
    print(f"\n📊 项目状态详情:")
    print(f"   项目ID: {project_id}")
    print(f"   项目目录: {status['project_dir']}")
    
    # 显示文件状态
    files = status['files']
    print(f"\n📁 文件状态:")
    print(f"   ✅ 故事大纲: {'存在' if files['story_outline']['exists'] else '缺失'}")
    print(f"   ✅ 角色信息: {'存在' if files['characters']['exists'] else '缺失'}")
    print(f"   ✅ 已批准内容: {'存在' if files['approved_content']['exists'] else '缺失'}")
    print(f"   📝 详细故事: {'存在' if files['detailed_story']['exists'] else '缺失'}")
    print(f"   📝 视频提示词: {'存在' if files['video_prompts']['exists'] else '缺失'}")
    
    # 显示处理状态
    print(f"\n🎯 处理状态:")
    print(f"   📝 脚本准备: {'✅ 已完成' if status['script_ready'] else '❌ 未完成'}")
    print(f"   🎬 视频制作: {'✅ 已完成' if status['videos_ready'] else '❌ 未完成'}")
    print(f"   📹 视频片段: {status['video_clips_count']} 个")
    print(f"   🎞️  最终视频: {status['final_videos_count']} 个")


def main():
    """主函数"""
    print("🎬 集成视频制作流水线")
    print("=" * 80)
    print("Script Crew → Maker Crew 完整集成流程")
    print("自动顺序执行，无需手动干预")
    print("=" * 80)
    
    try:
        # 初始化集成流水线
        print("🔧 初始化集成流水线...")
        pipeline = IntegratedVideoProductionPipeline()
        
        # 列出可用项目
        available_projects = pipeline.list_available_projects()
        
        if not available_projects:
            print("❌ 没有找到可用的项目")
            print("请确保在 projects/projects/ 目录下有包含必要文件的项目")
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
        
        # 显示项目状态
        show_project_status(pipeline, project_id)
        
        # 询问是否强制重新生成脚本
        try:
            force_regen = input("\n是否强制重新生成脚本? (y/N): ").strip().lower()
            force_regenerate_script = force_regen in ['y', 'yes', '是']
        except KeyboardInterrupt:
            print("\n👋 退出程序")
            return
        
        # 输入视频标题
        try:
            video_title = input(f"\n请输入视频标题 (回车使用默认): ").strip()
            if not video_title:
                video_title = f"Integrated_Video_{project_id[:8]}"
        except KeyboardInterrupt:
            print("\n👋 退出程序")
            return
        
        print(f"\n🚀 启动集成视频制作流程")
        print(f"📁 项目: {project_id}")
        print(f"🎬 标题: {video_title}")
        print(f"🔄 重新生成脚本: {'是' if force_regenerate_script else '否'}")
        print("⏳ 这将执行完整的两阶段流程，请耐心等待...")
        
        # 记录开始时间
        start_time = time.time()
        
        # 运行完整流水线
        print("\n" + "🎯" * 20 + " 开始执行 " + "🎯" * 20)
        result = pipeline.run_complete_pipeline(
            project_id=project_id,
            video_title=video_title,
            force_regenerate_script=force_regenerate_script
        )
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 显示结果
        print("\n" + "=" * 80)
        print("🎉 集成流水线执行结果")
        print("=" * 80)
        
        print(f"⏱️  实际总耗时: {total_time:.1f} 秒")
        print(f"📊 流水线状态: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'completed':
            print("✅ 视频制作成功!")
            
            # 显示执行统计
            execution_summary = result.get('execution_summary', {})
            print(f"\n📊 执行统计:")
            print(f"   📝 Script Crew: {execution_summary.get('script_time_seconds', 0):.1f} 秒")
            print(f"   🎬 Maker Crew: {execution_summary.get('maker_time_seconds', 0):.1f} 秒")
            print(f"   🔄 脚本重新生成: {'是' if execution_summary.get('script_regenerated', False) else '否'}")
            
            # 显示Script Crew结果
            script_result = result.get('script_crew_result', {})
            print(f"\n📝 Script Crew结果:")
            print(f"   状态: {script_result.get('status', 'unknown')}")
            print(f"   故事标题: {script_result.get('detailed_story_title', 'Unknown')}")
            print(f"   视频提示词: {script_result.get('video_prompts_count', 0)} 个")
            
            # 显示最终视频文件
            final_videos = result.get('final_videos', {})
            if final_videos:
                print(f"\n📁 生成的视频文件:")
                for version, path in final_videos.items():
                    file_path = Path(path)
                    if file_path.exists():
                        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                        print(f"   📹 {version}: {path} ({file_size:.1f}MB)")
                    else:
                        print(f"   ❌ {version}: {path} (文件不存在)")
            
            # 显示缩略图
            thumbnail = result.get('thumbnail', '')
            if thumbnail and Path(thumbnail).exists():
                print(f"\n🖼️  缩略图: {thumbnail}")
            
            # 显示视频元数据
            video_metadata = result.get('video_metadata', {})
            if video_metadata and 'error' not in video_metadata:
                print(f"\n📊 视频元数据:")
                for key, value in video_metadata.items():
                    if key != 'error':
                        print(f"   {key}: {value}")
        
        elif result.get('status') == 'failed':
            print("❌ 视频制作失败")
            error = result.get('error', 'Unknown error')
            print(f"错误信息: {error}")
            
            # 显示部分执行统计
            execution_summary = result.get('execution_summary', {})
            if execution_summary:
                print(f"\n📊 执行统计:")
                print(f"   耗时: {execution_summary.get('total_time_seconds', 0):.1f} 秒")
                failed_at = execution_summary.get('failed_at', 'unknown')
                if failed_at != 'unknown':
                    print(f"   失败阶段: {failed_at}")
        
        else:
            print(f"⚠️  未知状态: {result.get('status', 'unknown')}")
        
        print(f"\n📁 项目目录: projects/projects/{project_id}/")
        print("🏁 集成流水线执行完成!")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()