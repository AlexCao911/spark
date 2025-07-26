#!/usr/bin/env python3
"""
测试Script Crew：从项目中提取内容，执行故事扩展和视频提示生成
"""

import sys
import json
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from spark.crews.script.src.script.crew import ScriptGenerationCrew
from spark.project_manager import project_manager
from spark.config import config

def print_banner():
    """Print test banner."""
    print("=" * 80)
    print("🎬 Spark AI - Script Crew 测试")
    print("   项目提取 → 故事扩展 → 视频提示生成")
    print("=" * 80)

def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print("="*60)

def list_available_projects():
    """列出可用的项目"""
    print_section("可用项目列表")
    
    projects = project_manager.list_projects()
    
    if not projects:
        print("❌ 没有找到任何项目")
        return None
    
    print(f"📋 找到 {len(projects)} 个项目:")
    
    for i, project in enumerate(projects, 1):
        status_icon = "✅" if project['status'] == 'chatbot_complete' else "⚠️"
        print(f"\n{i}. {status_icon} {project['project_name']}")
        print(f"   ID: {project['project_id']}")
        print(f"   状态: {project['status']}")
        print(f"   主题: {project['theme']}")
        print(f"   创建时间: {project['created_at']}")
    
    # 返回最新的完成项目
    complete_projects = [p for p in projects if p['status'] == 'chatbot_complete']
    if complete_projects:
        return complete_projects[0]['project_id']
    else:
        print(f"\n⚠️  没有找到状态为'chatbot_complete'的项目")
        return projects[0]['project_id'] if projects else None

