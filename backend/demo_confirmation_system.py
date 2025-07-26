#!/usr/bin/env python3
"""
用户确认系统演示脚本

这个脚本演示了简化的用户确认系统的完整工作流程：
1. 用户在chatbot中描述视频创意
2. 系统生成story outline和角色档案
3. 用户确认内容
4. 系统保存确认的数据

使用方法:
python demo_confirmation_system.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.spark.models import UserIdea, StoryOutline, CharacterProfile
from src.spark.chatbot.simple_confirmation import confirmation_manager


def demo_confirmation_workflow():
    """演示确认工作流程"""
    
    print("🎬 Spark AI 用户确认系统演示")
    print("=" * 50)
    
    # 1. 模拟用户创意数据
    print("\n1. 创建示例用户创意...")
    user_idea = UserIdea(
        theme="太空冒险",
        genre="科幻",
        target_audience="成年人",
        duration_preference=180,
        basic_characters=["宇航员队长", "AI助手", "外星生物"],
        plot_points=[
            "发现神秘信号",
            "前往未知星球",
            "遭遇外星文明",
            "建立友好关系",
            "安全返回地球"
        ],
        visual_style="电影级",
        mood="紧张刺激"
    )
    print(f"✅ 用户创意: {user_idea.theme} - {user_idea.genre}")
    
    # 2. 创建故事大纲
    print("\n2. 创建故事大纲...")
    story_outline = StoryOutline(
        title="星际使者",
        summary="一支宇航员小队接收到来自深空的神秘信号，踏上了前往未知星球的危险旅程，最终与外星文明建立了友好关系。",
        narrative_text="""
        2157年，地球深空监测站接收到了一个来自银河系边缘的神秘信号。
        
        宇航员队长莎拉·陈带领着她的精英小队，驾驶着最先进的星际飞船"探索者号"前往信号源。
        船上的AI助手ARIA为他们提供导航和分析支持。
        
        经过数月的星际旅行，他们到达了一个美丽而神秘的星球。在那里，他们遇到了高度智慧的外星生物——
        一种能够通过生物发光进行交流的水晶生命体。
        
        起初双方都很谨慎，但通过ARIA的翻译协助和队长的外交智慧，人类与外星文明建立了史上第一次
        跨星际的友好接触。
        
        最终，宇航员们带着珍贵的友谊和科学发现安全返回地球，开启了人类文明的新纪元。
        """,
        estimated_duration=180
    )
    print(f"✅ 故事大纲: {story_outline.title}")
    print(f"   摘要: {story_outline.summary[:50]}...")
    
    # 3. 创建角色档案
    print("\n3. 创建角色档案...")
    character_profiles = [
        CharacterProfile(
            name="莎拉·陈",
            role="主角",
            appearance="35岁的亚裔女性，身材匀称，眼神坚定，短发利落",
            personality="勇敢、智慧、有领导力，善于外交和决策",
            backstory="前军事飞行员，后转为宇航员，有丰富的太空任务经验",
            motivations=["探索未知", "保护团队", "促进和平"],
            relationships={"ARIA": "信任的伙伴", "团队成员": "领导者"},
            image_url="https://example.com/sarah_chen.jpg",
            visual_consistency_tags=["亚裔", "女性", "队长", "宇航服"]
        ),
        CharacterProfile(
            name="ARIA",
            role="支持角色",
            appearance="全息投影形态，蓝色光芒，人形轮廓",
            personality="逻辑性强、忠诚、好奇心旺盛",
            backstory="最新一代的AI助手，专为深空探索任务设计",
            motivations=["协助人类", "学习新知识", "保护船员安全"],
            relationships={"莎拉·陈": "忠实助手", "外星生物": "翻译桥梁"},
            image_url="https://example.com/aria_ai.jpg",
            visual_consistency_tags=["AI", "全息", "蓝光", "未来科技"]
        ),
        CharacterProfile(
            name="泽塔",
            role="配角",
            appearance="水晶般透明的身体，内部有彩色光芒流动，高约2米",
            personality="智慧、和平、好奇",
            backstory="外星文明的使者，负责与其他种族的首次接触",
            motivations=["了解人类", "促进种族间理解", "保护自己的文明"],
            relationships={"莎拉·陈": "新朋友", "ARIA": "交流对象"},
            image_url="https://example.com/zeta_alien.jpg",
            visual_consistency_tags=["外星人", "水晶", "发光", "高大"]
        )
    ]
    
    for char in character_profiles:
        print(f"✅ 角色: {char.name} ({char.role})")
    
    # 4. 模拟用户确认过程
    print("\n4. 模拟用户确认过程...")
    print("📝 用户查看故事大纲...")
    print("👀 用户查看角色档案...")
    print("✅ 用户确认故事大纲: '很棒的科幻故事！'")
    print("✅ 用户确认角色档案: '角色设计很有创意，特别是AI助手ARIA'")
    
    # 5. 保存确认的内容
    print("\n5. 保存确认的内容...")
    result = confirmation_manager.save_approved_content(
        user_idea=user_idea,
        story_outline=story_outline,
        character_profiles=character_profiles,
        project_name="星际使者 - 演示项目"
    )
    
    if result["status"] == "success":
        print(f"✅ 内容保存成功！")
        print(f"   项目ID: {result['project_id']}")
        print(f"   项目名称: {result['project_name']}")
        print(f"   保存路径: {result['project_path']}")
        print(f"   创建文件: {', '.join(result['files_created'])}")
        
        # 6. 验证保存的内容
        print("\n6. 验证保存的内容...")
        loaded_content = confirmation_manager.load_approved_content(result['project_id'])
        
        if loaded_content:
            print("✅ 内容加载成功！")
            print(f"   项目名称: {loaded_content['project_name']}")
            print(f"   用户确认: {loaded_content['user_confirmed']}")
            print(f"   状态: {loaded_content['status']}")
            print(f"   角色数量: {len(loaded_content['character_profiles'])}")
            
            # 7. 展示项目列表
            print("\n7. 当前项目列表...")
            projects = confirmation_manager.list_projects()
            
            print(f"📁 共有 {len(projects)} 个项目:")
            for i, project in enumerate(projects, 1):
                print(f"   {i}. {project['project_name']}")
                print(f"      ID: {project['project_id'][:8]}...")
                print(f"      创建时间: {project['created_at'][:19].replace('T', ' ')}")
                print(f"      角色数量: {project['character_count']}")
                print()
            
            return result['project_id']
        else:
            print("❌ 内容加载失败")
            return None
    else:
        print(f"❌ 保存失败: {result['message']}")
        return None


def demo_project_management(project_id):
    """演示项目管理功能"""
    if not project_id:
        return
    
    print("\n" + "=" * 50)
    print("📁 项目管理功能演示")
    print("=" * 50)
    
    # 1. 模拟角色图片重新生成请求
    print("\n1. 模拟角色图片重新生成...")
    regen_result = confirmation_manager.regenerate_character_image(
        project_id=project_id,
        character_name="莎拉·陈",
        feedback="让她看起来更年轻一些，增加一些科技感的装备"
    )
    
    if regen_result["status"] == "success":
        print("✅ 角色图片重新生成请求已提交")
        print(f"   角色: {regen_result['character_name']}")
        print(f"   反馈: {regen_result['feedback']}")
    else:
        print(f"❌ 重新生成失败: {regen_result['message']}")
    
    # 2. 询问是否删除演示项目
    print(f"\n2. 清理演示数据...")
    response = input(f"是否删除演示项目 '{project_id[:8]}...'? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        delete_result = confirmation_manager.delete_project(project_id)
        if delete_result["status"] == "success":
            print("✅ 演示项目已删除")
        else:
            print(f"❌ 删除失败: {delete_result['message']}")
    else:
        print("📁 演示项目已保留，你可以稍后手动删除")


def main():
    """主函数"""
    try:
        print("开始用户确认系统演示...\n")
        
        # 运行确认工作流程演示
        project_id = demo_confirmation_workflow()
        
        # 运行项目管理演示
        demo_project_management(project_id)
        
        print("\n🎉 演示完成！")
        print("\n💡 要启动完整的Gradio界面，请运行:")
        print("   python -m src.spark.chatbot.confirmation_interface")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()