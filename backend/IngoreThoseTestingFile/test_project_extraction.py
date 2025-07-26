"""
简单测试：从projects/projects目录中提取文件
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_project_directory():
    """测试项目目录结构"""
    print("🔍 测试项目目录结构...")
    
    projects_base = Path("projects/projects")
    if not projects_base.exists():
        print(f"❌ 基础目录不存在: {projects_base}")
        return False
    
    print(f"✅ 基础目录存在: {projects_base}")
    
    # 列出所有项目
    project_dirs = [d for d in projects_base.iterdir() if d.is_dir()]
    print(f"📁 找到 {len(project_dirs)} 个项目目录:")
    
    for project_dir in project_dirs:
        print(f"   - {project_dir.name}")
    
    return project_dirs

def test_video_prompts_extraction(project_id: str):
    """测试从特定项目提取video_prompts.json"""
    print(f"\n📋 测试提取项目 {project_id} 的视频提示词...")
    
    try:
        # 构建文件路径
        prompts_path = Path("projects/projects") / project_id / "scripts" / "video_prompts.json"
        
        if not prompts_path.exists():
            print(f"❌ 文件不存在: {prompts_path}")
            return None
        
        print(f"✅ 文件存在: {prompts_path}")
        
        # 读取文件内容
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        
        print(f"✅ 成功读取JSON文件")
        print(f"📊 包含 {len(prompts_data)} 个视频提示词")
        
        # 验证数据结构
        if prompts_data:
            first_prompt = prompts_data[0]
            print(f"📝 第一个提示词结构:")
            print(f"   - shot_id: {first_prompt.get('shot_id')}")
            print(f"   - duration: {first_prompt.get('duration')}")
            print(f"   - veo3_prompt长度: {len(first_prompt.get('veo3_prompt', ''))}")
            print(f"   - 参考图片数量: {len(first_prompt.get('character_reference_images', []))}")
        
        return prompts_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 读取文件错误: {e}")
        return None

def test_veo3_tool_integration():
    """测试VEO3工具集成"""
    print(f"\n🔧 测试VEO3工具集成...")
    
    try:
        from src.spark.tools.veo3_crewai_tool import load_project_video_prompts
        print("✅ 成功导入VEO3 CrewAI工具")
        
        # 测试项目ID
        test_project_id = "c1c61a55-91c4-4084-957c-89ab4c9e529f"
        
        # 调用工具函数
        result = load_project_video_prompts.run(test_project_id)
        
        if result and not result.startswith("Error"):
            print("✅ 工具调用成功")
            
            # 尝试解析结果
            try:
                prompts_data = json.loads(result)
                print(f"✅ 工具返回了 {len(prompts_data)} 个提示词")
                return True
            except json.JSONDecodeError:
                print(f"⚠️ 工具返回非JSON格式: {result[:200]}...")
                return False
        else:
            print(f"❌ 工具调用失败: {result}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 工具测试错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 测试从projects/projects中提取文件")
    print("=" * 50)
    
    # 测试1: 项目目录结构
    project_dirs = test_project_directory()
    if not project_dirs:
        print("❌ 无法继续测试，项目目录为空")
        return
    
    # 测试2: 提取具体项目的视频提示词
    test_projects = [
        "c1c61a55-91c4-4084-957c-89ab4c9e529f",
        "7570de8d-2952-44ba-95ac-f9397c95ac0f",
        "60320249-473f-4214-892d-e99561c7da94"
    ]
    
    successful_extractions = 0
    
    for project_id in test_projects:
        prompts_data = test_video_prompts_extraction(project_id)
        if prompts_data:
            successful_extractions += 1
    
    # 测试3: VEO3工具集成
    tool_integration_success = test_veo3_tool_integration()
    
    # 总结
    print(f"\n📊 测试总结")
    print("=" * 50)
    print(f"找到项目目录: {len(project_dirs)}")
    print(f"成功提取视频提示词: {successful_extractions}/{len(test_projects)}")
    print(f"VEO3工具集成: {'✅ 成功' if tool_integration_success else '❌ 失败'}")
    
    if successful_extractions > 0:
        print("\n🎉 文件提取功能正常工作！")
        print("✅ 可以成功从projects/projects目录读取视频提示词")
    else:
        print("\n⚠️ 文件提取存在问题，请检查项目结构")

if __name__ == "__main__":
    main() 