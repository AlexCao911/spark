#!/usr/bin/env python3
"""
测试Maker Crew完整视频生成流水线
从projects/projects/下提取prompt -> 生成视频片段 -> 剪辑成长视频
"""

import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from src.spark.crews.maker.src.maker.crew import VideoProductionCrew
from complete_maker_pipeline import CompleteMakerPipeline


def test_crew_ai_approach(project_id: str):
    """测试使用CrewAI的方法"""
    print("🤖 测试方法1: 使用CrewAI框架")
    print("=" * 60)
    
    try:
        # 初始化CrewAI视频制作团队
        crew = VideoProductionCrew()
        
        # 运行完整流程
        result = crew.process_project(project_id)
        
        print("✅ CrewAI方法执行完成")
        print(f"📊 结果状态: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'completed':
            outputs = result.get('final_videos', {})
            if outputs:
                print("📁 生成的视频文件:")
                for version, path in outputs.items():
                    print(f"   {version}: {path}")
        
        return result
        
    except Exception as e:
        print(f"❌ CrewAI方法失败: {e}")
        return {"status": "failed", "error": str(e)}


def test_direct_pipeline_approach(project_id: str):
    """测试使用直接流水线的方法"""
    print("\n🔧 测试方法2: 使用直接流水线")
    print("=" * 60)
    
    try:
        # 初始化直接流水线
        pipeline = CompleteMakerPipeline()
        
        # 运行完整流程
        result = pipeline.run_complete_pipeline(project_id, "Maker_Crew_Test_Video")
        
        print("✅ 直接流水线方法执行完成")
        print(f"📊 结果状态: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'completed':
            outputs = result.get('outputs', {})
            if outputs:
                print("📁 生成的视频文件:")
                for version, path in outputs.items():
                    print(f"   {version}: {path}")
        
        return result
        
    except Exception as e:
        print(f"❌ 直接流水线方法失败: {e}")
        return {"status": "failed", "error": str(e)}


def compare_results(crew_result: Dict, pipeline_result: Dict):
    """比较两种方法的结果"""
    print("\n📊 结果对比分析")
    print("=" * 80)
    
    print(f"CrewAI方法状态: {crew_result.get('status', 'unknown')}")
    print(f"直接流水线状态: {pipeline_result.get('status', 'unknown')}")
    
    # 分析成功率
    crew_success = crew_result.get('status') == 'completed'
    pipeline_success = pipeline_result.get('status') == 'completed'
    
    if crew_success and pipeline_success:
        print("🎉 两种方法都成功完成!")
    elif crew_success:
        print("✅ CrewAI方法成功，直接流水线失败")
    elif pipeline_success:
        print("✅ 直接流水线成功，CrewAI方法失败")
    else:
        print("❌ 两种方法都失败了")
    
    # 比较输出文件
    crew_outputs = crew_result.get('final_videos', {}) or crew_result.get('outputs', {})
    pipeline_outputs = pipeline_result.get('outputs', {})
    
    if crew_outputs or pipeline_outputs:
        print("\n📁 输出文件对比:")
        print("CrewAI输出:")
        for version, path in crew_outputs.items():
            print(f"   {version}: {path}")
        
        print("直接流水线输出:")
        for version, path in pipeline_outputs.items():
            print(f"   {version}: {path}")


def main():
    """主测试函数"""
    print("🎬 Maker Crew 完整流水线测试")
    print("=" * 80)
    
    # 选择测试项目
    project_id = "7570de8d-2952-44ba-95ac-f9397c95ac0f"
    
    print(f"📁 测试项目: {project_id}")
    
    # 检查项目是否存在
    project_dir = Path("projects/projects") / project_id
    prompts_file = project_dir / "scripts" / "video_prompts.json"
    
    if not prompts_file.exists():
        print(f"❌ 项目提示词文件不存在: {prompts_file}")
        return
    
    # 显示项目信息
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    print(f"📊 项目信息:")
    print(f"   提示词数量: {len(prompts)}")
    print(f"   预计总时长: {len(prompts) * 5} 秒")
    print(f"   项目目录: {project_dir}")
    
    start_time = time.time()
    
    # 测试方法1: CrewAI
    crew_result = test_crew_ai_approach(project_id)
    
    # 测试方法2: 直接流水线
    pipeline_result = test_direct_pipeline_approach(project_id)
    
    # 比较结果
    compare_results(crew_result, pipeline_result)
    
    # 总结
    total_time = time.time() - start_time
    print(f"\n⏱️  总测试时间: {total_time:.2f} 秒")
    
    print("\n🏁 测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()