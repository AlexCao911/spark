"""
Tests for configuration management.
"""

import os
import tempfile
import pytest
from spark.config import Config, RetryConfig, ModelManager


def test_retry_config_creation():
    """Test RetryConfig model creation and default values."""
    config = RetryConfig()
    
    assert config.max_retries == 3
    assert config.base_delay == 1.0
    assert config.max_delay == 60.0
    assert config.exponential_base == 2.0


def test_config_default_values():
    """Test Config model with default values."""
    config = Config()
    
    assert config.CHATBOT_MODEL == "gpt-4o"
    assert config.IMAGE_GEN_MODEL == "dall-e-3"
    assert config.DETAILED_STORY_MODEL == "qwen3-turbo"
    assert config.VIDEO_GENERATE_MODEL == "veo3-standard"
    assert config.MAX_VIDEO_DURATION == 300
    assert config.MAX_CONCURRENT_GENERATIONS == 3


def test_config_retry_config_property():
    """Test that Config returns proper RetryConfig object."""
    config = Config()
    retry_config = config.retry_config
    
    assert isinstance(retry_config, RetryConfig)
    assert retry_config.max_retries == config.API_MAX_RETRIES
    assert retry_config.base_delay == config.API_BASE_DELAY


def test_config_api_key_validation():
    """Test API key validation functionality."""
    config = Config()
    
    # Test with no API keys
    validation = config.validate_api_keys()
    assert all(not valid for valid in validation.values())
    
    missing_keys = config.get_missing_api_keys()
    assert len(missing_keys) == 4
    assert "chatbot" in missing_keys


def test_config_with_environment_variables():
    """Test Config loading from environment variables."""
    # Set test environment variables
    test_env = {
        "CHATBOT_API_KEY": "test_chatbot_key",
        "IMAGE_GEN_API_KEY": "test_image_key",
        "MAX_VIDEO_DURATION": "600",
        "DEBUG_MODE": "true"
    }
    
    # Temporarily set environment variables
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        config = Config()
        
        assert config.CHATBOT_API_KEY == "test_chatbot_key"
        assert config.IMAGE_GEN_API_KEY == "test_image_key"
        assert config.MAX_VIDEO_DURATION == 600
        assert config.DEBUG_MODE is True
        
        # Test validation with some keys present
        validation = config.validate_api_keys()
        assert validation["chatbot"] is True
        assert validation["image_generation"] is True
        assert validation["detailed_story"] is False
        assert validation["video_generation"] is False
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def test_config_temp_directory_creation():
    """Test temporary directory creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config()
        config.TEMP_STORAGE_PATH = os.path.join(temp_dir, "test_spark_videos")
        
        # Directory should not exist initially
        assert not os.path.exists(config.TEMP_STORAGE_PATH)
        
        # After calling ensure_temp_directory, it should exist
        config.ensure_temp_directory()
        assert os.path.exists(config.TEMP_STORAGE_PATH)
        assert os.path.isdir(config.TEMP_STORAGE_PATH)


def test_model_manager_creation():
    """Test ModelManager creation and basic functionality."""
    config = Config()
    manager = ModelManager(config)
    
    assert manager.config == config
    
    # Test getting available models
    chatbot_models = manager.get_available_models("chatbot")
    assert "gpt-4o" in chatbot_models
    assert "gpt-4" in chatbot_models
    
    image_models = manager.get_available_models("image_generation")
    assert "dall-e-3" in image_models
    assert "stable-diffusion" in image_models


def test_model_manager_model_switching():
    """Test model switching functionality."""
    config = Config()
    manager = ModelManager(config)
    
    # Test valid model switch
    result = manager.switch_model("chatbot", "gpt-4")
    assert result is True
    assert config.CHATBOT_MODEL == "gpt-4"
    
    # Test invalid model switch
    result = manager.switch_model("chatbot", "invalid-model")
    assert result is False
    assert config.CHATBOT_MODEL == "gpt-4"  # Should remain unchanged
    
    # Test invalid model type
    result = manager.switch_model("invalid-type", "gpt-4")
    assert result is False


def test_model_manager_health_check():
    """Test model health check functionality."""
    config = Config()
    manager = ModelManager(config)
    
    health_status = manager.health_check_models()
    
    assert isinstance(health_status, dict)
    assert "chatbot" in health_status
    assert "image_generation" in health_status
    assert "detailed_story" in health_status
    assert "video_generation" in health_status
    
    # All should be False since no API keys are set
    assert all(not status for status in health_status.values())


if __name__ == "__main__":
    pytest.main([__file__])