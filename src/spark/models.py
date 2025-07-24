"""
Core data models for the Spark AI Video Generation Pipeline.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class UserIdea(BaseModel):
    """User's initial creative idea for video generation."""
    theme: str = ""
    genre: str = ""
    target_audience: str = ""
    duration_preference: int = 60  # in seconds
    basic_characters: List[str] = Field(default_factory=list)  # basic character descriptions from user
    plot_points: List[str] = Field(default_factory=list)
    visual_style: str = ""
    mood: str = ""


class CharacterProfile(BaseModel):
    """Complete character profile with visual design."""
    name: str
    role: str
    appearance: str
    personality: str
    backstory: str
    motivations: List[str] = Field(default_factory=list)
    relationships: Dict[str, str] = Field(default_factory=dict)  # relationships with other characters
    image_url: str = ""
    visual_consistency_tags: List[str] = Field(default_factory=list)  # for maintaining visual consistency across scenes


class StoryOutline(BaseModel):
    """Story outline that user reviews and approves."""
    title: str
    summary: str
    narrative_text: str  # Coherent story outline text that user sees and approves
    estimated_duration: int  # in seconds


class ApprovedContent(BaseModel):
    """User-approved content ready for production."""
    story_outline: StoryOutline
    character_profiles: List[CharacterProfile] = Field(default_factory=list)
    user_confirmed: bool = False


class DetailedStory(BaseModel):
    """Complete, detailed narrative text for video production."""
    title: str
    full_story_text: str  # Complete, detailed, coherent narrative text
    total_duration: int  # in seconds


class Shot(BaseModel):
    """Individual shot breakdown from detailed story."""
    shot_id: int
    description: str  # What happens in this specific shot
    characters_present: List[str] = Field(default_factory=list)
    location: str
    duration: int  # in seconds


class VideoPrompt(BaseModel):
    """VEO3-optimized prompt for video generation."""
    shot_id: int
    veo3_prompt: str  # Complete optimized prompt for VEO3 with character context
    duration: int  # in seconds
    character_reference_images: List[str] = Field(default_factory=list)  # For visual consistency


class VideoClip(BaseModel):
    """Generated video clip information."""
    clip_id: int
    shot_id: int
    file_path: str
    duration: int  # in seconds
    status: str = "pending"  # "generating", "completed", "failed", "pending"
    generation_job_id: Optional[str] = None


class VideoGenerationState(BaseModel):
    """State management for the video generation flow."""
    # Stage 1: User idea and approval
    user_idea: UserIdea = Field(default_factory=UserIdea)
    approved_content: ApprovedContent = Field(default_factory=lambda: ApprovedContent(
        story_outline=StoryOutline(title="", summary="", narrative_text="", estimated_duration=0)
    ))
    
    # Stage 2: Story expansion (coherent narrative text)
    detailed_story: DetailedStory = Field(default_factory=lambda: DetailedStory(
        title="", full_story_text="", total_duration=0
    ))
    
    # Stage 3: Shot breakdown and prompt generation
    video_prompts: List[VideoPrompt] = Field(default_factory=list)
    video_clip_urls: List[str] = Field(default_factory=list)
    final_video_path: str = ""