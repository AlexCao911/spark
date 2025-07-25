"""
Unit tests for CharacterProfileGenerator class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.spark.chatbot.character_generator import CharacterProfileGenerator
from src.spark.models import CharacterProfile, UserIdea


class TestCharacterProfileGenerator:
    """Test cases for CharacterProfileGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create CharacterProfileGenerator instance for testing."""
        return CharacterProfileGenerator()
    
    @pytest.fixture
    def sample_user_idea(self):
        """Sample UserIdea for testing."""
        return UserIdea(
            theme="adventure",
            genre="action",
            target_audience="teens",
            duration_preference=120,
            basic_characters=["brave hero", "wise mentor", "cunning villain"],
            plot_points=["hero's journey begins", "faces challenges", "overcomes obstacles"],
            visual_style="cinematic",
            mood="exciting"
        )
    
    def test_init(self, generator):
        """Test CharacterProfileGenerator initialization."""
        assert generator is not None
        assert isinstance(generator, CharacterProfileGenerator)
    
    def test_generate_complete_character_profiles_basic(self, generator, sample_user_idea):
        """Test basic character profile generation."""
        characters = ["brave hero", "wise mentor"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        assert len(profiles) == 2
        assert all(isinstance(profile, CharacterProfile) for profile in profiles)
        
        # Check first character (main character)
        hero = profiles[0]
        assert hero.name == "Character_1"
        assert hero.role == "main"
        assert "brave hero" in hero.appearance
        
        # Check second character (supporting)
        mentor = profiles[1]
        assert mentor.name == "Character_2"
        assert mentor.role == "supporting"
        assert "wise mentor" in mentor.appearance
    
    def test_generate_complete_character_profiles_empty_list(self, generator, sample_user_idea):
        """Test character profile generation with empty character list."""
        characters = []
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        assert len(profiles) == 0
        assert isinstance(profiles, list)
    
    def test_generate_complete_character_profiles_single_character(self, generator, sample_user_idea):
        """Test character profile generation with single character."""
        characters = ["lone protagonist"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        assert len(profiles) == 1
        profile = profiles[0]
        assert profile.name == "Character_1"
        assert profile.role == "main"
        assert "lone protagonist" in profile.appearance
    
    def test_generate_complete_character_profiles_multiple_characters(self, generator, sample_user_idea):
        """Test character profile generation with multiple characters."""
        characters = ["hero", "villain", "sidekick", "mentor", "love interest"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        assert len(profiles) == 5
        
        # First character should be main
        assert profiles[0].role == "main"
        
        # Rest should be supporting
        for i in range(1, 5):
            assert profiles[i].role == "supporting"
            assert profiles[i].name == f"Character_{i+1}"
    
    def test_character_profile_structure(self, generator, sample_user_idea):
        """Test that generated character profiles have correct structure."""
        characters = ["test character"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        profile = profiles[0]
        
        # Check all required fields are present
        assert hasattr(profile, 'name')
        assert hasattr(profile, 'role')
        assert hasattr(profile, 'appearance')
        assert hasattr(profile, 'personality')
        assert hasattr(profile, 'backstory')
        assert hasattr(profile, 'motivations')
        assert hasattr(profile, 'relationships')
        assert hasattr(profile, 'image_url')
        assert hasattr(profile, 'visual_consistency_tags')
        
        # Check field types
        assert isinstance(profile.name, str)
        assert isinstance(profile.role, str)
        assert isinstance(profile.appearance, str)
        assert isinstance(profile.personality, str)
        assert isinstance(profile.backstory, str)
        assert isinstance(profile.motivations, list)
        assert isinstance(profile.relationships, dict)
        assert isinstance(profile.image_url, str)
        assert isinstance(profile.visual_consistency_tags, list)
    
    def test_generate_character_image_placeholder(self, generator):
        """Test character image generation (placeholder implementation)."""
        profile = CharacterProfile(
            name="Test Hero",
            role="main",
            appearance="Tall and brave",
            personality="Courageous",
            backstory="Grew up in a village",
            motivations=["save the world"],
            relationships={},
            image_url="",
            visual_consistency_tags=[]
        )
        
        image_url = generator.generate_character_image(profile)
        
        assert isinstance(image_url, str)
        assert len(image_url) > 0
        assert "Test Hero" in image_url or "character" in image_url.lower()
    
    def test_character_naming_convention(self, generator, sample_user_idea):
        """Test that characters are named with proper convention."""
        characters = ["first", "second", "third"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        expected_names = ["Character_1", "Character_2", "Character_3"]
        actual_names = [profile.name for profile in profiles]
        
        assert actual_names == expected_names
    
    def test_role_assignment(self, generator, sample_user_idea):
        """Test that roles are assigned correctly."""
        characters = ["protagonist", "antagonist", "helper"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        # First character should be main
        assert profiles[0].role == "main"
        
        # Others should be supporting
        assert profiles[1].role == "supporting"
        assert profiles[2].role == "supporting"
    
    def test_appearance_includes_description(self, generator, sample_user_idea):
        """Test that appearance field includes original character description."""
        characters = ["mysterious detective with a long coat", "cheerful baker with flour-covered apron"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        
        assert "mysterious detective with a long coat" in profiles[0].appearance
        assert "cheerful baker with flour-covered apron" in profiles[1].appearance
    
    def test_motivations_structure(self, generator, sample_user_idea):
        """Test that motivations are properly structured."""
        characters = ["hero"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        profile = profiles[0]
        
        assert isinstance(profile.motivations, list)
        assert len(profile.motivations) >= 1
        assert all(isinstance(motivation, str) for motivation in profile.motivations)
    
    def test_relationships_structure(self, generator, sample_user_idea):
        """Test that relationships are properly structured."""
        characters = ["hero"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        profile = profiles[0]
        
        assert isinstance(profile.relationships, dict)
        # Initially empty, but should be a dict
        assert len(profile.relationships) == 0
    
    def test_visual_consistency_tags_structure(self, generator, sample_user_idea):
        """Test that visual consistency tags are properly structured."""
        characters = ["hero"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        profile = profiles[0]
        
        assert isinstance(profile.visual_consistency_tags, list)
        # Initially empty, but should be a list
        assert len(profile.visual_consistency_tags) == 0
    
    def test_character_profile_completeness(self, generator, sample_user_idea):
        """Test that all character profiles are complete and valid."""
        characters = ["detailed character with complex background"]
        
        profiles = generator.generate_complete_character_profiles(characters, sample_user_idea)
        profile = profiles[0]
        
        # All string fields should have content
        assert len(profile.name) > 0
        assert len(profile.role) > 0
        assert len(profile.appearance) > 0
        assert len(profile.personality) > 0
        assert len(profile.backstory) > 0
        
        # Lists should be initialized (even if empty)
        assert isinstance(profile.motivations, list)
        assert isinstance(profile.visual_consistency_tags, list)
        
        # Dict should be initialized
        assert isinstance(profile.relationships, dict)
    
    def test_integration_with_user_idea_context(self, generator):
        """Test that character generation considers UserIdea context."""
        # Test with different genres/themes
        sci_fi_idea = UserIdea(
            theme="space exploration",
            genre="sci-fi",
            basic_characters=["space captain"],
            plot_points=["launch", "discovery", "return"]
        )
        
        fantasy_idea = UserIdea(
            theme="magical quest",
            genre="fantasy", 
            basic_characters=["wizard"],
            plot_points=["spell", "quest", "victory"]
        )
        
        sci_fi_profiles = generator.generate_complete_character_profiles(
            sci_fi_idea.basic_characters, sci_fi_idea
        )
        
        fantasy_profiles = generator.generate_complete_character_profiles(
            fantasy_idea.basic_characters, fantasy_idea
        )
        
        # Both should generate valid profiles
        assert len(sci_fi_profiles) == 1
        assert len(fantasy_profiles) == 1
        
        # Profiles should contain the character descriptions
        assert "space captain" in sci_fi_profiles[0].appearance
        assert "wizard" in fantasy_profiles[0].appearance


if __name__ == "__main__":
    pytest.main([__file__])