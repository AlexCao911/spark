"""
Unit tests for ChatbotCore class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.spark.chatbot.core import ChatbotCore, ConversationManager
from src.spark.models import UserIdea


class TestConversationManager:
    """Test cases for ConversationManager."""
    
    def test_init(self):
        """Test ConversationManager initialization."""
        manager = ConversationManager()
        assert manager.messages == []
        assert manager.context == {}
        assert manager.session_id is None
    
    def test_add_message(self):
        """Test adding messages to conversation."""
        manager = ConversationManager()
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        
        assert len(manager.messages) == 2
        assert manager.messages[0] == {"role": "user", "content": "Hello"}
        assert manager.messages[1] == {"role": "assistant", "content": "Hi there!"}
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary."""
        manager = ConversationManager()
        
        # Test empty conversation
        summary = manager.get_conversation_summary()
        assert summary == "No conversation history."
        
        # Test with messages
        manager.add_message("user", "I want to create a video about space adventure")
        manager.add_message("assistant", "That sounds exciting! Tell me more about the characters.")
        
        summary = manager.get_conversation_summary()
        assert "user:" in summary.lower()
        assert "assistant:" in summary.lower()
        assert "space adventure" in summary
    
    def test_context_management(self):
        """Test context update and retrieval."""
        manager = ConversationManager()
        
        manager.update_context("theme", "adventure")
        manager.update_context("genre", "sci-fi")
        
        assert manager.get_context("theme") == "adventure"
        assert manager.get_context("genre") == "sci-fi"
        assert manager.get_context("nonexistent", "default") == "default"


class TestChatbotCore:
    """Test cases for ChatbotCore."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('src.spark.chatbot.core.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock response structure
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response from GPT-4o"
            mock_client.chat.completions.create.return_value = mock_response
            
            yield mock_client
    
    @pytest.fixture
    def chatbot(self, mock_openai_client):
        """Create ChatbotCore instance with mocked client."""
        with patch('src.spark.config.config') as mock_config:
            mock_config.CHATBOT_API_KEY = "test-key"
            mock_config.CHATBOT_API_ENDPOINT = "https://api.openai.com/v1"
            mock_config.CHATBOT_MODEL = "gpt-4o"
            
            return ChatbotCore()
    
    def test_init(self, chatbot, mock_openai_client):
        """Test ChatbotCore initialization."""
        assert chatbot.client == mock_openai_client
        assert isinstance(chatbot.conversation_manager, ConversationManager)
        assert chatbot.system_prompt is not None
        assert len(chatbot.system_prompt) > 0
    
    def test_system_prompt_content(self, chatbot):
        """Test that system prompt contains required elements."""
        prompt = chatbot.system_prompt
        
        # Check for key instruction elements
        assert "creative ai assistant" in prompt.lower()
        assert "video ideas" in prompt.lower()
        assert "theme" in prompt.lower()
        assert "characters" in prompt.lower()
        assert "plot" in prompt.lower()
    
    def test_engage_user_success(self, chatbot, mock_openai_client):
        """Test successful user engagement."""
        initial_input = "I want to create a video about a space adventure"
        
        result = chatbot.engage_user(initial_input)
        
        assert result["status"] == "engaged"
        assert "response" in result
        assert "is_complete" in result
        assert "missing_elements" in result
        assert "conversation_id" in result
        
        # Verify OpenAI API was called
        mock_openai_client.chat.completions.create.assert_called_once()
        
        # Verify conversation history
        messages = chatbot.conversation_manager.messages
        assert len(messages) >= 2  # system + user + assistant
        assert any(msg["role"] == "user" and initial_input in msg["content"] for msg in messages)
    
    def test_engage_user_api_error(self, chatbot, mock_openai_client):
        """Test user engagement with API error."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = chatbot.engage_user("Test input")
        
        assert result["status"] == "error"
        assert "error" in result
        assert "trouble processing" in result["response"].lower()
    
    def test_continue_conversation_success(self, chatbot, mock_openai_client):
        """Test continuing conversation successfully."""
        # First engage user
        chatbot.engage_user("I want to create a video")
        
        # Then continue conversation
        result = chatbot.continue_conversation("It's about space exploration")
        
        assert result["status"] == "continued"
        assert "response" in result
        assert "is_complete" in result
        
        # Verify multiple API calls
        assert mock_openai_client.chat.completions.create.call_count == 2
    
    def test_analyze_idea_completeness(self, chatbot):
        """Test idea completeness analysis."""
        # Add some conversation messages
        chatbot.conversation_manager.add_message("user", "I want to create a sci-fi video about a space explorer who discovers aliens")
        chatbot.conversation_manager.add_message("user", "The main character is brave and curious, and the story has action and drama")
        
        completeness = chatbot._analyze_idea_completeness()
        
        assert "is_complete" in completeness
        assert "found_elements" in completeness
        assert "missing_elements" in completeness
        assert isinstance(completeness["found_elements"], list)
        assert isinstance(completeness["missing_elements"], list)
        
        # Should find theme, genre, characters in the conversation
        found = completeness["found_elements"]
        assert "theme" in found or "genre" in found or "characters" in found
    
    def test_ask_clarifying_questions_success(self, chatbot, mock_openai_client):
        """Test generating clarifying questions."""
        current_idea = {
            "found_elements": ["theme", "genre"],
            "missing_elements": ["characters", "plot"]
        }
        
        question = chatbot.ask_clarifying_questions(current_idea)
        
        assert isinstance(question, str)
        assert len(question) > 0
        mock_openai_client.chat.completions.create.assert_called()
    
    def test_ask_clarifying_questions_fallback(self, chatbot, mock_openai_client):
        """Test fallback clarifying questions when API fails."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        current_idea = {"missing_elements": ["theme"]}
        question = chatbot.ask_clarifying_questions(current_idea)
        
        assert isinstance(question, str)
        assert len(question) > 0
        assert "theme" in question.lower() or "concept" in question.lower()
    
    def test_conversation_management(self, chatbot):
        """Test conversation history and context management."""
        # Test getting empty history
        history = chatbot.get_conversation_history()
        assert isinstance(history, list)
        
        # Add some conversation
        chatbot.engage_user("Test input")
        
        # Test getting history with content
        history = chatbot.get_conversation_history()
        assert len(history) > 0
        
        # Test getting context
        context = chatbot.get_conversation_context()
        assert "message_count" in context
        assert "context" in context
        assert "last_analysis" in context
        
        # Test reset
        chatbot.reset_conversation()
        new_history = chatbot.get_conversation_history()
        assert len(new_history) == 0
    
    def test_keyword_analysis_accuracy(self, chatbot):
        """Test accuracy of keyword-based analysis."""
        test_cases = [
            {
                "input": "I want to create a comedy video about two friends who go on a road trip",
                "expected_found": ["theme", "genre", "characters", "plot"]
            },
            {
                "input": "A horror story",
                "expected_found": ["genre"]
            },
            {
                "input": "The main character is a detective who solves mysteries in a futuristic city",
                "expected_found": ["characters", "genre", "theme"]
            }
        ]
        
        for case in test_cases:
            chatbot.reset_conversation()
            chatbot.conversation_manager.add_message("user", case["input"])
            
            analysis = chatbot._analyze_idea_completeness()
            found = analysis["found_elements"]
            
            # Check that at least some expected elements are found
            overlap = set(found) & set(case["expected_found"])
            assert len(overlap) > 0, f"No expected elements found in: {case['input']}"


if __name__ == "__main__":
    pytest.main([__file__])