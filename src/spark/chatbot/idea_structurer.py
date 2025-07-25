"""
Idea structuring functionality for converting conversations to structured data.
"""

import json
import logging
import re
from typing import List, Dict, Optional, Any
from openai import OpenAI
from ..models import UserIdea, StoryOutline
from ..config import config
# Local error handling decorator defined below

logger = logging.getLogger(__name__)


class PromptTemplates:
    """Templates for consistent structured output generation."""
    
    IDEA_EXTRACTION_PROMPT = """
You are an expert at analyzing creative conversations and extracting structured information about video ideas.

Analyze the following conversation and extract the key elements for a video concept. Return ONLY a valid JSON object with the following structure:

{{
    "theme": "main theme or concept of the video",
    "genre": "genre (e.g., comedy, drama, action, horror, sci-fi, fantasy, documentary, etc.)",
    "target_audience": "intended audience (e.g., children, teens, adults, general, etc.)",
    "duration_preference": 60,
    "basic_characters": ["character description 1", "character description 2"],
    "plot_points": ["plot point 1", "plot point 2", "plot point 3"],
    "visual_style": "visual style preference (e.g., cinematic, animated, documentary, etc.)",
    "mood": "overall mood or tone (e.g., adventurous, mysterious, funny, dramatic, etc.)"
}}

Rules:
1. Extract information ONLY from what is explicitly mentioned in the conversation
2. If information is not mentioned, use reasonable defaults or empty values
3. For duration_preference, use seconds (default 60 for 1 minute if not specified)
4. Keep character descriptions concise but descriptive
5. Plot points should be key story beats or events
6. Return ONLY the JSON object, no additional text

Conversation to analyze:
{conversation_text}
"""

    STORY_OUTLINE_PROMPT = """
You are a professional story developer. Based on the user's video idea, create a compelling story outline.

Create a story outline with the following JSON structure:

{{
    "title": "compelling title for the video",
    "summary": "brief 2-3 sentence summary of the story",
    "narrative_text": "detailed narrative description that tells the complete story in a coherent, engaging way (3-5 paragraphs)",
    "estimated_duration": 60
}}

User's video idea:
Theme: {theme}
Genre: {genre}
Characters: {characters}
Plot Points: {plot_points}
Visual Style: {visual_style}
Mood: {mood}
Target Audience: {target_audience}
Duration Preference: {duration_preference} seconds

Create an engaging story that incorporates all these elements. The narrative_text should be a complete, coherent story that could be used as the basis for video production.

Return ONLY the JSON object, no additional text.
"""

    VALIDATION_PROMPT = """
Analyze this video idea JSON and identify any missing or incomplete elements:

{idea_json}

Return a JSON object with this structure:
{{
    "is_complete": true/false,
    "missing_elements": ["list", "of", "missing", "elements"],
    "suggestions": ["specific suggestions for improvement"]
}}

Consider an idea complete if it has:
- Clear theme and genre
- At least one character description
- At least 2-3 plot points
- Reasonable duration and target audience
"""


