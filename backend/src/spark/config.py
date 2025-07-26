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
    
    # Storage Configuration
    PROJECTS_STORAGE_PATH: str = "projects"  # Base path for project storage
    ENABLE_AUTO_SAVE: bool = True  # Automatically save generated content
    MAX_PROJECTS: int = 100  # Maximum number of projects to keep
    AUTO_EXPORT_FORMAT: str = "json"  # Default export format

    # Retry Configuration
    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables
    
    def get_missing_api_keys(self) -> List[str]:
        """Check which API keys are missing."""
        missing = []
        if not self.CHATBOT_API_KEY:
            missing.append("CHATBOT_API_KEY")
        if not self.IMAGE_GEN_API_KEY:
            missing.append("IMAGE_GEN_API_KEY") 
        if not self.DETAILED_STORY_API_KEY:
            missing.append("DETAILED_STORY_API_KEY")
        if not self.VIDEO_GENERATE_API_KEY:
            missing.append("VIDEO_GENERATE_API_KEY")
        return missing
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate that all required configuration is present."""
        validation = {
            "api_keys_present": len(self.get_missing_api_keys()) == 0,
            "endpoints_configured": all([
                self.CHATBOT_API_ENDPOINT,
                self.IMAGE_GEN_API_ENDPOINT,
                self.DETAILED_STORY_API_ENDPOINT,
                self.VIDEO_GENERATE_API_ENDPOINT
            ]),
            "models_configured": all([
                self.CHATBOT_MODEL,
                self.IMAGE_GEN_MODEL,
                self.DETAILED_STORY_MODEL,
                self.VIDEO_GENERATE_MODEL
            ])
        }
        validation["all_valid"] = all(validation.values())
        return validation
    
    def get_llm_for_crew(self):
        """Get LLM configuration for CrewAI."""
        try:
            # Import here to avoid circular imports
            from langchain_openai import ChatOpenAI
            
            # Use DETAILED_STORY_API_KEY for crew operations since it's for Qwen
            return ChatOpenAI(
                model=self.DETAILED_STORY_MODEL,
                api_key=self.DETAILED_STORY_API_KEY,
                base_url=self.DETAILED_STORY_API_ENDPOINT,
                temperature=0.7,
                max_tokens=2000
            )
        except ImportError:
            # Fallback if langchain_openai is not available
            print("Warning: langchain_openai not available, using mock LLM for crew")
            return None


class ModelManager:
    """Manages model switching and configuration."""
    
    def __init__(self, config: Config):
        self.config = config
        self.active_models = {
            "chatbot": config.CHATBOT_MODEL,
            "image_gen": config.IMAGE_GEN_MODEL,
            "detailed_story": config.DETAILED_STORY_MODEL,
            "video_generate": config.VIDEO_GENERATE_MODEL
        }
    
    def switch_model(self, service: str, model_name: str) -> bool:
        """Switch to a different model for a service."""
        if service in self.active_models:
            self.active_models[service] = model_name
            return True
        return False
    
    def get_active_model(self, service: str) -> str:
        """Get the currently active model for a service."""
        return self.active_models.get(service, "unknown")
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List available models for each service."""
        return {
            "chatbot": ["qwen-turbo-latest", "gpt-4o", "claude-3-opus"],
            "image_gen": ["wanx-v1", "dalle-3", "midjourney"],
            "detailed_story": ["qwen-turbo-latest", "gpt-4o"],
            "video_generate": ["veo3-standard", "veo3-premium", "runway-ml"]
        }


# Global configuration instance
config = Config()
model_manager = ModelManager(config)