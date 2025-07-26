"""
Tests for core data models.
"""

import pytest
from spark.models import (
    UserIdea, CharacterProfile, StoryOutline, ApprovedContent,
    DetailedStory, Shot, VideoPrompt, VideoClip, VideoGenerationState
)


def test_user_idea_creation():
    """Test UserIdea model creation and validation."""
    idea = UserIdea(
        theme="Adventure",
        genre="Fantasy",
        target_audience="Young Adults",
        duration_preference=120,
        basic_characters=["Hero", "Villain"],
        plot_points=["Beginning", "Conflict", "Resolution"],
        visual_style="Cinematic",
        mood="Epic"
    )
    
    assert idea.theme == "Adventure"
    assert idea.duration_preference == 120
    assert len(idea.basic_characters) == 2
    assert len(idea.plot_points) == 3


def test_character_profile_creation():
    """Test CharacterProfile model creation and validation."""
    character = CharacterProfile(
        name="Hero",
        role="Protagonist",
        appearance="Tall, dark hair, blue eyes",
        personality="Brave and determined",
        backstory="Orphaned at young age",
        motivations=["Save the world", "Find family"],
        relationships={"Villain": "Enemy", "Mentor": "Teacher"},
        image_url="https://example.com/hero.jpg",
        visual_consistency_tags=["blue_eyes", "dark_hair", "tall"]
    )
    
    assert character.name == "Hero"
    assert len(character.motivations) == 2
    assert character.relationships["Villain"] == "Enemy"
    assert len(character.visual_consistency_tags) == 3


def test_story_outline_creation():
    """Test StoryOutline model creation and validation."""
    outline = StoryOutline(
        title="The Great Adventure",
        summary="A hero's journey to save the world",
        narrative_text="Once upon a time, in a land far away...",
        estimated_duration=180
    )
    
    assert outline.title == "The Great Adventure"
    assert outline.estimated_duration == 180
    assert "Once upon a time" in outline.narrative_text


def test_video_prompt_creation():
    """Test VideoPrompt model creation and validation."""
    prompt = VideoPrompt(
        shot_id=1,
        veo3_prompt="A hero stands on a mountain peak at sunrise",
        duration=10,
        character_reference_images=["hero_ref.jpg"]
    )
    
    assert prompt.shot_id == 1
    assert prompt.duration == 10
    assert len(prompt.character_reference_images) == 1


def test_video_generation_state_creation():
    """Test VideoGenerationState model creation and default values."""
    state = VideoGenerationState()
    
    assert isinstance(state.user_idea, UserIdea)
    assert isinstance(state.approved_content, ApprovedContent)
    assert isinstance(state.detailed_story, DetailedStory)
    assert isinstance(state.video_prompts, list)
    assert len(state.video_prompts) == 0
    assert state.final_video_path == ""


def test_approved_content_validation():
    """Test ApprovedContent model with nested objects."""
    outline = StoryOutline(
        title="Test Story",
        summary="Test summary",
        narrative_text="Test narrative",
        estimated_duration=60
    )
    
    character = CharacterProfile(
        name="Test Character",
        role="Test Role",
        appearance="Test appearance",
        personality="Test personality",
        backstory="Test backstory"
    )
    
    approved = ApprovedContent(
        story_outline=outline,
        character_profiles=[character],
        user_confirmed=True
    )
    
    assert approved.user_confirmed is True
    assert approved.story_outline.title == "Test Story"
    assert len(approved.character_profiles) == 1
    assert approved.character_profiles[0].name == "Test Character"


if __name__ == "__main__":
    pytest.main([__file__])