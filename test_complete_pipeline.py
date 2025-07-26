#!/usr/bin/env python3
"""
测试完整的Maker Crew视频生成流水线
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from complete_maker_pipeline import CompleteMakerPipeline


def test_project_extraction():
    """测试项目提取功能"""
    print("🧪 测试1: 项目提取功能")
    print("=" * 50)
    
    pipeline = CompleteMakerPipeline()
    
    # 列出可用项目
    projects = pipeline.list_available_projects()
    print(f"📁 找到项目: {projects}")
    
    if not projects:
        print("❌ 没有可用项目，创建测试项目...")
        create_test_project()
        projects = pipeline.list_available_projects()
    
    if projects:
        test_project = projects[0]
        print(f"🔍 测试项目: {test_project}")
        
        # 提取提示词
        prompts = pipeline.extract_project_prompts(test_project)
        print(f"📋 提取到 {len(prompts)} 个提示词")
        
        if prompts:
            print("✅ 项目提取测试通过")
            return test_project, prompts
        else:
            print("❌ 项目提取测试失败")
            return None, []
    else:
        print("❌ 无法找到测试项目")
        return None, []


def test_video_generation(project_id: str, prompts: list):
    """测试视频生成功能（仅测试第一个提示词）"""
    print(f"\n🧪 测试2: 视频生成功能")
    print("=" * 50)
    
    if not prompts:
        print("❌ 没有提示词可以测试")
        return []
    
    pipeline = CompleteMakerPipeline()
    
    # 只测试第一个提示词
    test_prompts = prompts[:1]
    print(f"🎬 测试生成 {len(test_prompts)} 个视频片段")
    
    clips = pipeline.generate_video_clips(project_id, test_prompts)
    
    if clips:
        successful_clips = [c for c in clips if c.get("status") == "completed"]
        print(f"✅ 生成测试完成: {len(successful_clips)}/{len(clips)} 成功")
        return clips
    else:
        print("❌ 视频生成测试失败")
        return []


def test_video_assembly(project_id: str, clips: list):
    """测试视频拼接功能"""
    print(f"\n🧪 测试3: 视频拼接功能")
    print("=" * 50)
    
    if not clips:
        print("❌ 没有视频片段可以测试")
        return {}
    
    pipeline = CompleteMakerPipeline()
    
    # 测试拼接
    result = pipeline.assemble_final_video(
        project_id=project_id,
        video_clips=clips,
        video_title="Test_Video"
    )
    
    if result.get("status") == "completed":
        print("✅ 视频拼接测试通过")
        return result
    else:
        print(f"❌ 视频拼接测试失败: {result.get('error', 'Unknown error')}")
        return result


def test_complete_pipeline():
    """测试完整流水线"""
    print(f"\n🧪 测试4: 完整流水线")
    print("=" * 50)
    
    pipeline = CompleteMakerPipeline()
    projects = pipeline.list_available_projects()
    
    if not projects:
        print("❌ 没有可用项目")
        return
    
    test_project = projects[0]
    print(f"🚀 测试完整流水线，项目: {test_project}")
    
    # 运行完整流水线（但只处理前2个提示词以节省时间）
    result = pipeline.run_complete_pipeline(test_project, "Complete_Test_Video")
    
    if result.get("status") == "completed":
        print("✅ 完整流水线测试通过")
    else:
        print(f"❌ 完整流水线测试失败: {result.get('error', 'Unknown error')}")
    
    return result


def create_test_project():
    """创建测试项目"""
    print("🔧 创建测试项目...")
    
    test_project_id = "test_project_001"
    project_dir = Path("projects/projects") / test_project_id
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试提示词
    test_prompts = [
        {
            "shot_id": 1,
            "veo3_prompt": "A beautiful sunrise over mountains, cinematic shot, golden hour lighting",
            "duration": 5,
            "character_reference_images": []
        },
        {
            "shot_id": 2,
            "veo3_prompt": "A peaceful lake with reflections, calm water, nature documentary style",
            "duration": 5,
            "character_reference_images": []
        }
    ]
    
    # 保存提示词文件
    prompts_file = scripts_dir / "video_prompts.json"
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(test_prompts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 测试项目已创建: {project_dir}")
    print(f"📁 提示词文件: {prompts_file}")


def run_all_tests():
    """运行所有测试"""
    print("🧪 Maker Crew 流水线测试套件")
    print("=" * 80)
    
    try:
        # 测试1: 项目提取
        project_id, prompts = test_project_extraction()
        
        if not project_id:
            print("❌ 项目提取失败，无法继续测试")
            return
        
        # 测试2: 视频生成（仅测试一个片段）
        clips = test_video_generation(project_id, prompts)
        
        # 测试3: 视频拼接
        if clips:
            assembly_result = test_video_assembly(project_id, clips)
        
        # 测试4: 完整流水线（可选，耗时较长）
        run_full_test = input("\n是否运行完整流水线测试？(y/N): ").strip().lower()
        if run_full_test == 'y':
            complete_result = test_complete_pipeline()
        
        print("\n" + "=" * 80)
        print("🎉 测试完成!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")


def quick_demo():
    """快速演示"""
    print("🎬 Maker Crew 快速演示")
    print("=" * 50)
    
    try:
        pipeline = CompleteMakerPipeline()
        projects = pipeline.list_available_projects()
        
        if not projects:
            print("创建演示项目...")
            create_test_project()
            projects = pipeline.list_available_projects()
        
        if projects:
            demo_project = projects[0]
            print(f"🚀 演示项目: {demo_project}")
            
            # 只提取和显示提示词，不实际生成视频
            prompts = pipeline.extract_project_prompts(demo_project)
            
            if prompts:
                print(f"\n📋 项目包含 {len(prompts)} 个视频提示词:")
                for prompt in prompts:
                    print(f"   镜头 {prompt['shot_id']}: {prompt['veo3_prompt'][:60]}...")
                
                print(f"\n💡 要生成实际视频，请运行:")
                print(f"   python complete_maker_pipeline.py")
                print(f"   然后选择项目: {demo_project}")
            else:
                print("❌ 无法提取提示词")
        else:
            print("❌ 无法创建演示项目")
            
    except Exception as e:
        print(f"❌ 演示失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_all_tests()
        elif sys.argv[1] == "demo":
            quick_demo()
        else:
            print("用法:")
            print("  python test_complete_pipeline.py test  # 运行测试")
            print("  python test_complete_pipeline.py demo  # 快速演示")
    else:
        print("🎬 Maker Crew 流水线测试")
        print("选择操作:")
        print("1. 快速演示")
        print("2. 运行测试")
        
        choice = input("请选择 (1-2): ").strip()
        
        if choice == "1":
            quick_demo()
        elif choice == "2":
            run_all_tests()
        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    main()