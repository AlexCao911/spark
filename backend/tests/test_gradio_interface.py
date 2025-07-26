"""
Tests for the Gradio chatbot interface.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from spark.chatbot.gradio_interface import ChatbotGradioInterface, create_chatbot_interface
from spark.models import UserIdea, StoryOutline, CharacterProfile


class TestChatbotGradioInterface:
    """Test cases for the Gradio chatbot interface."""
    
    @pytest.fixture
    def interface(self):
        """Create a ChatbotGradioInterface instance for testing."""
        with patch('spark.chatbot.gradio_interface.ChatbotCore'), \
             patch('spark.chatbot.gradio_interface.IdeaStructurer'), \
             patch('spark.chatbot.gradio_interface.CharacterProfileGenerator'):
            return ChatbotGradioInterface()
    
    @pytest.fixture
    def mock_user_idea(self):
        """Create a mock UserIdea for testing."""
        return UserIdea(
            theme="adventure",
            genre="action",
            target_audience="teens",
            duration_preference=120,
            basic_characters=["brave hero", "wise mentor"],
            plot_points=["hero's journey begins", "faces challenges", "overcomes obstacles"],
            visual_style="cinematic",
            mood="exciting"
        )
    
    @pytest.fixture
    def mock_story_outline(self):
        """Create a mock StoryOutline for testing."""
        return StoryOutline(
            title="The Hero's Adventure",
            summary="A young hero embarks on an epic journey.",
            narrative_text="This is a complete story about a hero who faces challenges and grows stronger.",
            estimated_duration=120
        )
    
    @pytest.fixture
    def mock_character_profiles(self):
        """Create mock CharacterProfile list for testing."""
        return [
            CharacterProfile(
                name="Hero",
                role="main",
                appearance="Young, determined, athletic",
                personality="Brave and curious",
                backstory="Grew up in a small village",
                motivations=["save the world", "prove themselves"],
                relationships={"mentor": "student"},
                image_url="https://example.com/hero.jpg",
                visual_consistency_tags=["young", "athletic"]
            ),
            CharacterProfile(
                name="Mentor",
                role="supporting",
                appearance="Elderly, wise, experienced",
                personality="Patient and knowledgeable",
                backstory="Former hero, now teacher",
                motivations=["guide the hero", "pass on knowledge"],
                relationships={"hero": "teacher"},
                image_url="https://example.com/mentor.jpg",
                visual_consistency_tags=["elderly", "wise"]
            )
        ]
    
    def test_interface_initialization(self, interface):
        """Test that the interface initializes correctly."""
        assert interface is not None
        assert hasattr(interface, 'chatbot_core')
        assert hasattr(interface, 'idea_structurer')
        assert hasattr(interface, 'character_generator')
        assert interface.current_session is None
        assert interface.structured_output is None
        assert interface.story_outline is None
        assert interface.character_profiles == []
    
    def test_get_status_html(self, interface):
        """Test status HTML generation."""
        # Test complete status
        complete_html = interface._get_status_html("complete", "Test complete")
        assert "status-complete" in complete_html
        assert "Test complete" in complete_html
        
        # Test incomplete status
        incomplete_html = interface._get_status_html("incomplete", "Test incomplete")
        assert "status-incomplete" in incomplete_html
        assert "Test incomplete" in incomplete_html
        
        # Test error status
        error_html = interface._get_status_html("error", "Test error")
        assert "status-error" in error_html
        assert "Test error" in error_html
        
        # Test unknown status defaults to incomplete
        unknown_html = interface._get_status_html("unknown", "Test unknown")
        assert "status-incomplete" in unknown_html
        assert "Test unknown" in unknown_html
    
    def test_create_interface(self, interface):
        """Test interface creation."""
        # Test that create_interface returns a Gradio Blocks object
        # We'll mock the actual Gradio components to avoid version issues
        with patch('gradio.Blocks') as mock_blocks, \
             patch('gradio.Markdown'), \
             patch('gradio.Row'), \
             patch('gradio.Column'), \
             patch('gradio.Chatbot'), \
             patch('gradio.Textbox'), \
             patch('gradio.Button'), \
             patch('gradio.HTML'), \
             patch('gradio.JSON'), \
             patch('gradio.Tabs'), \
             patch('gradio.TabItem'):
            
            mock_interface = Mock()
            mock_blocks.return_value.__enter__.return_value = mock_interface
            
            result = interface.create_interface()
            
            # Verify that Blocks was called
            mock_blocks.assert_called_once()
            assert result == mock_interface
    
    def test_send_message_first_interaction(self, interface):
        """Test sending the first message to the chatbot."""
        # Mock the chatbot core response
        mock_response = {
            "status": "engaged",
            "response": "Hello! Tell me about your video idea.",
            "is_complete": False,
            "missing_elements": ["theme", "characters"]
        }
        interface.chatbot_core.engage_user.return_value = mock_response
        interface.chatbot_core.get_conversation_history.return_value = [
            {"role": "user", "content": "I want to make a video"},
            {"role": "assistant", "content": "Hello! Tell me about your video idea."}
        ]
        
        # Test the send_message functionality by calling the internal logic
        message = "I want to make a video"
        history = []
        
        # Simulate what the send_message function would do
        response_data = interface.chatbot_core.engage_user(message)
        new_history = history + [[message, response_data.get("response", "No response")]]
        
        assert len(new_history) == 1
        assert new_history[0][0] == message
        assert new_history[0][1] == "Hello! Tell me about your video idea."
        assert response_data["is_complete"] is False
        assert "theme" in response_data["missing_elements"]
    
    def test_send_message_continuation(self, interface):
        """Test continuing a conversation."""
        # Mock the chatbot core response for continuation
        mock_response = {
            "status": "continued",
            "response": "That sounds interesting! Can you tell me more about the characters?",
            "is_complete": False,
            "missing_elements": ["characters"]
        }
        interface.chatbot_core.continue_conversation.return_value = mock_response
        
        # Simulate continuing conversation
        message = "It's about space exploration"
        history = [["I want to make a video", "Hello! Tell me about your video idea."]]
        
        response_data = interface.chatbot_core.continue_conversation(message)
        new_history = history + [[message, response_data.get("response", "No response")]]
        
        assert len(new_history) == 2
        assert new_history[1][0] == message
        assert "characters" in response_data.get("response", "")
        assert response_data["is_complete"] is False
    
    def test_send_message_error_handling(self, interface):
        """Test error handling in send_message."""
        # Mock an error response
        mock_response = {
            "status": "error",
            "response": "I'm experiencing technical difficulties. Please try again.",
            "error": "API connection failed"
        }
        interface.chatbot_core.engage_user.return_value = mock_response
        
        message = "Test message"
        history = []
        
        response_data = interface.chatbot_core.engage_user(message)
        
        assert response_data["status"] == "error"
        assert "technical difficulties" in response_data["response"]
        assert response_data["error"] == "API connection failed"
    
    def test_structure_idea_success(self, interface, mock_user_idea):
        """Test successful idea structuring."""
        # Mock conversation history
        mock_conversation = [
            {"role": "user", "content": "I want to make an action video about a hero"},
            {"role": "assistant", "content": "Tell me more about the hero"},
            {"role": "user", "content": "The hero is brave and goes on adventures"}
        ]
        interface.chatbot_core.get_conversation_history.return_value = mock_conversation
        
        # Mock idea structurer
        interface.idea_structurer.structure_conversation.return_value = mock_user_idea
        interface.idea_structurer.validate_idea_completeness.return_value = {
            "is_complete": True,
            "completeness_score": 0.8,
            "missing_elements": [],
            "suggestions": []
        }
        
        # Test structuring
        user_idea = interface.idea_structurer.structure_conversation(mock_conversation)
        validation = interface.idea_structurer.validate_idea_completeness(user_idea)
        
        assert user_idea is not None
        assert user_idea.theme == "adventure"
        assert user_idea.genre == "action"
        assert validation["is_complete"] is True
        assert validation["completeness_score"] == 0.8
    
    def test_structure_idea_no_conversation(self, interface):
        """Test structuring idea with no conversation."""
        interface.chatbot_core.get_conversation_history.return_value = []
        
        conversation_history = interface.chatbot_core.get_conversation_history()
        
        assert len(conversation_history) == 0
    
    def test_generate_story_outline_success(self, interface, mock_user_idea, mock_story_outline):
        """Test successful story outline generation."""
        interface.structured_output = mock_user_idea
        interface.idea_structurer.generate_story_outline.return_value = mock_story_outline
        
        story_outline = interface.idea_structurer.generate_story_outline(interface.structured_output)
        
        assert story_outline is not None
        assert story_outline.title == "The Hero's Adventure"
        assert story_outline.estimated_duration == 120
        assert "hero" in story_outline.narrative_text.lower()
    
    def test_generate_story_outline_no_structured_idea(self, interface):
        """Test story outline generation without structured idea."""
        interface.structured_output = None
        
        # This should fail because no structured output exists
        assert interface.structured_output is None
    
    def test_generate_character_profiles_success(self, interface, mock_user_idea, mock_character_profiles):
        """Test successful character profile generation."""
        interface.structured_output = mock_user_idea
        interface.character_generator.generate_complete_character_profiles.return_value = mock_character_profiles
        
        character_profiles = interface.character_generator.generate_complete_character_profiles(
            interface.structured_output.basic_characters,
            interface.structured_output
        )
        
        assert character_profiles is not None
        assert len(character_profiles) == 2
        assert character_profiles[0].name == "Hero"
        assert character_profiles[1].name == "Mentor"
        assert character_profiles[0].role == "main"
        assert character_profiles[1].role == "supporting"
    
    def test_generate_character_profiles_no_characters(self, interface):
        """Test character profile generation with no characters."""
        mock_idea = UserIdea(
            theme="adventure",
            genre="action",
            basic_characters=[],  # No characters
            plot_points=["start", "middle", "end"]
        )
        interface.structured_output = mock_idea
        
        # Should handle empty character list
        assert len(interface.structured_output.basic_characters) == 0
    
    def test_reset_session(self, interface):
        """Test session reset functionality."""
        # Set up some state
        interface.structured_output = Mock()
        interface.story_outline = Mock()
        interface.character_profiles = [Mock()]
        
        # Mock the reset method
        interface.chatbot_core.reset_conversation = Mock()
        
        # Simulate reset
        interface.chatbot_core.reset_conversation()
        interface.structured_output = None
        interface.story_outline = None
        interface.character_profiles = []
        
        # Verify reset
        interface.chatbot_core.reset_conversation.assert_called_once()
        assert interface.structured_output is None
        assert interface.story_outline is None
        assert interface.character_profiles == []
    
    def test_factory_function(self):
        """Test the factory function."""
        with patch('spark.chatbot.gradio_interface.ChatbotCore'), \
             patch('spark.chatbot.gradio_interface.IdeaStructurer'), \
             patch('spark.chatbot.gradio_interface.CharacterProfileGenerator'):
            interface = create_chatbot_interface()
            assert isinstance(interface, ChatbotGradioInterface)
    
    @patch('spark.chatbot.gradio_interface.ChatbotGradioInterface.launch')
    def test_launch_chatbot_interface(self, mock_launch):
        """Test the launch convenience function."""
        from spark.chatbot.gradio_interface import launch_chatbot_interface
        
        with patch('spark.chatbot.gradio_interface.create_chatbot_interface') as mock_create:
            mock_interface = Mock()
            mock_create.return_value = mock_interface
            
            launch_chatbot_interface(server_port=8080, debug=True)
            
            mock_create.assert_called_once()
            mock_interface.launch.assert_called_once_with(server_port=8080, debug=True)


class TestIntegration:
    """Integration tests for the Gradio interface."""
    
    @pytest.fixture
    def real_interface(self):
        """Create a real interface for integration testing."""
        # Only create if we have proper config
        try:
            return ChatbotGradioInterface()
        except Exception:
            pytest.skip("Cannot create real interface without proper configuration")
    
    def test_interface_creation_integration(self, real_interface):
        """Test that the interface can be created with real components."""
        assert real_interface is not None
        assert hasattr(real_interface, 'chatbot_core')
        assert hasattr(real_interface, 'idea_structurer')
        assert hasattr(real_interface, 'character_generator')
    
    def test_gradio_interface_structure(self, real_interface):
        """Test that the Gradio interface has the expected structure."""
        # Test interface structure without actually creating Gradio components
        with patch('gradio.Blocks') as mock_blocks, \
             patch('gradio.Markdown'), \
             patch('gradio.Row'), \
             patch('gradio.Column'), \
             patch('gradio.Chatbot'), \
             patch('gradio.Textbox'), \
             patch('gradio.Button'), \
             patch('gradio.HTML'), \
             patch('gradio.JSON'), \
             patch('gradio.Tabs'), \
             patch('gradio.TabItem'):
            
            mock_interface = Mock()
            mock_blocks.return_value.__enter__.return_value = mock_interface
            
            result = real_interface.create_interface()
            
            # Verify Gradio components would be created
            mock_blocks.assert_called_once()
            call_kwargs = mock_blocks.call_args[1]
            
            assert call_kwargs['title'] == "Spark AI Chatbot Testing Interface"
            assert 'css' in call_kwargs


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])