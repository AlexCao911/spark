"""
Demo mode implementations for testing without API keys.
"""

import json
import random
import time
from typing import Dict, List, Any, Optional
from ..models import UserIdea, StoryOutline, CharacterProfile


class DemoChatbotCore:
    """Demo version of ChatbotCore that works without API keys."""
    
    def __init__(self):
        self.conversation_history = []
        self.demo_responses = [
            "That sounds like an exciting video idea! Can you tell me more about the main characters?",
            "Interesting! What genre are you thinking - action, comedy, drama, or something else?",
            "Great concept! How long do you want the video to be?",
            "I love that theme! What's the target audience for this video?",
            "Excellent! Can you describe the visual style you're imagining?",
            "Perfect! What mood or tone should the video have?",
            "That's a compelling story! Do you have any specific plot points in mind?",
            "Wonderful! I think we have enough information to structure your idea now."
        ]
        self.response_index = 0
    
    def engage_user(self, initial_input: str) -> Dict:
        """Demo version of user engagement."""
        self.conversation_history.append({"role": "user", "content": initial_input})
        
        # Simulate processing delay
        time.sleep(0.5)
        
        response = self.demo_responses[self.response_index % len(self.demo_responses)]
        self.response_index += 1
        
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Simulate completeness analysis
        is_complete = len(self.conversation_history) >= 8  # After 4 exchanges
        missing_elements = [] if is_complete else ["characters", "plot", "style"]
        
        return {
            "status": "engaged",
            "response": response,
            "is_complete": is_complete,
            "missing_elements": missing_elements,
            "conversation_id": "demo_session"
        }
    
    def continue_conversation(self, user_input: str) -> Dict:
        """Demo version of conversation continuation."""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        time.sleep(0.5)
        
        response = self.demo_responses[self.response_index % len(self.demo_responses)]
        self.response_index += 1
        
        self.conversation_history.append({"role": "assistant", "content": response})
        
        is_complete = len(self.conversation_history) >= 8
        missing_elements = [] if is_complete else ["details", "refinement"]
        
        return {
            "status": "continued",
            "response": response,
            "is_complete": is_complete,
            "missing_elements": missing_elements
        }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def reset_conversation(self) -> None:
        """Reset conversation."""
        self.conversation_history = []
        self.response_index = 0


class DemoIdeaStructurer:
    """Demo version of IdeaStructurer."""
    
    def structure_conversation(self, conversation_history: List[Dict[str, str]]) -> Optional[UserIdea]:
        """Demo version of conversation structuring."""
        time.sleep(1)  # Simulate processing
        
        # Extract some keywords from conversation for demo
        conversation_text = " ".join([msg.get("content", "") for msg in conversation_history if msg.get("role") == "user"])
        
        # Demo idea based on conversation content
        if "space" in conversation_text.lower() or "sci-fi" in conversation_text.lower():
            return UserIdea(
                theme="space exploration",
                genre="sci-fi",
                target_audience="adults",
                duration_preference=120,
                basic_characters=["brave astronaut", "alien ambassador"],
                plot_points=["launch mission", "discover alien life", "first contact", "return to Earth"],
                visual_style="cinematic",
                mood="adventurous"
            )
        elif "comedy" in conversation_text.lower() or "funny" in conversation_text.lower():
            return UserIdea(
                theme="friendship",
                genre="comedy",
                target_audience="general",
                duration_preference=90,
                basic_characters=["clumsy hero", "wise-cracking sidekick"],
                plot_points=["meet by accident", "get into trouble", "work together", "save the day"],
                visual_style="colorful",
                mood="lighthearted"
            )
        else:
            return UserIdea(
                theme="adventure",
                genre="action",
                target_audience="teens",
                duration_preference=150,
                basic_characters=["young hero", "mysterious mentor"],
                plot_points=["call to adventure", "training montage", "face the villain", "victory"],
                visual_style="dynamic",
                mood="exciting"
            )
    
    def generate_story_outline(self, user_idea: UserIdea) -> Optional[StoryOutline]:
        """Demo version of story outline generation."""
        time.sleep(1.5)  # Simulate processing
        
        return StoryOutline(
            title=f"The {user_idea.theme.title()} Chronicles",
            summary=f"An epic {user_idea.genre} story about {', '.join(user_idea.basic_characters[:2])} on a thrilling journey.",
            narrative_text=f"""
This {user_idea.mood} {user_idea.genre} story follows {user_idea.basic_characters[0]} as they embark on an incredible journey.

The adventure begins when {user_idea.plot_points[0] if user_idea.plot_points else 'the story starts'}. Our hero must navigate through challenges and discover their true potential.

With a {user_idea.visual_style} visual style, this {user_idea.duration_preference}-second video will captivate {user_idea.target_audience} audiences with its engaging narrative and compelling characters.

The story builds through {', '.join(user_idea.plot_points[1:-1]) if len(user_idea.plot_points) > 2 else 'various challenges'} before reaching its climactic conclusion where {user_idea.plot_points[-1] if user_idea.plot_points else 'the hero succeeds'}.
            """.strip(),
            estimated_duration=user_idea.duration_preference
        )
    
    def validate_idea_completeness(self, idea: UserIdea) -> Dict[str, Any]:
        """Demo validation."""
        return {
            "is_complete": True,
            "completeness_score": 0.9,
            "missing_elements": [],
            "suggestions": ["Great idea! Ready for production."],
            "details": {
                "theme": True,
                "genre": True,
                "characters": True,
                "plot_points": True,
                "target_audience": True,
                "duration": True,
                "visual_style": True,
                "mood": True
            }
        }


class DemoCharacterProfileGenerator:
    """Demo version of CharacterProfileGenerator."""
    
    def generate_complete_character_profiles(self, characters: List[str], user_idea: UserIdea) -> List[CharacterProfile]:
        """Demo version of character profile generation."""
        time.sleep(1)  # Simulate processing
        
        profiles = []
        demo_personalities = ["brave and determined", "wise and patient", "cunning and mysterious", "cheerful and optimistic"]
        demo_backstories = [
            "Grew up in a small village with big dreams",
            "Former warrior turned peaceful mentor", 
            "Mysterious figure with a hidden past",
            "Young adventurer seeking their destiny"
        ]
        
        for i, character_desc in enumerate(characters):
            profile = CharacterProfile(
                name=f"Character_{i+1}",
                role="main" if i == 0 else "supporting",
                appearance=f"Appearance based on: {character_desc}",
                personality=demo_personalities[i % len(demo_personalities)],
                backstory=demo_backstories[i % len(demo_backstories)],
                motivations=[f"motivation_{i+1}_a", f"motivation_{i+1}_b"],
                relationships={},
                image_url=f"https://placeholder.com/300x400/character_{i+1}.jpg",
                visual_consistency_tags=[f"tag_{i+1}_a", f"tag_{i+1}_b"]
            )
            profiles.append(profile)
        
        return profiles
    
    def generate_character_image(self, character_profile: CharacterProfile) -> str:
        """Demo version of image generation."""
        return f"https://placeholder.com/300x400/{character_profile.name.lower()}.jpg"


def create_demo_interface():
    """Create a demo version of the chatbot interface."""
    from .gradio_interface_fixed import ChatbotGradioInterfaceFixed
    
    # Create interface with demo components
    interface = ChatbotGradioInterfaceFixed()
    
    # Replace with demo versions
    interface.chatbot_core = DemoChatbotCore()
    interface.idea_structurer = DemoIdeaStructurer()
    interface.character_generator = DemoCharacterProfileGenerator()
    
    return interface