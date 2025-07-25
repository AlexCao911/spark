"""
Configuration management for the Spark AI Video Generation Pipeline.
"""

import os
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class RetryConfig(BaseModel):
    """Configuration for API retry logic."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0


class Config(BaseSettings):
    """Main configuration class with functional API key names."""
    
    # API Configuration - Functional names for different AI services
    CHATBOT_API_KEY: str = Field(default="", description="API key for chatbot interactions (GPT-4o)")
    IMAGE_GEN_API_KEY: str = Field(default="", description="API key for character image generation")
    DETAILED_STORY_API_KEY: str = Field(default="", description="API key for story expansion (Qwen3)")
    VIDEO_GENERATE_API_KEY: str = Field(default="", description="API key for video generation (VEO3)")
    
    # Model Configuration
    CHATBOT_MODEL: str = "qwen-turbo-latest"  # For user interaction and idea structuring
    IMAGE_GEN_MODEL: str = "wanx-v1"  # For character image generation using Wanx2.1-t2i-turbo
    DETAILED_STORY_MODEL: str = "qwen-turbo-latest"  # For story expansion and prompt generation
    VIDEO_GENERATE_MODEL: str = "veo3-standard"  # For video clip generation
    
    # API Endpoints (configurable for different providers)
    CHATBOT_API_ENDPOINT: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    IMAGE_GEN_API_ENDPOINT: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    DETAILED_STORY_API_ENDPOINT: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    VIDEO_GENERATE_API_ENDPOINT: str = "https://api.veo3.com/v1"
    
    # Processing Configuration
    MAX_VIDEO_DURATION: int = 300  # seconds
    MAX_CONCURRENT_GENERATIONS: int = 3
    TEMP_STORAGE_PATH: str = "/tmp/spark_videos"
    
    # Retry Configuration
    API_MAX_RETRIES: int = 3
    API_BASE_DELAY: float = 1.0
    API_MAX_DELAY: float = 60.0
    API_EXPONENTIAL_BASE: float = 2.0
    
    # Content Safety
    ENABLE_CONTENT_FILTERING: bool = True
    MAX_CHARACTERS_PER_STORY: int = 10
    MAX_SHOTS_PER_VIDEO: int = 50
    
    # Development Configuration
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment
    
    @property
    def retry_config(self) -> RetryConfig:
        """Get retry configuration object."""
        return RetryConfig(
            max_retries=self.API_MAX_RETRIES,
            base_delay=self.API_BASE_DELAY,
            max_delay=self.API_MAX_DELAY,
            exponential_base=self.API_EXPONENTIAL_BASE
        )
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        keys_status = {
            "chatbot": bool(self.CHATBOT_API_KEY),
            "image_generation": bool(self.IMAGE_GEN_API_KEY),
            "detailed_story": bool(self.DETAILED_STORY_API_KEY),
            "video_generation": bool(self.VIDEO_GENERATE_API_KEY)
        }
        return keys_status
    
    def get_missing_api_keys(self) -> List[str]:
        """Get list of missing API keys."""
        validation = self.validate_api_keys()
        return [key for key, is_valid in validation.items() if not is_valid]
    
    def ensure_temp_directory(self) -> None:
        """Ensure temporary storage directory exists."""
        os.makedirs(self.TEMP_STORAGE_PATH, exist_ok=True)


class ModelManager:
    """Manager for dynamic model switching and health checks."""
    
    def __init__(self, config: Config):
        self.config = config
        self._available_models = {
            "chatbot": ["qwen-turbo-latest", "qwen-plus", "qwen-max", "gpt-4o", "gpt-4"],
            "image_generation": ["wanx-v1", "dall-e-3", "dall-e-2"],
            "detailed_story": ["qwen-turbo-latest", "qwen-plus", "qwen-max", "gpt-4"],
            "video_generation": ["veo3-standard", "veo3-pro"]
        }
    
    def get_available_models(self, model_type: str) -> List[str]:
        """Get list of available models for a given type."""
        return self._available_models.get(model_type, [])
    
    def switch_model(self, model_type: str, new_model: str) -> bool:
        """Switch to a different model for a given type."""
        available = self.get_available_models(model_type)
        if new_model not in available:
            return False
        
        # Update configuration based on model type
        if model_type == "chatbot":
            self.config.CHATBOT_MODEL = new_model
        elif model_type == "image_generation":
            self.config.IMAGE_GEN_MODEL = new_model
        elif model_type == "detailed_story":
            self.config.DETAILED_STORY_MODEL = new_model
        elif model_type == "video_generation":
            self.config.VIDEO_GENERATE_MODEL = new_model
        else:
            return False
        
        return True
    
    def health_check_models(self) -> Dict[str, bool]:
        """Perform health checks on configured models."""
        # This would implement actual health checks in a real system
        # For now, return basic validation
        return {
            "chatbot": bool(self.config.CHATBOT_API_KEY),
            "image_generation": bool(self.config.IMAGE_GEN_API_KEY),
            "detailed_story": bool(self.config.DETAILED_STORY_API_KEY),
            "video_generation": bool(self.config.VIDEO_GENERATE_API_KEY)
        }


# Global configuration instance
config = Config()
model_manager = ModelManager(config)