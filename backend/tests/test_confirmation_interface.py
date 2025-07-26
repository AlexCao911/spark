"""
确认界面的测试
"""

import pytest
from unittest.mock import Mock, patch
from src.spark.chatbot.confirmation_interface import ConfirmationGradioInterface
from src.spark.models import UserIdea, StoryOutline, CharacterProfile


class TestConfirmationGradioInterface:
    """测试确认Gradio界面"""
    
    def setup_method(self):
        """设置测试环境"""
        self.interface = ConfirmationGradioInterface()
        
        # 创建测试数据
        self.user_idea = UserIdea(
            theme="冒险",
            genre="奇幻",
            target_audience="青少年",
            duration_preference=120,
            basic_characters=["英雄", "导师"],
            plot_points=["开始旅程", "面临挑战", "获得胜利"],
            visual_style="电影风格",
            mood="史诗"
        )
        
        self.story_outline = StoryOutline(
            title="魔法冒险",
            summary="一个年轻英雄的成长故事",
            narrative_text="从前，有一个年轻的英雄踏上了拯救王国的旅程...",
            estimated_duration=120
        )
        
        self.character_profiles = [
            CharacterProfile(
                name="英雄",
                role="主角",
                appearance="年轻勇敢的战士",
                personality="勇敢坚定",
                backstory="在小村庄长大",
                motivations=["拯救王国"],
                relationships={},
                image_url="http://example.com/hero.jpg",
                visual_consistency_tags=["年轻", "战士"]
            )
        ]
    
    def test_interface_initialization(self):
        """测试界面初始化"""
        assert self.interface.confirmation_manager is not None
        assert hasattr(self.interface, 'chatbot_core')
        assert hasattr(self.interface, 'idea_structurer')
        assert hasattr(self.interface, 'character_generator')
    
    def test_send_message_base_success(self):
        """测试基础发送消息功能"""
        # Mock chatbot core response
        with patch.object(self.interface.chatbot_core, 'engage_user') as mock_engage:
            mock_engage.return_value = {
                "status": "engaged",
                "response": "测试响应",
                "is_complete": False,
                "missing_elements": ["theme"]
            }
            
            with patch.object(self.interface.chatbot_core, 'get_conversation_history') as mock_history:
                mock_history.return_value = []
                
                result = self.interface.send_message_base("测试消息", [])
                
                assert len(result) == 5
                assert len(result[0]) == 2  # 新的历史记录应该有2条消息
                assert result[1] == ""  # 输入应该被清空
                assert "正在收集信息" in result[2]  # 状态HTML
                assert isinstance(result[3], dict)  # 完整性数据
                assert isinstance(result[4], list)  # 对话数据
    
    def test_send_message_base_error(self):
        """测试发送消息时的错误处理"""
        with patch.object(self.interface.chatbot_core, 'engage_user') as mock_engage:
            mock_engage.return_value = {
                "status": "error",
                "error": "测试错误"
            }
            
            result = self.interface.send_message_base("测试消息", [])
            
            assert "错误" in result[2]  # 状态HTML应该包含错误信息
    
    def test_clear_chat(self):
        """测试清空聊天功能"""
        result = self.interface.clear_chat()
        
        assert len(result) == 5
        assert result[0] == []  # 聊天历史应该为空
        assert result[1] == ""  # 输入应该为空
        assert "聊天已清空" in result[2]  # 状态消息
    
    def test_reset_session(self):
        """测试重置会话功能"""
        # 设置一些状态
        self.interface.structured_output = self.user_idea
        self.interface.story_outline = self.story_outline
        self.interface.character_profiles = self.character_profiles
        
        with patch.object(self.interface.chatbot_core, 'reset_conversation'):
            result = self.interface.reset_session()
            
            assert len(result) == 8
            assert result[0] == []  # 聊天显示应该为空
            assert result[1] == ""  # 用户输入应该为空
            assert "会话已重置" in result[2]  # 状态消息
            
            # 验证状态已重置
            assert self.interface.structured_output is None
            assert self.interface.story_outline is None
            assert self.interface.character_profiles == []
    
    def test_get_status_html(self):
        """测试状态HTML生成"""
        # 测试完成状态
        complete_html = self.interface._get_status_html("complete", "测试完成")
        assert "status-complete" in complete_html
        assert "测试完成" in complete_html
        
        # 测试未完成状态
        incomplete_html = self.interface._get_status_html("incomplete", "测试未完成")
        assert "status-incomplete" in incomplete_html
        assert "测试未完成" in incomplete_html
        
        # 测试错误状态
        error_html = self.interface._get_status_html("error", "测试错误")
        assert "status-error" in error_html
        assert "测试错误" in error_html
    
    def test_create_interface_structure(self):
        """测试界面结构创建"""
        # 这个测试主要验证create_interface方法不会抛出异常
        try:
            interface = self.interface.create_interface()
            assert interface is not None
        except Exception as e:
            pytest.fail(f"创建界面时出现异常: {str(e)}")
    
    @patch('src.spark.chatbot.confirmation_interface.confirmation_manager')
    def test_confirmation_manager_integration(self, mock_manager):
        """测试与确认管理器的集成"""
        # 设置mock返回值
        mock_manager.save_approved_content.return_value = {
            "status": "success",
            "project_id": "test_id",
            "project_name": "测试项目"
        }
        
        mock_manager.list_projects.return_value = [
            {
                "project_id": "test_id",
                "project_name": "测试项目",
                "created_at": "2024-01-01T00:00:00",
                "status": "approved",
                "character_count": 1
            }
        ]
        
        # 验证管理器被正确设置
        assert self.interface.confirmation_manager == mock_manager
    
    def test_interface_inheritance(self):
        """测试界面继承关系"""
        # 验证继承自ChatbotGradioInterfaceFixed
        from src.spark.chatbot.gradio_interface_fixed import ChatbotGradioInterfaceFixed
        assert isinstance(self.interface, ChatbotGradioInterfaceFixed)
        
        # 验证继承的方法存在
        assert hasattr(self.interface, 'chatbot_core')
        assert hasattr(self.interface, 'idea_structurer')
        assert hasattr(self.interface, 'character_generator')


def test_factory_functions():
    """测试工厂函数"""
    from src.spark.chatbot.confirmation_interface import (
        create_confirmation_interface,
        launch_confirmation_interface
    )
    
    # 测试创建函数
    interface = create_confirmation_interface()
    assert isinstance(interface, ConfirmationGradioInterface)
    
    # 测试启动函数存在（不实际启动）
    assert callable(launch_confirmation_interface)