def handle_api_errors(func):
    """Simple decorator to handle API errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {str(e)}")
            # Return error response instead of raising
            return None
    return wrapper


class IdeaStructurer:
    """Converts natural language conversations to structured UserIdea objects."""
    
    def __init__(self):
        self.config = config
        self.client = OpenAI(
            api_key=self.config.CHATBOT_API_KEY,
            base_url=self.config.CHATBOT_API_ENDPOINT
        )
        self.templates = PromptTemplates()
    
    @handle_api_errors
    def structure_conversation(self, conversation_history: List[Dict[str, str]]) -> Optional[UserIdea]:
        """Convert conversation history to structured UserIdea."""
        try:
            # Extract conversation text (user messages only)
            conversation_text = self._extract_conversation_text(conversation_history)
            
            if not conversation_text.strip():
                logger.warning("Empty conversation text provided")
                return self._create_default_idea()
            
            # Generate structured output using GPT-4o
            prompt = self.templates.IDEA_EXTRACTION_PROMPT.format(
                conversation_text=conversation_text
            )
            
            response = self.client.chat.completions.create(
                model=self.config.CHATBOT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from conversations. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3  # Lower temperature for more consistent structured output
            )
            
            # Parse the JSON response
            response_text = response.choices[0].message.content.strip()
            idea_data = self._parse_json_response(response_text)
            
            if idea_data:
                return UserIdea(**idea_data)
            else:
                logger.warning("Failed to parse JSON response, using fallback extraction")
                return self._fallback_extraction(conversation_text)
                
        except Exception as e:
            logger.error(f"Error in structure_conversation: {str(e)}")
            return self._fallback_extraction(conversation_text if 'conversation_text' in locals() else "")
    
    def _extract_conversation_text(self, conversation_history: List[Dict[str, str]]) -> str:
        """Extract user messages from conversation history."""
        user_messages = []
        for message in conversation_history:
            if message.get("role") == "user":
                user_messages.append(message.get("content", ""))
        
        return "\n".join(user_messages)
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from API, handling various formats."""
        try:
            # Try to parse as-is first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to find JSON object in the text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Failed to parse JSON from response: {response_text[:200]}...")
            return None
    
    def _fallback_extraction(self, conversation_text: str) -> UserIdea:
        """Fallback method using keyword extraction when API fails."""
        logger.info("Using fallback keyword extraction")
        
        # Simple keyword-based extraction
        text_lower = conversation_text.lower()
        
        # Extract theme
        theme = "adventure"  # default
        if "love" in text_lower or "romance" in text_lower:
            theme = "romance"
        elif "mystery" in text_lower or "detective" in text_lower:
            theme = "mystery"
        elif "space" in text_lower or "sci-fi" in text_lower:
            theme = "science fiction"
        elif "magic" in text_lower or "fantasy" in text_lower:
            theme = "fantasy"
        
        # Extract genre
        genre = "drama"  # default
        genre_keywords = {
            "comedy": ["funny", "comedy", "humor", "laugh"],
            "horror": ["scary", "horror", "fear", "monster", "zombie"],
            "sci-fi": ["space", "future", "robot", "alien", "sci-fi", "science fiction"],
            "fantasy": ["magic", "wizard", "dragon", "fantasy"],
            "action": ["action", "fight", "battle", "adventure"]
        }
        
        # Check in order of specificity (more specific genres first)
        for g, keywords in genre_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                genre = g
                break
        
        # Extract characters (simple approach)
        characters = ["main character"]
        character_indicators = ["character", "hero", "protagonist", "person", "man", "woman", "boy", "girl"]
        for indicator in character_indicators:
            if indicator in text_lower:
                characters = [f"character mentioned in conversation"]
                break
        
        # Extract plot points (simple approach)
        plot_points = ["beginning", "middle", "end"]
        if "journey" in text_lower:
            plot_points = ["starts journey", "faces challenges", "reaches destination"]
        elif "mystery" in text_lower:
            plot_points = ["mystery discovered", "investigation begins", "mystery solved"]
        
        return UserIdea(
            theme=theme,
            genre=genre,
            target_audience="general",
            duration_preference=60,
            basic_characters=characters,
            plot_points=plot_points,
            visual_style="cinematic",
            mood="engaging"
        )
    
    def _create_default_idea(self) -> UserIdea:
        """Create a default UserIdea when no conversation is provided."""
        return UserIdea(
            theme="adventure",
            genre="drama",
            target_audience="general",
            duration_preference=60,
            basic_characters=["main character"],
            plot_points=["beginning", "conflict", "resolution"],
            visual_style="cinematic",
            mood="engaging"
        )
    
    @handle_api_errors
    def generate_story_outline(self, user_idea: UserIdea) -> Optional[StoryOutline]:
        """Generate a detailed story outline from a UserIdea."""
        try:
            prompt = self.templates.STORY_OUTLINE_PROMPT.format(
                theme=user_idea.theme,
                genre=user_idea.genre,
                characters=", ".join(user_idea.basic_characters),
                plot_points=", ".join(user_idea.plot_points),
                visual_style=user_idea.visual_style,
                mood=user_idea.mood,
                target_audience=user_idea.target_audience,
                duration_preference=user_idea.duration_preference
            )
            
            response = self.client.chat.completions.create(
                model=self.config.CHATBOT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional story developer. Create compelling, coherent story outlines in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            outline_data = self._parse_json_response(response_text)
            
            if outline_data:
                return StoryOutline(**outline_data)
            else:
                return self._create_fallback_outline(user_idea)
                
        except Exception as e:
            logger.error(f"Error generating story outline: {str(e)}")
            return self._create_fallback_outline(user_idea)
    
    def _create_fallback_outline(self, user_idea: UserIdea) -> StoryOutline:
        """Create a fallback story outline when API fails."""
        title = f"A {user_idea.genre.title()} Story"
        summary = f"A {user_idea.mood} {user_idea.genre} about {', '.join(user_idea.basic_characters[:2])}."
        
        narrative_text = f"""
This is a {user_idea.genre} story with a {user_idea.mood} tone, designed for {user_idea.target_audience} audiences.

The story follows {user_idea.basic_characters[0] if user_idea.basic_characters else 'the main character'} through an engaging narrative that explores the theme of {user_idea.theme}.

Key story beats include: {', '.join(user_idea.plot_points)}.

The visual style will be {user_idea.visual_style}, creating an immersive experience that captures the {user_idea.mood} atmosphere throughout the {user_idea.duration_preference}-second video.
        """.strip()
        
        return StoryOutline(
            title=title,
            summary=summary,
            narrative_text=narrative_text,
            estimated_duration=user_idea.duration_preference
        )
    
    def validate_idea_completeness(self, idea: UserIdea) -> Dict[str, Any]:
        """Check if the user idea has all required components."""
        completeness_check = {
            "theme": bool(idea.theme and idea.theme.strip()),
            "genre": bool(idea.genre and idea.genre.strip()),
            "characters": len(idea.basic_characters) > 0 and any(char.strip() for char in idea.basic_characters),
            "plot_points": len(idea.plot_points) >= 2 and any(point.strip() for point in idea.plot_points),
            "target_audience": bool(idea.target_audience and idea.target_audience.strip()),
            "duration": idea.duration_preference > 0,
            "visual_style": bool(idea.visual_style and idea.visual_style.strip()),
            "mood": bool(idea.mood and idea.mood.strip())
        }
        
        missing_elements = [key for key, is_complete in completeness_check.items() if not is_complete]
        is_complete = len(missing_elements) <= 2  # Allow up to 2 missing elements
        
        # Generate suggestions for missing elements
        suggestions = []
        if not completeness_check["theme"]:
            suggestions.append("Specify the main theme or concept of your video")
        if not completeness_check["characters"]:
            suggestions.append("Describe the main characters in your story")
        if not completeness_check["plot_points"]:
            suggestions.append("Outline the key events or story beats")
        if not completeness_check["genre"]:
            suggestions.append("Specify the genre (comedy, drama, action, etc.)")
        
        return {
            "is_complete": is_complete,
            "completeness_score": sum(completeness_check.values()) / len(completeness_check),
            "missing_elements": missing_elements,
            "suggestions": suggestions,
            "details": completeness_check
        }
    
    @handle_api_errors
    def validate_with_ai(self, idea: UserIdea) -> Optional[Dict[str, Any]]:
        """Use AI to validate and provide suggestions for the idea."""
        try:
            idea_json = idea.model_dump_json(indent=2)
            prompt = self.templates.VALIDATION_PROMPT.format(idea_json=idea_json)
            
            response = self.client.chat.completions.create(
                model=self.config.CHATBOT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert story analyst. Provide constructive feedback on video ideas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            validation_data = self._parse_json_response(response_text)
            
            if validation_data:
                return validation_data
            else:
                # Fallback to basic validation
                return self.validate_idea_completeness(idea)
                
        except Exception as e:
            logger.error(f"Error in AI validation: {str(e)}")
            return self.validate_idea_completeness(idea)
    
    def get_schema_template(self) -> Dict[str, Any]:
        """Get the JSON schema template for UserIdea."""
        return {
            "theme": "string - main theme or concept",
            "genre": "string - video genre",
            "target_audience": "string - intended audience",
            "duration_preference": "integer - duration in seconds",
            "basic_characters": ["array of character descriptions"],
            "plot_points": ["array of story beats"],
            "visual_style": "string - visual style preference",
            "mood": "string - overall tone or mood"
        }