"""
Tests for main pipeline functionality.
"""

import pytest
from unittest.mock import Mock, patch
from spark.main import VideoGenerationPipeline
from spark.models import VideoGenerationState, UserIdea, ApprovedContent, StoryOutline


def test_video_generation_pipeline_creation():
    """Test VideoGenerationPipeline creation."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        pipeline = VideoGenerationPipeline()
        
        assert pipeline is not None
        assert hasattr(pipeline, 'script_crew')
        assert hasattr(pipeline, 'video_crew')
        mock_config.ensure_temp_directory.assert_called_once()


def test_video_generation_pipeline_with_missing_keys():
    """Test VideoGenerationPipeline creation with missing API keys."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = ['chatbot', 'video_generation']
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            
            assert pipeline is not None
            mock_print.assert_called_with("Warning: Missing API keys for: chatbot, video_generation")


def test_pipeline_state_initialization():
    """Test that pipeline initializes with proper state."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        pipeline = VideoGenerationPipeline()
        
        # Check that state is properly initialized
        assert isinstance(pipeline.state, VideoGenerationState)
        assert isinstance(pipeline.state.user_idea, UserIdea)
        assert isinstance(pipeline.state.approved_content, ApprovedContent)


def test_initialize_pipeline_method():
    """Test initialize_pipeline method."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = ['chatbot']
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            pipeline.initialize_pipeline()
            
            # Should print initialization messages
            assert mock_print.call_count >= 2
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Initializing Spark AI Video Generation Pipeline" in call for call in calls)


def test_pipeline_with_existing_theme():
    """Test pipeline initialization with existing theme."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            pipeline.state.user_idea.theme = "Adventure"
            pipeline.initialize_pipeline()
            
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Resuming pipeline for theme: Adventure" in call for call in calls)


def test_expand_story_narrative_without_confirmation():
    """Test expand_story_narrative when user hasn't confirmed."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            pipeline.state.approved_content.user_confirmed = False
            
            pipeline.expand_story_narrative()
            
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Waiting for user confirmation" in call for call in calls)


def test_expand_story_narrative_with_confirmation():
    """Test expand_story_narrative when user has confirmed."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        pipeline = VideoGenerationPipeline()
        pipeline.state.approved_content.user_confirmed = True
        pipeline.state.approved_content.story_outline = StoryOutline(
            title="Test Story",
            summary="Test summary",
            narrative_text="Test narrative",
            estimated_duration=60
        )
        
        # Mock the script crew method
        mock_detailed_story = Mock()
        mock_detailed_story.full_story_text = "Detailed story text"
        pipeline.script_crew.expand_story_narrative = Mock(return_value=mock_detailed_story)
        
        with patch('builtins.print') as mock_print:
            pipeline.expand_story_narrative()
            
            pipeline.script_crew.expand_story_narrative.assert_called_once()
            assert pipeline.state.detailed_story == mock_detailed_story
            
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Expanding story narrative" in call for call in calls)


def test_generate_video_prompts_without_story():
    """Test generate_video_prompts without detailed story."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            pipeline.state.detailed_story.full_story_text = ""
            
            pipeline.generate_video_prompts()
            
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("No detailed story available" in call for call in calls)


def test_generate_video_clips_without_prompts():
    """Test generate_video_clips without video prompts."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            pipeline.state.video_prompts = []
            
            pipeline.generate_video_clips()
            
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("No video prompts available" in call for call in calls)


def test_assemble_final_video_without_clips():
    """Test assemble_final_video without video clips."""
    with patch('spark.main.config') as mock_config:
        mock_config.ensure_temp_directory.return_value = None
        mock_config.get_missing_api_keys.return_value = []
        
        with patch('builtins.print') as mock_print:
            pipeline = VideoGenerationPipeline()
            pipeline.state.video_clip_urls = []
            
            pipeline.assemble_final_video()
            
            calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("No video clips available" in call for call in calls)


if __name__ == "__main__":
    pytest.main([__file__])