def test_project_loading(project_id):
    """测试项目数据加载"""
    print_section("第一阶段: 项目数据加载")
    
    try:
        project_data = project_manager.load_project_for_crew(project_id, "script")
        
        print("✅ 项目数据加载成功")
        print(f"   项目ID: {project_data['project_id']}")
        print(f"   项目目录: {project_data['project_dir']}")
        
        if 'story_outline' in project_data:
            story = project_data['story_outline']
            print(f"   📖 故事大纲: {story['title']}")
            print(f"   📝 故事概要: {story['summary'][:100]}...")
            print(f"   ⏱️  预估时长: {story['estimated_duration']}秒")
        
        if 'character_profiles' in project_data:
            characters = project_data['character_profiles']
            print(f"   👥 角色数量: {len(characters)}个")
            for i, char in enumerate(characters, 1):
                image_status = "✅" if char.get('image_url') else "❌"
                print(f"      {i}. {char['name']} ({char['role']}) {image_status}")
        
        return project_data
        
    except Exception as e:
        print(f"❌ 项目数据加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_crew_initialization():
    """测试Script Crew初始化"""
    print_section("第二阶段: Script Crew 初始化")
    
    try:
        # 检查API密钥
        missing_keys = config.get_missing_api_keys()
        if missing_keys:
            print(f"⚠️  缺少API密钥: {missing_keys}")
        else:
            print("✅ 所有API密钥配置完整")
        
        # 初始化Script Crew
        print("\n🤖 初始化Script Crew...")
        script_crew = ScriptGenerationCrew()
        
        print("✅ Script Crew初始化成功")
        print(f"   📋 代理数量: {len(script_crew.agents)}个")
        print(f"   📋 任务配置: {len(script_crew.tasks)}个")
        
        # 显示代理信息
        for agent_name, agent in script_crew.agents.items():
            print(f"   🤖 {agent_name}: {agent.role}")
        
        return script_crew
        
    except Exception as e:
        print(f"❌ Script Crew初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_story_expansion(script_crew, project_data):
    """测试故事扩展功能"""
    print_section("第三阶段: 故事扩展测试")
    
    if not script_crew or not project_data:
        print("❌ 无法测试 - 前置条件不满足")
        return None
    
    try:
        print("📖 开始故事扩展...")
        print("   这可能需要几分钟时间...")
        
        # 提取批准内容
        approved_content = script_crew._extract_approved_content(project_data)
        
        print(f"✅ 提取批准内容成功")
        print(f"   故事标题: {approved_content.story_outline.title}")
        print(f"   角色数量: {len(approved_content.character_profiles)}")
        
        # 执行故事扩展
        detailed_story = script_crew.expand_story_narrative(approved_content)
        
        print(f"✅ 故事扩展完成")
        print(f"   扩展后标题: {detailed_story.title}")
        print(f"   总时长: {detailed_story.total_duration}秒")
        print(f"   文本长度: {len(detailed_story.full_story_text)}字符")
        
        # 显示部分扩展内容
        preview = detailed_story.full_story_text[:200] + "..." if len(detailed_story.full_story_text) > 200 else detailed_story.full_story_text
        print(f"   📝 内容预览: {preview}")
        
        return detailed_story, approved_content
        
    except Exception as e:
        print(f"❌ 故事扩展失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_shot_generation(script_crew, detailed_story, approved_content):
    """测试视频提示生成"""
    print_section("第四阶段: 视频提示生成测试")
    
    if not script_crew or not detailed_story or not approved_content:
        print("❌ 无法测试 - 前置条件不满足")
        return None
    
    try:
        print("🎬 开始生成视频提示...")
        print("   这可能需要几分钟时间...")
        
        # 生成视频提示
        video_prompts = script_crew.break_into_shots_and_generate_prompts(
            detailed_story, 
            approved_content.character_profiles
        )
        
        print(f"✅ 视频提示生成完成")
        print(f"   生成镜头数: {len(video_prompts)}个")
        print(f"   总时长: {sum(p.duration for p in video_prompts)}秒")
        
        # 显示每个镜头
        for i, prompt in enumerate(video_prompts, 1):
            print(f"\n   🎬 镜头 {i} (时长: {prompt.duration}秒):")
            preview = prompt.veo3_prompt[:100] + "..." if len(prompt.veo3_prompt) > 100 else prompt.veo3_prompt
            print(f"      {preview}")
            
            if prompt.character_reference_images:
                print(f"      🖼️  角色参考图: {len(prompt.character_reference_images)}张")
        
        return video_prompts
        
    except Exception as e:
        print(f"❌ 视频提示生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_complete_processing(script_crew, project_id):
    """测试完整的处理流程"""
    print_section("第五阶段: 完整流程测试")
    
    if not script_crew:
        print("❌ 无法测试 - Script Crew未初始化")
        return None
    
    try:
        print("🔄 执行完整的Script Crew处理流程...")
        
        # 处理项目
        results = script_crew.process_project(project_id)
        
        print("✅ 完整流程处理成功")
        print(f"   项目ID: {results['project_id']}")
        print(f"   处理状态: {results['processing_status']}")
        
        # 显示结果摘要
        detailed_story = results['detailed_story']
        video_prompts = results['video_prompts']
        
        print(f"\n📖 详细故事:")
        print(f"   标题: {detailed_story.title}")
        print(f"   时长: {detailed_story.total_duration}秒")
        print(f"   字数: {len(detailed_story.full_story_text.split())}词")
        
        print(f"\n🎬 视频提示:")
        print(f"   镜头数量: {len(video_prompts)}")
        print(f"   总时长: {sum(p.duration for p in video_prompts)}秒")
        
        return results
        
    except Exception as e:
        print(f"❌ 完整流程处理失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def show_output_files(project_id):
    """显示生成的输出文件"""
    print_section("第六阶段: 输出文件检查")
    
    try:
        project_dir = Path("projects/projects") / project_id
        scripts_dir = project_dir / "scripts"
        
        if not scripts_dir.exists():
            print(f"❌ 脚本输出目录不存在: {scripts_dir}")
            return
        
        print(f"📁 脚本输出目录: {scripts_dir}")
        
        # 检查生成的文件
        files = list(scripts_dir.iterdir())
        
        for file_path in files:
            if file_path.is_file():
                size = file_path.stat().st_size
                size_str = f" ({size:,} bytes)" if size > 1024 else f" ({size} bytes)"
                print(f"   📄 {file_path.name}{size_str}")
                
                # 显示JSON文件的简要内容
                if file_path.suffix == '.json':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if 'title' in data:
                            print(f"      标题: {data['title']}")
                        if 'total_shots' in data:
                            print(f"      镜头数: {data['total_shots']}")
                        if isinstance(data, list) and len(data) > 0:
                            print(f"      数组长度: {len(data)}")
                    except:
                        pass
        
        # 显示处理摘要
        summary_file = scripts_dir / "script_crew_summary.json"
        if summary_file.exists():
            print(f"\n📊 处理摘要:")
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            print(f"   处理日期: {summary.get('processing_date', 'N/A')}")
            print(f"   状态: {summary.get('status', 'N/A')}")
            
            if 'detailed_story' in summary:
                story_info = summary['detailed_story']
                print(f"   故事词数: {story_info.get('word_count', 'N/A')}")
            
            if 'video_prompts' in summary:
                prompt_info = summary['video_prompts']
                print(f"   镜头总数: {prompt_info.get('total_shots', 'N/A')}")
                print(f"   有角色的镜头: {prompt_info.get('shots_with_characters', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 检查输出文件失败: {e}")

def main():
    """运行Script Crew完整测试"""
    print_banner()
    
    try:
        # 步骤1: 列出并选择项目
        project_id = list_available_projects()
        if not project_id:
            print("❌ 没有可用的项目进行测试")
            return
        
        print(f"\n🎯 选择项目: {project_id}")
        
        # 步骤2: 加载项目数据
        project_data = test_project_loading(project_id)
        
        # 步骤3: 初始化Script Crew
        script_crew = test_crew_initialization()
        
        # 步骤4: 测试故事扩展
        detailed_story, approved_content = test_story_expansion(script_crew, project_data)
        
        # 步骤5: 测试视频提示生成
        video_prompts = test_shot_generation(script_crew, detailed_story, approved_content)
        
        # 步骤6: 测试完整流程
        results = test_complete_processing(script_crew, project_id)
        
        # 步骤7: 检查输出文件
        show_output_files(project_id)
        
        # 最终总结
        print_section("测试完成总结")
        
        success_count = sum([
            bool(project_data),
            bool(script_crew),
            bool(detailed_story),
            bool(video_prompts),
            bool(results)
        ])
        
        print(f"🎯 完成度: {success_count}/5 个阶段")
        print(f"✅ 项目加载: {'成功' if project_data else '失败'}")
        print(f"✅ Crew初始化: {'成功' if script_crew else '失败'}")
        print(f"✅ 故事扩展: {'成功' if detailed_story else '失败'}")
        print(f"✅ 视频提示: {'成功' if video_prompts else '失败'}")
        print(f"✅ 完整流程: {'成功' if results else '失败'}")
        
        if success_count >= 4:
            print("\n🎉 Script Crew测试基本成功！")
            print("✨ 能够从项目中提取内容并执行任务")
            print(f"📁 输出已保存到: projects/projects/{project_id}/scripts/")
        else:
            print(f"\n⚠️  部分测试失败，请检查错误信息")
        
        if results:
            print(f"\n🔄 下一步可以:")
            print(f"   1. 检查生成的详细故事文本")
            print(f"   2. 查看VEO3视频提示")
            print(f"   3. 运行Maker Crew进行视频生成")
        
    except Exception as e:
        print(f"❌ Script Crew测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 