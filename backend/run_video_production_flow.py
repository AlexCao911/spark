#!/usr/bin/env python3
"""
视频制作Flow启动脚本
使用CrewAI Flow集成Script Crew和Maker Crew
"""

import json
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.spark.crews.video_production_flow import VideoProductionFlow


def list_available_projects() -> list[str]:
    """列出可用的项目"""
    projects_base = Path("projects/projects")
    if not projects_base.exists():
        return []
    
    projects = []
    for project_dir in projects_base.iterdir():
        if project_dir.is_dir():
            # 检查是否有必要的项目文件
            has_story = (project_dir / "story_outline.json").exists()
            has_characters = (project_dir / "characters.json").exists() or (project_dir / "characters").exists()
            has_approved = (project_dir / "approved_content.json").exists()
            
            if has_story or has_characters or has_approved:
                projects.append(project_dir.name)
    
    return projects


def show_project_info(project_id: str):
    """显示项目信息"""
    project_dir = Path("projects/projects") / project_id
    
    print(f"\n📊 项目信息:")
    print(f"   项目ID: {project_id}")
    print(f"   项目目录: {project_dir}")
    
    # 检查已有文件
    files_status = []
    
    # 故事大纲
    story_file = project_dir / "story_outline.json"
    if story_file.exists():
        files_status.append("✅ 故事大纲")
        try:
            with open(story_file, 'r', encoding='utf-8') as f:
                story_data = json.load(f)
                print(f"   故事标题: {story_data.get('title', 'Unknown')}")
                print(f"   预计时长: {story_data.get('estimated_duration', 0)} 秒")
        except:
            pass
    else:
        files_status.append("❌ 故事大纲")
    
    # 角色信息
    characters_file = project_dir / "characters.json"
    characters_dir = project_dir / "characters"
    if characters_file.exists() or characters_dir.exists():
        files_status.append("✅ 角色信息")
    else:
        files_status.append("❌ 角色信息")
    
    # 已批准内容
    approved_file = project_dir / "approved_content.json"
    if approved_file.exists():
        files_status.append("✅ 已批准内容")
    else:
        files_status.append("❌ 已批准内容")
    
    # 脚本文件
    scripts_dir = project_dir / "scripts"
    if scripts_dir.exists():
        detailed_story = scripts_dir / "detailed_story.json"
        video_prompts = scripts_dir / "video_prompts.json"
        if detailed_story.exists() and video_prompts.exists():
            files_status.append("✅ 生成的脚本")
            try:
                with open(video_prompts, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                    print(f"   视频提示词: {len(prompts)} 个")
            except:
                pass
        else:
            files_status.append("❌ 生成的脚本")
    else:
        files_status.append("❌ 生成的脚本")
    
    # 视频文件
    videos_dir = project_dir / "videos"
    final_videos_dir = project_dir / "final_videos"
    if videos_dir.exists() or final_videos_dir.exists():
        files_status.append("✅ 视频文件")
        if videos_dir.exists():
            video_files = list(videos_dir.glob("*.mp4"))
            print(f"   视频片段: {len(video_files)} 个")
        if final_videos_dir.exists():
            final_files = list(final_videos_dir.glob("*.mp4"))
            print(f"   最终视频: {len(final_files)} 个")
    else:
        files_status.append("❌ 视频文件")
    
    print(f"   文件状态: {' | '.join(files_status)}")


def main():
    """主函数"""
    print("🎬 CrewAI Flow 视频制作流水线")
    print("=" * 80)
    print("Script Crew → Maker Crew 完整集成流程")
    print("=" * 80)
    
    try:
        # 列出可用项目
        available_projects = list_available_projects()
        
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
        
        # 显示项目信息
        show_project_info(project_id)
        
        # 询问是否强制重新生成脚本
        try:
            force_regen = input("\n是否强制重新生成脚本? (y/N): ").strip().lower()
            force_regenerate = force_regen in ['y', 'yes', '是']
        except KeyboardInterrupt:
            print("\n👋 退出程序")
            return
        
        # 输入视频标题
        try:
            video_title = input(f"\n请输入视频标题 (回车使用默认): ").strip()
            if not video_title:
                video_title = f"Flow_Video_{project_id[:8]}"
        except KeyboardInterrupt:
            print("\n👋 退出程序")
            return
        
        print(f"\n🚀 启动CrewAI Flow视频制作流程")
        print(f"📁 项目: {project_id}")
        print(f"🎬 标题: {video_title}")
        print(f"🔄 重新生成脚本: {'是' if force_regenerate else '否'}")
        print("⏳ 这可能需要较长时间，请耐心等待...")
        
        # 初始化Flow
        print("\n🔧 初始化CrewAI Flow...")
        flow = VideoProductionFlow()
        
        # 记录开始时间
        start_time = time.time()
        
        # 运行完整流水线
        print("🎯 执行完整视频制作流程...")
        result = flow.run_complete_pipeline(
            project_id=project_id,
            video_title=video_title,
            force_regenerate=force_regenerate
        )
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 显示结果
        print("\n" + "=" * 80)
        print("🎉 CrewAI Flow 执行结果")
        print("=" * 80)
        
        print(f"⏱️  总耗时: {total_time:.1f} 秒")
        print(f"📊 Flow状态: {result.get('flow_execution', 'unknown')}")
        print(f"🎬 制作状态: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'completed':
            print("✅ 视频制作成功!")
            
            final_videos = result.get('final_videos', {})
            if final_videos:
                print("\n📁 生成的视频文件:")
                for version, path in final_videos.items():
                    file_path = Path(path)
                    if file_path.exists():
                        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                        print(f"   📹 {version}: {path} ({file_size:.1f}MB)")
                    else:
                        print(f"   ❌ {version}: {path} (文件不存在)")
            
            thumbnail = result.get('thumbnail', '')
            if thumbnail and Path(thumbnail).exists():
                print(f"\n🖼️  缩略图: {thumbnail}")
            
            # 显示元数据
            metadata = result.get('metadata', {})
            if metadata and 'error' not in metadata:
                print(f"\n📊 制作统计:")
                for key, value in metadata.items():
                    if key != 'error':
                        print(f"   {key}: {value}")
        
        elif result.get('status') == 'failed':
            print("❌ 视频制作失败")
            error = result.get('error', 'Unknown error')
            print(f"错误信息: {error}")
        
        else:
            print(f"⚠️  未知状态: {result.get('status', 'unknown')}")
        
        print(f"\n📁 项目目录: projects/projects/{project_id}/")
        print("🏁 Flow执行完成!")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()