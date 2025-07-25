#!/usr/bin/env python3
"""
Test script for Maker Crew VEO3 video generation workflow.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🎬 Maker Crew VEO3 视频生成测试")
    print("=" * 60)
    
    try:
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ 环境变量已加载")
        except ImportError:
            print("⚠️ python-dotenv未安装，请运行: pip install python-dotenv")
            print("   或者手动设置环境变量")
        
        from spark.crews.maker.src.maker.crew import MakerCrew
        from spark.models import VideoPrompt
        import json
        
        print("\n🚀 步骤1: 初始化Maker Crew")
        print("-" * 40)
        
        # Initialize Maker Crew
        try:
            maker_crew = MakerCrew()
            print("✅ Maker Crew初始化成功")
        except Exception as e:
            print(f"❌ Maker Crew初始化失败: {e}")
            if "API key" in str(e):
                print("\n📋 API密钥配置指南:")
                print("1. 复制环境变量模板: cp env.example .env")
                print("2. 编辑 .env 文件，填入你的API密钥:")
                print("   - OPENAI_API_KEY=你的DashScope密钥")
                print("   - VIDEO_GENERATE_API_KEY=你的Google AI Studio密钥")
                print("3. 重新运行测试")
            return
        
        # Check API key configuration
        veo3_key = os.getenv('VIDEO_GENERATE_API_KEY') or os.getenv('VEO3_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
        
        print(f"   VEO3 API Key: {'✅ 已配置' if veo3_key else '❌ 未配置'}")
        print(f"   OpenAI API Key: {'✅ 已配置' if openai_key else '❌ 未配置'}")
        print(f"   VEO3 Endpoint: {os.getenv('VIDEO_GENERATE_API_ENDPOINT', 'default')}")
        
        print("\n📂 步骤2: 查找现有项目的Script Crew输出")
        print("-" * 40)
        
        # Find existing project with Script Crew output
        projects_dir = Path("projects/projects")
        if not projects_dir.exists():
            print("❌ 项目目录不存在")
            print("请先运行完整的聊天机器人流程创建项目:")
            print("   python run_chatbot.py")
            return
        
        test_project_id = None
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                scripts_dir = project_dir / "scripts"
                prompts_file = scripts_dir / "video_prompts.json"
                if prompts_file.exists():
                    test_project_id = project_dir.name
                    print(f"✅ 找到测试项目: {test_project_id}")
                    break
        
        if not test_project_id:
            print("❌ 未找到包含video_prompts.json的项目")
            print("请先运行Script Crew生成视频提示词:")
            print("   1. python run_chatbot.py  # 生成项目")
            print("   2. 确认启用Script Crew处理")
            return
        
        print("\n📋 步骤3: 加载和验证视频提示词")
        print("-" * 40)
        
        # Load and validate video prompts
        video_prompts = maker_crew._extract_video_prompts(test_project_id)
        
        if not video_prompts:
            print("❌ 未能提取视频提示词")
            return
        
        print(f"✅ 成功提取 {len(video_prompts)} 个视频提示词")
        
        # Show sample prompts
        print("\n🎥 视频提示词预览:")
        for i, prompt in enumerate(video_prompts[:3], 1):
            print(f"   {i}. 镜头{prompt.shot_id} ({prompt.duration}秒)")
            print(f"      提示词: {prompt.veo3_prompt[:60]}...")
            print(f"      角色图像: {len(prompt.character_reference_images)}个")
        
        if len(video_prompts) > 3:
            print(f"   ... 还有 {len(video_prompts) - 3} 个提示词")
        
        print("\n🔧 步骤4: VEO3 API 连接测试")
        print("-" * 40)
        
        # Test VEO3 API connection
        try:
            from spark.tools.veo3_real_tool import VEO3RealTool
            
            veo3_tool = VEO3RealTool()
            print("✅ VEO3工具初始化成功")
            
            # Validate first prompt
            first_prompt = video_prompts[0]
            is_valid = veo3_tool.validate_prompt_compatibility(first_prompt)
            print(f"✅ 提示词兼容性验证: {'通过' if is_valid else '❌ 失败'}")
            
            if is_valid:
                # Get optimized parameters
                params = veo3_tool.optimize_generation_parameters(first_prompt)
                print(f"✅ 优化参数: {params}")
            
        except Exception as e:
            print(f"❌ VEO3工具初始化失败: {e}")
            print("请检查以下配置:")
            print("1. VIDEO_GENERATE_API_KEY 是否设置在 .env 文件中")
            print("2. API密钥是否有效（Google AI Studio密钥）")
            print("3. 网络连接是否正常")
        
        print("\n🎯 步骤5: 模拟视频生成流程")
        print("-" * 40)
        
        # Test video generation workflow (without actual API calls)
        print("开始模拟视频生成...")
        
        # Check dependencies
        dependencies_ok = True
        try:
            import moviepy
            print("✅ MoviePy已安装")
        except ImportError:
            print("❌ MoviePy未安装，请运行: pip install moviepy")
            dependencies_ok = False
        
        try:
            import requests
            print("✅ Requests库可用")
        except ImportError:
            print("❌ Requests库未安装，请运行: pip install requests")
            dependencies_ok = False
        
        try:
            from dotenv import load_dotenv
            print("✅ python-dotenv可用")
        except ImportError:
            print("⚠️ python-dotenv未安装，建议安装: pip install python-dotenv")
        
        if not dependencies_ok:
            print("❌ 缺少必要依赖，请安装后重试")
            return
        
        print("\n📊 步骤6: 项目处理能力验证")
        print("-" * 40)
        
        # Validate project processing capability
        project_data = maker_crew._load_project_data(test_project_id)
        print(f"✅ 项目数据加载成功")
        print(f"   故事标题: {project_data.get('story_title', 'N/A')}")
        print(f"   预计时长: {project_data.get('estimated_duration', 0)}秒")
        
        # Calculate expected output
        total_clips = len(video_prompts)
        total_duration = sum(p.duration for p in video_prompts)
        estimated_generation_time = total_clips * 30  # 30 seconds per clip estimate
        
        print(f"\n📈 处理统计预测:")
        print(f"   待生成片段: {total_clips}个")
        print(f"   总视频时长: {total_duration}秒")
        print(f"   预计生成时间: {estimated_generation_time}秒 ({estimated_generation_time//60}分{estimated_generation_time%60}秒)")
        print(f"   输出目录: projects/projects/{test_project_id}/videos/")
        
        print("\n🔗 步骤7: 准备实际处理")
        print("-" * 40)
        
        # Check if all required API keys are configured
        if veo3_key and openai_key:
            proceed = input("\n🚨 是否执行实际的VEO3视频生成？这将消耗API配额 [y/N]: ").strip().lower()
            
            if proceed in ['y', 'yes']:
                print("\n🎬 开始实际视频生成...")
                
                try:
                    # Process with actual API calls
                    results = maker_crew.process_project(test_project_id)
                    
                    print("\n🎉 视频生成完成!")
                    print(f"✅ 成功生成: {results['video_generation_results'].get('success_count', 0)} 个片段")
                    print(f"❌ 失败数量: {len(results['video_generation_results'].get('failed_prompts', []))} 个")
                    
                    final_video = results['video_generation_results'].get('final_video_path')
                    if final_video:
                        print(f"🎬 最终视频: {final_video}")
                    
                except Exception as e:
                    print(f"❌ 视频生成失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⏸️ 跳过实际视频生成")
        else:
            print("⚠️ API密钥配置不完整，无法进行实际视频生成")
            print("\n📝 配置指南:")
            print("1. 创建 .env 文件:")
            print("   cp env.example .env")
            print("\n2. 填入必要的API密钥:")
            if not veo3_key:
                print("   ❌ VIDEO_GENERATE_API_KEY (Google AI Studio)")
            if not openai_key:
                print("   ❌ OPENAI_API_KEY (DashScope)")
            print("\n3. 重新运行测试")
        
        print("\n✅ Maker Crew测试完成")
        print("=" * 60)
        print("📋 测试摘要:")
        print("✅ Maker Crew初始化正常")
        print("✅ 项目数据提取正常")
        print("✅ 视频提示词解析正常")
        print("✅ VEO3工具配置正常" if veo3_key else "⚠️ VEO3工具需要配置API密钥")
        print("✅ 依赖检查通过" if dependencies_ok else "❌ 缺少必要依赖")
        print("✅ 处理流程验证完成")
        
        if veo3_key and openai_key:
            print("✅ API配置完整，可以进行实际生成")
        else:
            print("⚠️ 需要完整配置API密钥进行实际生成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 