"""
Unit tests for IdeaStructurer class.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.spark.chatbot.idea_structurer import IdeaStructurer, PromptTemplates
from src.spark.models import UserIdea, StoryOutline


class TestPromptTemplates:
    """Test cases for PromptTemplates."""
    
    def test_idea_extraction_prompt_format(self):
        """Test that idea extraction prompt formats correctly."""
        templates = PromptTemplates()
        conversation_text = "I want to create a sci-fi video about space exploration"
        
        prompt = templates.IDEA_EXTRACTION_PROMPT.format(
            conversation_text=conversation_text
        )
        
        assert conversation_text in prompt
        assert "JSON" in prompt
        assert "theme" in prompt
        assert "genre" in prompt
        assert "characters" in prompt
    
    def test_story_outline_prompt_format(self):
        """Test that story outline prompt formats correctly."""
        templates = PromptTemplates()
        
        prompt = templates.STORY_OUTLINE_PROMPT.format(
            theme="adventure",
            genre="action",
            characters="hero, villain",
            plot_points="start, conflict, resolution",
            visual_style="cinematic",
            mood="exciting",
            target_audience="teens",
            duration_preference=120
        )
        
        assert "adventure" in prompt
        assert "action" in prompt
        assert "hero" in prompt
        assert "120" in prompt
    
    def test_validation_prompt_format(self):
        """Test that validation prompt formats correctly."""
        templates = PromptTemplates()
        idea_json = '{"theme": "test", "genre": "comedy"}'
        
        prompt = templates.VALIDATION_PROMPT.format(idea_json=idea_json)
        
        assert idea_json in prompt
        assert "missing_elements" in prompt
        assert "is_complete" in prompt


class TestIdeaStructurer:
    """Test cases for IdeaStructurer."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('src.spark.chatbot.idea_structurer.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def structurer(self, mock_openai_client):
        """Create IdeaStructurer instance with mocked client."""
        with patch('src.spark.config.config') as mock_config:
            mock_config.CHATBOT_API_KEY = "test-key"
            mock_config.CHATBOT_API_ENDPOINT = "https://api.openai.com/v1"
            mock_config.CHATBOT_MODEL = "gpt-4o"
            
            return IdeaStructurer()
    
    @pytest.fixture
    def sample_conversation(self):
        """Sample conversation history for testing."""
        return [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "I want to create a video about a space adventure"},
            {"role": "assistant", "content": "That sounds exciting! Tell me more about the characters."},
            {"role": "user", "content": "The main character is a brave astronaut who discovers alien life"},
            {"role": "assistant", "content": "Great! What happens in the story?"},
            {"role": "user", "content": "The astronaut must protect Earth from an alien invasion"}
        ]
    
    @pytest.fixture
    def sample_user_idea(self):
        """Sample UserIdea for testing."""
        return UserIdea(
            theme="space exploration",
            genre="sci-fi",
            target_audience="adults",
            duration_preference=120,
            basic_characters=["brave astronaut", "alien leader"],
            plot_points=["discovery", "first contact", "conflict", "resolution"],
            visual_style="cinematic",
            mood="thrilling"
        )
    
    def test_init(self, structurer, mock_openai_client):
        """Test IdeaStructurer initialization."""
        assert structurer.client == mock_openai_client
        assert isinstance(structurer.templates, PromptTemplates)
    
    def test_extract_conversation_text(self, structurer, sample_conversation):
        """Test extracting user messages from conversation."""
        text = structurer._extract_conversation_text(sample_conversation)
        
        assert "space adventure" in text
        assert "brave astronaut" in text
        assert "alien invasion" in text
        # Should not contain assistant messages
        assert "That sounds exciting" not in text
    
    def test_parse_json_response_valid_json(self, structurer):
        """Test parsing valid JSON response."""
        json_response = '{"theme": "adventure", "genre": "action"}'
        result = structurer._parse_json_response(json_response)
        
        assert result is not None
        assert result["theme"] == "adventure"
        assert result["genre"] == "action"
    
    def test_parse_json_response_markdown_format(self, structurer):
        """Test parsing JSON from markdown code blocks."""
        markdown_response = '''Here's the JSON:
        ```json
        {"theme": "mystery", "genre": "thriller"}
        ```
        '''
        result = structurer._parse_json_response(markdown_response)
        
        assert result is not None
        assert result["theme"] == "mystery"
        assert result["genre"] == "thriller"
    
    def test_parse_json_response_embedded_json(self, structurer):
        """Test parsing JSON embedded in text."""
        text_response = 'The analysis shows {"theme": "comedy", "genre": "humor"} as the result.'
        result = structurer._parse_json_response(text_response)
        
        assert result is not None
        assert result["theme"] == "comedy"
        assert result["genre"] == "humor"
    
    def test_parse_json_response_invalid(self, structurer):
        """Test handling invalid JSON response."""
        invalid_response = "This is not JSON at all"
        result = structurer._parse_json_response(invalid_response)
        
        assert result is None
    
    def test_fallback_extraction(self, structurer):
        """Test fallback keyword extraction."""
        conversation_text = "I want a funny comedy about two friends going on a road trip adventure"
        
        result = structurer._fallback_extraction(conversation_text)
        
        assert isinstance(result, UserIdea)
        assert result.genre == "comedy"  # Should detect comedy
        assert result.theme in ["adventure", "romance", "mystery", "science fiction", "fantasy"]
        assert len(result.basic_characters) > 0
        assert len(result.plot_points) > 0
    
    def test_create_default_idea(self, structurer):
        """Test creating default UserIdea."""
        result = structurer._create_default_idea()
        
        assert isinstance(result, UserIdea)
        assert result.theme == "adventure"
        assert result.genre == "drama"
        assert result.target_audience == "general"
        assert result.duration_preference == 60
        assert len(result.basic_characters) > 0
        assert len(result.plot_points) > 0
    
    def test_structure_conversation_success(self, structurer, mock_openai_client, sample_conversation):
        """Test successful conversation structuring."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "theme": "space exploration",
            "genre": "sci-fi",
            "target_audience": "adults",
            "duration_preference": 120,
            "basic_characters": ["astronaut"],
            "plot_points": ["discovery", "conflict"],
            "visual_style": "cinematic",
            "mood": "thrilling"
        })
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = structurer.structure_conversation(sample_conversation)
        
        assert isinstance(result, UserIdea)
        assert result.theme == "space exploration"
        assert result.genre == "sci-fi"
        assert "astronaut" in result.basic_characters
        mock_openai_client.chat.completions.create.assert_called_once()
    
    def test_structure_conversation_api_error(self, structurer, mock_openai_client, sample_conversation):
        """Test conversation structuring with API error."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = structurer.structure_conversation(sample_conversation)
        
        # Should return fallback result
        assert isinstance(result, UserIdea)
        assert result is not None
    
    def test_structure_conversation_empty_input(self, structurer):
        """Test structuring with empty conversation."""
        empty_conversation = []
        
        result = structurer.structure_conversation(empty_conversation)
        
        assert isinstance(result, UserIdea)
        # Should return default idea
        assert result.theme == "adventure"
    
    def test_generate_story_outline_success(self, structurer, mock_openai_client, sample_user_idea):
        """Test successful story outline generation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "title": "Space Adventure",
            "summary": "An exciting space exploration story",
            "narrative_text": "A brave astronaut discovers alien life and must protect Earth...",
            "estimated_duration": 120
        })
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = structurer.generate_story_outline(sample_user_idea)
        
        assert isinstance(result, StoryOutline)
        assert result.title == "Space Adventure"
        assert result.estimated_duration == 120
        mock_openai_client.chat.completions.create.assert_called_once()
    
    def test_generate_story_outline_fallback(self, structurer, mock_openai_client, sample_user_idea):
        """Test story outline generation with API error."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = structurer.generate_story_outline(sample_user_idea)
        
        assert isinstance(result, StoryOutline)
        assert "Sci-Fi Story" in result.title
        assert sample_user_idea.theme in result.narrative_text
    
    def test_validate_idea_completeness_complete(self, structurer, sample_user_idea):
        """Test validation of complete idea."""
        result = structurer.validate_idea_completeness(sample_user_idea)
        
        assert result["is_complete"] is True
        assert result["completeness_score"] == 1.0
        assert len(result["missing_elements"]) == 0
        assert "details" in result
    
    def test_validate_idea_completeness_incomplete(self, structurer):
        """Test validation of incomplete idea."""
        incomplete_idea = UserIdea(
            theme="",  # Missing theme
            genre="action",
            target_audience="",  # Missing audience
            duration_preference=0,  # Invalid duration
            basic_characters=[],  # No characters
            plot_points=["one point"],  # Not enough plot points
            visual_style="cinematic",
            mood="exciting"
        )
        
        result = structurer.validate_idea_completeness(incomplete_idea)
        
        assert result["is_complete"] is False
        assert result["completeness_score"] < 1.0
        assert len(result["missing_elements"]) > 0
        assert "theme" in result["missing_elements"]
        assert len(result["suggestions"]) > 0
    
    def test_validate_with_ai_success(self, structurer, mock_openai_client, sample_user_idea):
        """Test AI-powered validation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_complete": True,
            "missing_elements": [],
            "suggestions": ["Great idea! Ready for production."]
        })
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = structurer.validate_with_ai(sample_user_idea)
        
        assert result["is_complete"] is True
        assert len(result["missing_elements"]) == 0
        mock_openai_client.chat.completions.create.assert_called_once()
    
    def test_validate_with_ai_fallback(self, structurer, mock_openai_client, sample_user_idea):
        """Test AI validation with API error fallback."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = structurer.validate_with_ai(sample_user_idea)
        
        # Should fallback to basic validation
        assert "is_complete" in result
        assert "missing_elements" in result
    
    def test_get_schema_template(self, structurer):
        """Test getting JSON schema template."""
        schema = structurer.get_schema_template()
        
        assert "theme" in schema
        assert "genre" in schema
        assert "basic_characters" in schema
        assert "plot_points" in schema
        assert isinstance(schema, dict)
    
    def test_keyword_extraction_accuracy(self, structurer):
        """Test accuracy of keyword-based extraction."""
        test_cases = [
            {
                "text": "I want to create a horror movie about zombies",
                "expected_genre": "horror"
            },
            {
                "text": "A romantic comedy about two people falling in love",
                "expected_genre": "comedy",
                "expected_theme": "romance"
            },
            {
                "text": "Space adventure with aliens and robots",
                "expected_genre": "sci-fi",
                "expected_theme": "science fiction"
            },
            {
                "text": "Mystery detective story with clues and investigation",
                "expected_theme": "mystery"
            }
        ]
        
        for case in test_cases:
            result = structurer._fallback_extraction(case["text"])
            
            if "expected_genre" in case:
                assert result.genre == case["expected_genre"], f"Failed for: {case['text']}"
            
            if "expected_theme" in case:
                assert case["expected_theme"] in result.theme.lower(), f"Failed for: {case['text']}"


if __name__ == "__main__":
    pytest.main([__file__])