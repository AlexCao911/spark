"""
简单的Gradio确认界面，集成到chatbot中
"""

import gradio as gr
import logging
from typing import List, Tuple, Dict, Any, Optional
from .simple_confirmation import confirmation_manager
from .gradio_interface_fixed import ChatbotGradioInterfaceFixed
from ..models import UserIdea, StoryOutline, CharacterProfile

logger = logging.getLogger(__name__)


class ConfirmationGradioInterface(ChatbotGradioInterfaceFixed):
    """扩展的Gradio界面，包含确认功能"""
    
    def __init__(self):
        super().__init__()
        self.confirmation_manager = confirmation_manager
    
    def create_interface(self) -> gr.Blocks:
        """创建包含确认功能的Gradio界面"""
        
        with gr.Blocks(
            title="Spark AI - 完整工作流测试界面",
            theme=gr.themes.Soft(),
            css="""
            .status-indicator { padding: 8px 12px; border-radius: 6px; font-weight: bold; margin: 4px 0; }
            .status-complete { background-color: #d4edda; color: #155724; }
            .status-incomplete { background-color: #fff3cd; color: #856404; }
            .status-error { background-color: #f8d7da; color: #721c24; }
            .confirmation-section { border: 2px solid #28a745; border-radius: 8px; padding: 15px; margin: 10px 0; }
            .character-card { border: 1px solid #ddd; border-radius: 6px; padding: 10px; margin: 5px 0; }
            """
        ) as interface:
            
            gr.Markdown("# 🎬 Spark AI 视频生成 - 完整工作流测试")
            gr.Markdown("从聊天交互到内容确认的完整流程测试界面")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # 聊天界面（继承自父类）
                    gr.Markdown("## 💬 聊天界面")
                    
                    chatbot_display = gr.Chatbot(
                        label="对话",
                        height=400,
                        type="messages",
                        show_copy_button=True
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            placeholder="描述你的视频创意或继续对话...",
                            label="你的消息",
                            scale=4,
                            lines=1
                        )
                        send_btn = gr.Button("发送", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("清空聊天", variant="secondary")
                        reset_btn = gr.Button("重置会话", variant="stop")
                
                with gr.Column(scale=1):
                    # 状态和控制
                    gr.Markdown("## 📊 会话状态")
                    
                    status_display = gr.HTML(
                        value=self._get_status_html("incomplete", "准备开始"),
                        label="状态"
                    )
                    
                    completeness_display = gr.JSON(
                        label="创意完整性分析",
                        value={"status": "尚未分析"}
                    )
                    
                    # 操作按钮
                    with gr.Column():
                        structure_btn = gr.Button(
                            "📝 结构化当前创意",
                            variant="primary",
                            interactive=False
                        )
                        
                        generate_outline_btn = gr.Button(
                            "📖 生成故事大纲",
                            variant="primary",
                            interactive=False
                        )
                        
                        generate_characters_btn = gr.Button(
                            "👥 生成角色档案",
                            variant="primary",
                            interactive=False
                        )
            
            # 生成内容展示
            gr.Markdown("## 📋 生成内容")
            
            with gr.Tabs():
                with gr.TabItem("用户创意JSON"):
                    user_idea_display = gr.JSON(
                        label="结构化用户创意",
                        value={"status": "尚未生成结构化创意"}
                    )
                
                with gr.TabItem("故事大纲"):
                    story_outline_display = gr.JSON(
                        label="生成的故事大纲",
                        value={"status": "尚未生成故事大纲"}
                    )
                
                with gr.TabItem("角色档案"):
                    character_profiles_display = gr.JSON(
                        label="生成的角色档案",
                        value={"status": "尚未生成角色档案"}
                    )
            
            # 确认界面
            gr.Markdown("## ✅ 内容确认")
            
            with gr.Group(elem_classes=["confirmation-section"]):
                gr.Markdown("### 确认生成的内容")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**故事大纲确认**")
                        story_confirm_btn = gr.Button(
                            "✅ 确认故事大纲",
                            variant="primary",
                            interactive=False
                        )
                        story_feedback = gr.Textbox(
                            placeholder="对故事大纲的反馈（可选）",
                            label="故事反馈",
                            lines=2
                        )
                    
                    with gr.Column():
                        gr.Markdown("**角色确认**")
                        characters_confirm_btn = gr.Button(
                            "✅ 确认所有角色",
                            variant="primary",
                            interactive=False
                        )
                        characters_feedback = gr.Textbox(
                            placeholder="对角色的反馈（可选）",
                            label="角色反馈",
                            lines=2
                        )
                
                with gr.Row():
                    project_name_input = gr.Textbox(
                        placeholder="项目名称（可选，默认使用故事标题）",
                        label="项目名称",
                        scale=3
                    )
                    
                    final_save_btn = gr.Button(
                        "💾 保存确认内容",
                        variant="primary",
                        interactive=False,
                        scale=1
                    )
                
                confirmation_status = gr.HTML(
                    value='<div class="status-indicator status-incomplete">等待内容生成</div>',
                    label="确认状态"
                )
            
            # 项目管理
            gr.Markdown("## 📁 项目管理")
            
            with gr.Row():
                refresh_projects_btn = gr.Button("🔄 刷新项目列表", variant="secondary")
                
            projects_display = gr.Dataframe(
                headers=["项目ID", "项目名称", "创建时间", "状态", "角色数量"],
                label="已保存的项目",
                interactive=False
            )
            
            with gr.Row():
                project_id_input = gr.Textbox(
                    placeholder="输入项目ID",
                    label="项目ID",
                    scale=3
                )
                load_project_btn = gr.Button("📂 加载项目", variant="secondary", scale=1)
                delete_project_btn = gr.Button("🗑️ 删除项目", variant="stop", scale=1)
            
            # 原始对话记录
            with gr.TabItem("原始对话"):
                conversation_display = gr.JSON(
                    label="完整对话历史",
                    value=[]
                )
            
            # 事件处理函数
            def send_message_extended(message: str, history: List[Dict[str, str]]) -> Tuple:
                """扩展的发送消息函数"""
                result = self.send_message_base(message, history)
                
                # 检查是否可以开始确认流程
                completeness_data = result[3] if len(result) > 3 else {}
                can_confirm = (
                    self.structured_output is not None and 
                    self.story_outline is not None and 
                    self.character_profiles
                )
                
                return result + (can_confirm,)
            
            def confirm_story_outline(feedback: str) -> Tuple[str, bool]:
                """确认故事大纲"""
                try:
                    if not self.story_outline:
                        return (
                            self._get_status_html("error", "没有故事大纲可确认"),
                            False
                        )
                    
                    # 记录确认状态
                    self.story_confirmed = True
                    self.story_feedback = feedback
                    
                    status_html = self._get_status_html("complete", "故事大纲已确认")
                    can_save = self.story_confirmed and getattr(self, 'characters_confirmed', False)
                    
                    return status_html, can_save
                    
                except Exception as e:
                    logger.error(f"确认故事大纲时出错: {str(e)}")
                    return self._get_status_html("error", f"确认失败: {str(e)}"), False
            
            def confirm_characters(feedback: str) -> Tuple[str, bool]:
                """确认角色"""
                try:
                    if not self.character_profiles:
                        return (
                            self._get_status_html("error", "没有角色可确认"),
                            False
                        )
                    
                    # 记录确认状态
                    self.characters_confirmed = True
                    self.characters_feedback = feedback
                    
                    status_html = self._get_status_html("complete", "角色已确认")
                    can_save = getattr(self, 'story_confirmed', False) and self.characters_confirmed
                    
                    return status_html, can_save
                    
                except Exception as e:
                    logger.error(f"确认角色时出错: {str(e)}")
                    return self._get_status_html("error", f"确认失败: {str(e)}"), False
            
            def save_confirmed_content(project_name: str) -> str:
                """保存确认的内容"""
                try:
                    if not (getattr(self, 'story_confirmed', False) and 
                           getattr(self, 'characters_confirmed', False)):
                        return self._get_status_html("error", "请先确认故事大纲和角色")
                    
                    if not all([self.structured_output, self.story_outline, self.character_profiles]):
                        return self._get_status_html("error", "缺少必要的内容数据")
                    
                    # 保存内容
                    result = self.confirmation_manager.save_approved_content(
                        self.structured_output,
                        self.story_outline,
                        self.character_profiles,
                        project_name.strip() if project_name.strip() else None
                    )
                    
                    if result["status"] == "success":
                        return self._get_status_html(
                            "complete", 
                            f"内容已保存到项目: {result['project_name']} (ID: {result['project_id'][:8]}...)"
                        )
                    else:
                        return self._get_status_html("error", f"保存失败: {result['message']}")
                        
                except Exception as e:
                    logger.error(f"保存确认内容时出错: {str(e)}")
                    return self._get_status_html("error", f"保存失败: {str(e)}")
            
            def refresh_projects() -> List[List]:
                """刷新项目列表"""
                try:
                    projects = self.confirmation_manager.list_projects()
                    return [
                        [
                            p["project_id"][:8] + "...",
                            p["project_name"],
                            p["created_at"][:19].replace("T", " "),
                            p["status"],
                            str(p["character_count"])
                        ]
                        for p in projects
                    ]
                except Exception as e:
                    logger.error(f"刷新项目列表时出错: {str(e)}")
                    return []
            
            def load_project(project_id: str) -> Tuple[Dict, Dict, Dict, str]:
                """加载项目"""
                try:
                    if not project_id.strip():
                        return {}, {}, {}, self._get_status_html("error", "请输入项目ID")
                    
                    # 如果输入的是短ID，尝试匹配完整ID
                    projects = self.confirmation_manager.list_projects()
                    full_project_id = None
                    
                    for project in projects:
                        if project["project_id"].startswith(project_id.strip()):
                            full_project_id = project["project_id"]
                            break
                    
                    if not full_project_id:
                        full_project_id = project_id.strip()
                    
                    project_data = self.confirmation_manager.load_approved_content(full_project_id)
                    
                    if not project_data:
                        return {}, {}, {}, self._get_status_html("error", "项目不存在")
                    
                    return (
                        project_data.get("user_idea", {}),
                        project_data.get("story_outline", {}),
                        {"characters": project_data.get("character_profiles", [])},
                        self._get_status_html("complete", f"已加载项目: {project_data.get('project_name', 'Unknown')}")
                    )
                    
                except Exception as e:
                    logger.error(f"加载项目时出错: {str(e)}")
                    return {}, {}, {}, self._get_status_html("error", f"加载失败: {str(e)}")
            
            def delete_project(project_id: str) -> Tuple[List[List], str]:
                """删除项目"""
                try:
                    if not project_id.strip():
                        return [], self._get_status_html("error", "请输入项目ID")
                    
                    # 如果输入的是短ID，尝试匹配完整ID
                    projects = self.confirmation_manager.list_projects()
                    full_project_id = None
                    
                    for project in projects:
                        if project["project_id"].startswith(project_id.strip()):
                            full_project_id = project["project_id"]
                            break
                    
                    if not full_project_id:
                        full_project_id = project_id.strip()
                    
                    result = self.confirmation_manager.delete_project(full_project_id)
                    
                    if result["status"] == "success":
                        # 刷新项目列表
                        updated_projects = refresh_projects()
                        return updated_projects, self._get_status_html("complete", "项目已删除")
                    else:
                        return [], self._get_status_html("error", result["message"])
                        
                except Exception as e:
                    logger.error(f"删除项目时出错: {str(e)}")
                    return [], self._get_status_html("error", f"删除失败: {str(e)}")
            
            # 绑定事件处理器
            send_btn.click(
                fn=self.send_message_base,
                inputs=[user_input, chatbot_display],
                outputs=[chatbot_display, user_input, status_display, completeness_display, conversation_display]
            )
            
            user_input.submit(
                fn=self.send_message_base,
                inputs=[user_input, chatbot_display],
                outputs=[chatbot_display, user_input, status_display, completeness_display, conversation_display]
            )
            
            clear_btn.click(
                fn=self.clear_chat,
                outputs=[chatbot_display, user_input, status_display, completeness_display, conversation_display]
            )
            
            reset_btn.click(
                fn=self.reset_session,
                outputs=[
                    chatbot_display, user_input, status_display, completeness_display,
                    conversation_display, user_idea_display, story_outline_display, character_profiles_display
                ]
            )
            
            structure_btn.click(
                fn=self.structure_idea,
                outputs=[user_idea_display, status_display]
            )
            
            generate_outline_btn.click(
                fn=self.generate_story_outline,
                outputs=[story_outline_display, status_display]
            )
            
            generate_characters_btn.click(
                fn=self.generate_character_profiles,
                outputs=[character_profiles_display, status_display]
            )
            
            # 确认相关事件
            story_confirm_btn.click(
                fn=confirm_story_outline,
                inputs=[story_feedback],
                outputs=[confirmation_status, final_save_btn]
            )
            
            characters_confirm_btn.click(
                fn=confirm_characters,
                inputs=[characters_feedback],
                outputs=[confirmation_status, final_save_btn]
            )
            
            final_save_btn.click(
                fn=save_confirmed_content,
                inputs=[project_name_input],
                outputs=[confirmation_status]
            )
            
            # 项目管理事件
            refresh_projects_btn.click(
                fn=refresh_projects,
                outputs=[projects_display]
            )
            
            load_project_btn.click(
                fn=load_project,
                inputs=[project_id_input],
                outputs=[user_idea_display, story_outline_display, character_profiles_display, confirmation_status]
            )
            
            delete_project_btn.click(
                fn=delete_project,
                inputs=[project_id_input],
                outputs=[projects_display, confirmation_status]
            )
            
            # 动态更新按钮状态
            def update_confirmation_buttons(story_data: Dict, char_data: Dict) -> Tuple[bool, bool]:
                """更新确认按钮状态"""
                story_ready = isinstance(story_data, dict) and "title" in story_data
                char_ready = isinstance(char_data, dict) and "characters" in char_data
                return story_ready, char_ready
            
            story_outline_display.change(
                fn=lambda s, c: update_confirmation_buttons(s, c)[0],
                inputs=[story_outline_display, character_profiles_display],
                outputs=[story_confirm_btn]
            )
            
            character_profiles_display.change(
                fn=lambda s, c: update_confirmation_buttons(s, c)[1],
                inputs=[story_outline_display, character_profiles_display],
                outputs=[characters_confirm_btn]
            )
        
        return interface
    
    def send_message_base(self, message: str, history: List[Dict[str, str]]) -> Tuple:
        """基础发送消息函数（从父类继承并调用）"""
        if not message.strip():
            return history, "", self._get_status_html("error", "请输入消息"), {}, []
        
        try:
            # 调用父类的逻辑
            if not history:
                response_data = self.chatbot_core.engage_user(message)
            else:
                response_data = self.chatbot_core.continue_conversation(message)
            
            if response_data.get("status") == "error":
                status_html = self._get_status_html("error", f"错误: {response_data.get('error', '未知错误')}")
                return history, "", status_html, {}, []
            
            # 更新聊天历史
            new_history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response_data.get("response", "无响应")}
            ]
            
            # 更新状态
            is_complete = response_data.get("is_complete", False)
            missing_elements = response_data.get("missing_elements", [])
            
            if is_complete:
                status_html = self._get_status_html("complete", "创意看起来完整了！可以开始结构化。")
            else:
                status_html = self._get_status_html("incomplete", f"正在收集信息... 缺少: {', '.join(missing_elements)}")
            
            # 更新完整性分析
            completeness_data = {
                "is_complete": is_complete,
                "missing_elements": missing_elements,
                "message_count": len(new_history),
                "last_response_status": response_data.get("status")
            }
            
            # 更新对话显示
            conversation_data = self.chatbot_core.get_conversation_history()
            
            return (
                new_history,
                "",  # 清空输入
                status_html,
                completeness_data,
                conversation_data
            )
            
        except Exception as e:
            logger.error(f"发送消息时出错: {str(e)}")
            error_html = self._get_status_html("error", f"错误: {str(e)}")
            return history, message, error_html, {}, []
    
    def clear_chat(self) -> Tuple[List, str, str, Dict, List]:
        """清空聊天但保持会话"""
        return [], "", self._get_status_html("incomplete", "聊天已清空 - 会话保持"), {}, []
    
    def structure_idea(self) -> Tuple[Dict, str]:
        """结构化当前对话为UserIdea"""
        try:
            conversation_history = self.chatbot_core.get_conversation_history()
            if not conversation_history:
                return (
                    {"error": "没有对话可结构化"},
                    self._get_status_html("error", "没有找到对话")
                )
            
            # 结构化创意
            user_idea = self.idea_structurer.structure_conversation(conversation_history)
            if user_idea:
                self.structured_output = user_idea
                idea_dict = user_idea.model_dump()
                
                # 验证完整性
                validation = self.idea_structurer.validate_idea_completeness(user_idea)
                
                status_html = self._get_status_html(
                    "complete" if validation["is_complete"] else "incomplete",
                    f"创意已结构化！完整性: {validation['completeness_score']:.1%}"
                )
                
                return (idea_dict, status_html)
            else:
                return (
                    {"error": "结构化创意失败"},
                    self._get_status_html("error", "结构化创意失败")
                )
                
        except Exception as e:
            logger.error(f"结构化创意时出错: {str(e)}")
            return (
                {"error": str(e)},
                self._get_status_html("error", f"错误: {str(e)}")
            )
    
    def generate_story_outline(self) -> Tuple[Dict, str]:
        """从结构化创意生成故事大纲"""
        try:
            if not self.structured_output:
                return (
                    {"error": "没有结构化创意可用。请先结构化创意。"},
                    self._get_status_html("error", "没有结构化创意可用")
                )
            
            story_outline = self.idea_structurer.generate_story_outline(self.structured_output)
            if story_outline:
                self.story_outline = story_outline
                outline_dict = story_outline.model_dump()
                
                status_html = self._get_status_html("complete", "故事大纲生成成功！")
                return outline_dict, status_html
            else:
                return (
                    {"error": "生成故事大纲失败"},
                    self._get_status_html("error", "生成故事大纲失败")
                )
                
        except Exception as e:
            logger.error(f"生成故事大纲时出错: {str(e)}")
            return (
                {"error": str(e)},
                self._get_status_html("error", f"错误: {str(e)}")
            )
    
    def generate_character_profiles(self) -> Tuple[Dict, str]:
        """从结构化创意生成角色档案"""
        try:
            if not self.structured_output:
                return (
                    {"error": "没有结构化创意可用。请先结构化创意。"},
                    self._get_status_html("error", "没有结构化创意可用")
                )
            
            if not self.structured_output.basic_characters:
                return (
                    {"error": "结构化创意中没有找到角色"},
                    self._get_status_html("error", "没有找到角色")
                )
            
            character_profiles = self.character_generator.generate_complete_character_profiles(
                self.structured_output.basic_characters,
                self.structured_output
            )
            
            if character_profiles:
                self.character_profiles = character_profiles
                profiles_dict = {
                    "character_count": len(character_profiles),
                    "characters": [profile.model_dump() for profile in character_profiles]
                }
                
                status_html = self._get_status_html("complete", f"生成了 {len(character_profiles)} 个角色档案！")
                return profiles_dict, status_html
            else:
                return (
                    {"error": "生成角色档案失败"},
                    self._get_status_html("error", "生成角色档案失败")
                )
                
        except Exception as e:
            logger.error(f"生成角色档案时出错: {str(e)}")
            return (
                {"error": str(e)},
                self._get_status_html("error", f"错误: {str(e)}")
            )

    def reset_session(self) -> Tuple:
        """重置整个会话"""
        self.chatbot_core.reset_conversation()
        self.structured_output = None
        self.story_outline = None
        self.character_profiles = []
        
        # 重置确认状态
        self.story_confirmed = False
        self.characters_confirmed = False
        self.story_feedback = ""
        self.characters_feedback = ""
        
        return (
            [],  # chatbot_display
            "",  # user_input
            self._get_status_html("incomplete", "会话已重置 - 准备开始"),  # status_display
            {"status": "会话已重置"},  # completeness_display
            [],  # conversation_display
            {"status": "尚未生成结构化创意"},  # user_idea_display
            {"status": "尚未生成故事大纲"},  # story_outline_display
            {"status": "尚未生成角色档案"}  # character_profiles_display
        )
    
    def launch(self, **kwargs) -> None:
        """启动界面"""
        interface = self.create_interface()
        
        # 默认启动参数
        launch_params = {
            "share": True,
            "debug": True,
            "show_error": True,
            "inbrowser": False
        }
        
        # 用用户参数覆盖
        launch_params.update(kwargs)
        
        logger.info("启动确认界面...")
        interface.launch(**launch_params)


def create_confirmation_interface() -> ConfirmationGradioInterface:
    """创建确认界面的工厂函数"""
    return ConfirmationGradioInterface()


def launch_confirmation_interface(**kwargs) -> None:
    """启动确认界面的便捷函数"""
    interface = create_confirmation_interface()
    interface.launch(**kwargs)


if __name__ == "__main__":
    # 直接运行时启动界面
    launch_confirmation_interface()