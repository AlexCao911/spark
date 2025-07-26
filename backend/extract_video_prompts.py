"""
按照指定格式提取视频提示词
1. id用于表示输出顺序以及编排顺序
2. veo3_prompt 与 images打包成content 输入给 veo3 模型 
3. duration
"""

import json
from pathlib import Path
from typing import List, Dict, Any

def extract_video_prompts(project_id: str) -> List[Dict[str, Any]]:
    """
    从项目中提取视频提示词，按照指定格式返回
    
    Args:
        project_id: 项目ID
        
    Returns:
        格式化的视频提示词列表
    """
    try:
        # 构建文件路径
        prompts_path = Path("projects/projects") / project_id / "scripts" / "video_prompts.json"
        
        if not prompts_path.exists():
            print(f"❌ 文件不存在: {prompts_path}")
            return []
        
        # 读取原始数据
        with open(prompts_path, 'r', encoding='utf-8') as f:
            raw_prompts = json.load(f)
        
        # 转换为指定格式
        formatted_prompts = []
        
        for prompt in raw_prompts:
            formatted_prompt = {
                "id": prompt.get("shot_id"),  # 用于表示输出顺序以及编排顺序
                "content": {
                    "veo3_prompt": prompt.get("veo3_prompt", ""),
                    "images": prompt.get("character_reference_images", [])
                },
                "duration": prompt.get("duration", 5)
            }
            formatted_prompts.append(formatted_prompt)
        
        # 按ID排序确保正确的顺序
        formatted_prompts.sort(key=lambda x: x["id"])
        
        return formatted_prompts
        
    except Exception as e:
        print(f"❌ 提取错误: {e}")
        return []

def display_prompts(prompts: List[Dict[str, Any]], project_id: str):
    """显示提取的提示词"""
    print(f"\n📋 项目 {project_id} 的视频提示词:")
    print("=" * 60)
    
    total_duration = 0
    
    for prompt in prompts:
        print(f"\n🎬 镜头 {prompt['id']}:")
        print(f"   📝 提示词: {prompt['content']['veo3_prompt'][:50]}...")
        print(f"   ⏱️  时长: {prompt['duration']} 秒")
        print(f"   🖼️  参考图片: {len(prompt['content']['images'])} 张")
        
        total_duration += prompt['duration']
        
        # 显示图片URL（前50字符）
        for i, img_url in enumerate(prompt['content']['images']):
            print(f"      图片{i+1}: {img_url[:50]}...")
    
    print(f"\n📊 总计: {len(prompts)} 个镜头, 总时长: {total_duration} 秒")

def test_all_projects():
    """测试所有项目"""
    print("🧪 提取所有项目的视频提示词")
    print("=" * 60)
    
    # 找到所有项目
    projects_base = Path("projects/projects")
    if not projects_base.exists():
        print("❌ projects/projects 目录不存在")
        return
    
    project_dirs = [d.name for d in projects_base.iterdir() if d.is_dir()]
    print(f"📁 找到 {len(project_dirs)} 个项目")
    
    all_results = {}
    
    for project_id in project_dirs:
        print(f"\n🔍 处理项目: {project_id}")
        prompts = extract_video_prompts(project_id)
        
        if prompts:
            print(f"✅ 成功提取 {len(prompts)} 个提示词")
            all_results[project_id] = prompts
            display_prompts(prompts, project_id)
        else:
            print(f"❌ 提取失败")
    
    return all_results

def save_formatted_prompts(project_id: str, output_file: str = None):
    """保存格式化的提示词到文件"""
    prompts = extract_video_prompts(project_id)
    
    if not prompts:
        print(f"❌ 无法提取项目 {project_id} 的提示词")
        return
    
    if not output_file:
        output_file = f"formatted_prompts_{project_id}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)
        
        print(f"💾 格式化提示词已保存到: {output_file}")
        
        # 显示示例
        print(f"\n📝 格式示例（前2个镜头）:")
        for prompt in prompts[:2]:
            print(json.dumps(prompt, indent=2, ensure_ascii=False))
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ 保存失败: {e}")

def main():
    """主函数"""
    print("🎬 视频提示词提取工具")
    print("=" * 60)
    
    # 测试所有项目
    results = test_all_projects()
    
    if results:
        print(f"\n✅ 成功处理了 {len(results)} 个项目")
        
        # 保存第一个项目的格式化结果作为示例
        first_project = list(results.keys())[0]
        save_formatted_prompts(first_project)
        
        # 显示VEO3调用格式示例
        print(f"\n🔧 VEO3 API 调用格式示例:")
        print("=" * 40)
        first_prompts = results[first_project]
        if first_prompts:
            example_prompt = first_prompts[0]
            print("调用参数:")
            print(f"  prompt_text: '{example_prompt['content']['veo3_prompt']}'")
            print(f"  duration: {example_prompt['duration']}")
            print(f"  reference_images: {example_prompt['content']['images']}")
            print(f"  shot_id: {example_prompt['id']}")
    else:
        print("❌ 没有成功处理任何项目")

if __name__ == "__main__":
    main() 