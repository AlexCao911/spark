"""
Core chatbot functionality for user interaction.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from ..models import UserIdea
from ..config import config
from ..error_handling import APIErrorHandler, retry_with_backoff
from ..config import config

logger = logging.getLogger(__name__)


def handle_api_errors(func):
    """Simple decorator to handle API errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {str(e)}")
            # Return error response instead of raising
            return {
                "status": "error",
                "response": "I'm experiencing technical difficulties. Please try again.",
                "error": str(e)
            }
    return wrapper


class ConversationManager:
    """Manages conversation context and history."""
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.context: Dict = {}
        self.session_id: Optional[str] = None
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.messages.append({"role": role, "content": content})
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for context."""
        if not self.messages:
            return "No conversation history."
        
        summary_parts = []
        for msg in self.messages[-10:]:  # Last 10 messages for context
            summary_parts.append(f"{msg['role']}: {msg['content'][:100]}...")
        
        return "\n".join(summary_parts)
    
    def update_context(self, key: str, value: any) -> None:
        """Update conversation context."""
        self.context[key] = value
    
    def get_context(self, key: str, default=None) -> any:
        """Get value from conversation context."""
        return self.context.get(key, default)


class ChatbotCore:
    """Main chatbot interaction logic using GPT-4o."""
    
    def __init__(self):
        self.config = config
        self.client = OpenAI(
            api_key=self.config.CHATBOT_API_KEY,
            base_url=self.config.CHATBOT_API_ENDPOINT
        )
        self.conversation_manager = ConversationManager()
        self.error_handler = APIErrorHandler(self.config.retry_config)
        
        # Initialize system prompt
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Qwen chatbot."""
        return """你是一个专业的视频创意助手，帮助用户开发视频创意。你的目标是：

1. 与用户进行自然对话，了解他们的视频概念
2. 提出明确的问题来收集完整信息
3. 帮助将想法结构化为清晰、可执行的视频概念

重点收集这些关键要素：
- 视频的主题和类型
- 目标观众
- 主要角色及其基本描述
- 关键情节点或故事节拍
- 视觉风格偏好
- 情绪和基调
- 首选视频时长

要对话式、鼓励性和创造性。一次只问一个问题，避免让用户感到困扰。
当你收集到足够信息时，表明这个想法已经准备好进行结构化了。

始终以有帮助、热情的语调回应，鼓励创造力。支持中文和英文对话。"""
    
    @handle_api_errors
    def engage_user(self, initial_input: str) -> Dict:
        """Start user engagement and idea gathering."""
        try:
            # Initialize conversation with system prompt
            if not self.conversation_manager.messages:
                self.conversation_manager.add_message("system", self.system_prompt)
            
            # Add user input
            self.conversation_manager.add_message("user", initial_input)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.config.CHATBOT_MODEL,
                messages=self.conversation_manager.messages,
                max_tokens=500,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_manager.add_message("assistant", assistant_response)
            
            # Analyze if we have enough information
            completeness = self._analyze_idea_completeness()
            
            return {
                "status": "engaged",
                "response": assistant_response,
                "is_complete": completeness["is_complete"],
                "missing_elements": completeness["missing_elements"],
                "conversation_id": id(self.conversation_manager)
            }
            
        except Exception as e:
            logger.error(f"Error in engage_user: {str(e)}")
            return {
                "status": "error",
                "response": "I'm having trouble processing your request. Could you try rephrasing your idea?",
                "error": str(e)
            }
    
    @handle_api_errors
    def continue_conversation(self, user_input: str) -> Dict:
        """Continue the conversation with additional user input."""
        try:
            # Add user input to conversation
            self.conversation_manager.add_message("user", user_input)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.config.CHATBOT_MODEL,
                messages=self.conversation_manager.messages,
                max_tokens=500,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_manager.add_message("assistant", assistant_response)
            
            # Check completeness
            completeness = self._analyze_idea_completeness()
            
            return {
                "status": "continued",
                "response": assistant_response,
                "is_complete": completeness["is_complete"],
                "missing_elements": completeness["missing_elements"]
            }
            
        except Exception as e:
            logger.error(f"Error in continue_conversation: {str(e)}")
            return {
                "status": "error",
                "response": "I encountered an issue. Could you please continue with your idea?",
                "error": str(e)
            }
    
    def _analyze_idea_completeness(self) -> Dict:
        """Analyze if the conversation contains enough information for a complete idea."""
        conversation_text = " ".join([msg["content"] for msg in self.conversation_manager.messages if msg["role"] == "user"])
        
        # Simple keyword-based analysis (could be enhanced with NLP)
        required_elements = {
            "theme": ["theme", "about", "story", "concept", "idea"],
            "genre": ["genre", "type", "style", "comedy", "drama", "action", "horror", "romance", "sci-fi", "fantasy"],
            "characters": ["character", "protagonist", "hero", "villain", "person", "people"],
            "plot": ["plot", "story", "happens", "beginning", "middle", "end", "conflict"],
            "audience": ["audience", "viewers", "people", "kids", "adults", "teens"],
            "duration": ["long", "short", "minutes", "seconds", "duration", "length"]
        }
        
        found_elements = []
        missing_elements = []
        
        for element, keywords in required_elements.items():
            if any(keyword.lower() in conversation_text.lower() for keyword in keywords):
                found_elements.append(element)
            else:
                missing_elements.append(element)
        
        # Consider complete if we have at least theme, characters, and some plot
        is_complete = len(found_elements) >= 4 and "theme" in found_elements and "characters" in found_elements
        
        return {
            "is_complete": is_complete,
            "found_elements": found_elements,
            "missing_elements": missing_elements
        }
    
    @handle_api_errors
    def ask_clarifying_questions(self, current_idea: Dict) -> str:
        """Generate clarifying questions for incomplete user input."""
        try:
            # Create a prompt to generate clarifying questions
            clarification_prompt = f"""Based on the current conversation about a video idea, generate ONE specific clarifying question to help gather missing information.

Current conversation summary:
{self.conversation_manager.get_conversation_summary()}

Current idea elements identified: {current_idea.get('found_elements', [])}
Missing elements: {current_idea.get('missing_elements', [])}

Generate a single, specific question that would help clarify the most important missing element. Be conversational and encouraging."""

            response = self.client.chat.completions.create(
                model=self.config.CHATBOT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that asks clarifying questions about video ideas."},
                    {"role": "user", "content": clarification_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating clarifying question: {str(e)}")
            # Fallback questions based on missing elements
            missing = current_idea.get('missing_elements', [])
            if 'theme' in missing:
                return "What's the main theme or concept of your video?"
            elif 'characters' in missing:
                return "Who are the main characters in your story?"
            elif 'plot' in missing:
                return "What happens in your story? Can you describe the main events?"
            else:
                return "Can you tell me more about your video idea?"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.conversation_manager.messages.copy()
    
    def reset_conversation(self) -> None:
        """Reset the conversation for a new session."""
        self.conversation_manager = ConversationManager()
    
    def get_conversation_context(self) -> Dict:
        """Get current conversation context."""
        return {
            "message_count": len(self.conversation_manager.messages),
            "context": self.conversation_manager.context,
            "last_analysis": self._analyze_idea_completeness()
        }