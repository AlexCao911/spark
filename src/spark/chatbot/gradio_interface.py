"""
Gradio interface for interactive chatbot testing.
"""

import gradio as gr
import json
import logging
from typing import List, Tuple, Dict, Any, Optional
from .core import ChatbotCore
from .idea_structurer import IdeaStructurer
from .character_generator import CharacterProfileGenerator
from ..models import UserIdea, StoryOutline, CharacterProfile

logger = logging.getLogger(__name__)


class ChatbotGradioInterface:
    """Gradio web interface for interactive chatbot testing."""
    
    def __init__(self):
        self.chatbot_core = ChatbotCore()
        self.idea_structurer = IdeaStructurer()
        self.character_generator = CharacterProfileGenerator()
        self.current_session = None
        self.structured_output = None
        self.story_outline = None
        self.character_profiles = []
    
    def create_interface(self) -> gr.Blocks:
        """Create and configure the Gradio interface."""
        
        with gr.Blocks(
            title="Spark AI Chatbot Testing Interface",
            theme=gr.themes.Soft(),
            css="""
            .chat-container { max-height: 500px; overflow-y: auto; }
            .structured-output { background-color: #f8f9fa; padding: 15px; border-radius: 8px; }
            .json-display { font-family: monospace; white-space: pre-wrap; }
            .status-indicator { padding: 5px 10px; border-radius: 4px; font-weight: bold; }
            .status-complete { background-color: #d4edda; color: #155724; }
            .status-incomplete { background-color: #fff3cd; color: #856404; }
            .status-error { background-color: #f8d7da; color: #721c24; }
            """
        ) as interface:
            
            gr.Markdown("# 🎬 Spark AI Video Generation - Chatbot Testing Interface")
            gr.Markdown("Test the chatbot interaction, idea structuring, and character generation components.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Chat Interface
                    gr.Markdown("## 💬 Chat Interface")
                    
                    chatbot_display = gr.Chatbot(
                        label="Conversation",
                        height=400,
                        elem_classes=["chat-container"],
                        type="messages"
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            placeholder="Describe your video idea or continue the conversation...",
                            label="Your Message",
                            scale=4
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("Clear Chat", variant="secondary")
                        reset_btn = gr.Button("Reset Session", variant="stop")
                
                with gr.Column(scale=1):
                    # Status and Controls
                    gr.Markdown("## 📊 Session Status")
                    
                    status_display = gr.HTML(
                        value='<div class="status-indicator status-incomplete">Ready to start</div>',
                        label="Status"
                    )
                    
                    completeness_display = gr.JSON(
                        label="Idea Completeness Analysis",
                        value={"status": "No analysis yet"}
                    )
                    
                    # Action buttons
                    with gr.Column():
                        structure_btn = gr.Button(
                            "📝 Structure Current Idea",
                            variant="primary",
                            interactive=False
                        )
                        
                        generate_outline_btn = gr.Button(
                            "📖 Generate Story Outline",
                            variant="primary",
                            interactive=False
                        )
                        
                        generate_characters_btn = gr.Button(
                            "👥 Generate Character Profiles",
                            variant="primary",
                            interactive=False
                        )
            
            # Structured Output Display
            gr.Markdown("## 📋 Structured Output")
            
            with gr.Tabs():
                with gr.TabItem("User Idea JSON"):
                    user_idea_display = gr.JSON(
                        label="Structured User Idea",
                        value={"status": "No structured idea generated yet"}
                    )
                
                with gr.TabItem("Story Outline"):
                    story_outline_display = gr.JSON(
                        label="Generated Story Outline",
                        value={"status": "No story outline generated yet"}
                    )
                
                with gr.TabItem("Character Profiles"):
                    character_profiles_display = gr.JSON(
                        label="Generated Character Profiles",
                        value={"status": "No character profiles generated yet"}
                    )
                
                with gr.TabItem("Raw Conversation"):
                    conversation_display = gr.JSON(
                        label="Full Conversation History",
                        value=[]
                    )
            
            # Event handlers
            def send_message(message: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str, str, Dict, Dict]:
                """Handle sending a message to the chatbot."""
                if not message.strip():
                    return history, "", self._get_status_html("error", "Please enter a message"), {}, {}
                
                try:
                    # Determine if this is the first message or continuation
                    if not history:
                        # First message - engage user
                        response_data = self.chatbot_core.engage_user(message)
                    else:
                        # Continue conversation
                        response_data = self.chatbot_core.continue_conversation(message)
                    
                    if response_data.get("status") == "error":
                        status_html = self._get_status_html("error", f"Error: {response_data.get('error', 'Unknown error')}")
                        return history, "", status_html, {}, {}
                    
                    # Update chat history with new message format
                    new_history = history + [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": response_data.get("response", "No response")}
                    ]
                    
                    # Update status
                    is_complete = response_data.get("is_complete", False)
                    missing_elements = response_data.get("missing_elements", [])
                    
                    if is_complete:
                        status_html = self._get_status_html("complete", "Idea appears complete! Ready to structure.")
                        structure_interactive = True
                    else:
                        status_html = self._get_status_html("incomplete", f"Gathering information... Missing: {', '.join(missing_elements)}")
                        structure_interactive = False
                    
                    # Update completeness analysis
                    completeness_data = {
                        "is_complete": is_complete,
                        "missing_elements": missing_elements,
                        "message_count": len(new_history),
                        "last_response_status": response_data.get("status")
                    }
                    
                    # Update conversation display
                    conversation_data = self.chatbot_core.get_conversation_history()
                    
                    return (
                        new_history,
                        "",  # Clear input
                        status_html,
                        completeness_data,
                        conversation_data
                    )
                    
                except Exception as e:
                    logger.error(f"Error in send_message: {str(e)}")
                    error_html = self._get_status_html("error", f"Error: {str(e)}")
                    return history, message, error_html, {}, {}
            
            def clear_chat() -> Tuple[List, str, str, Dict, Dict]:
                """Clear the chat display but keep the session."""
                return [], "", self._get_status_html("incomplete", "Chat cleared - session maintained"), {}, {}
            
            def reset_session() -> Tuple[List, str, str, Dict, Dict, Dict, Dict, Dict]:
                """Reset the entire session."""
                self.chatbot_core.reset_conversation()
                self.structured_output = None
                self.story_outline = None
                self.character_profiles = []
                
                return (
                    [],  # chatbot_display
                    "",  # user_input
                    self._get_status_html("incomplete", "Session reset - ready to start"),  # status_display
                    {"status": "Session reset"},  # completeness_display
                    [],  # conversation_display
                    {"status": "No structured idea generated yet"},  # user_idea_display
                    {"status": "No story outline generated yet"},  # story_outline_display
                    {"status": "No character profiles generated yet"}  # character_profiles_display
                )
            
            def structure_idea() -> Tuple[Dict, str, bool, bool]:
                """Structure the current conversation into a UserIdea."""
                try:
                    conversation_history = self.chatbot_core.get_conversation_history()
                    if not conversation_history:
                        return (
                            {"error": "No conversation to structure"},
                            self._get_status_html("error", "No conversation found"),
                            False,
                            False
                        )
                    
                    # Structure the idea
                    user_idea = self.idea_structurer.structure_conversation(conversation_history)
                    if user_idea:
                        self.structured_output = user_idea
                        idea_dict = user_idea.model_dump()
                        
                        # Validate completeness
                        validation = self.idea_structurer.validate_idea_completeness(user_idea)
                        
                        status_html = self._get_status_html(
                            "complete" if validation["is_complete"] else "incomplete",
                            f"Idea structured! Completeness: {validation['completeness_score']:.1%}"
                        )
                        
                        return (
                            idea_dict,
                            status_html,
                            True,  # Enable story outline generation
                            True   # Enable character generation
                        )
                    else:
                        return (
                            {"error": "Failed to structure idea"},
                            self._get_status_html("error", "Failed to structure idea"),
                            False,
                            False
                        )
                        
                except Exception as e:
                    logger.error(f"Error structuring idea: {str(e)}")
                    return (
                        {"error": str(e)},
                        self._get_status_html("error", f"Error: {str(e)}"),
                        False,
                        False
                    )
            
            def generate_story_outline() -> Tuple[Dict, str]:
                """Generate a story outline from the structured idea."""
                try:
                    if not self.structured_output:
                        return (
                            {"error": "No structured idea available. Please structure the idea first."},
                            self._get_status_html("error", "No structured idea available")
                        )
                    
                    story_outline = self.idea_structurer.generate_story_outline(self.structured_output)
                    if story_outline:
                        self.story_outline = story_outline
                        outline_dict = story_outline.model_dump()
                        
                        status_html = self._get_status_html("complete", "Story outline generated successfully!")
                        return outline_dict, status_html
                    else:
                        return (
                            {"error": "Failed to generate story outline"},
                            self._get_status_html("error", "Failed to generate story outline")
                        )
                        
                except Exception as e:
                    logger.error(f"Error generating story outline: {str(e)}")
                    return (
                        {"error": str(e)},
                        self._get_status_html("error", f"Error: {str(e)}")
                    )
            
            def generate_character_profiles() -> Tuple[Dict, str]:
                """Generate character profiles from the structured idea."""
                try:
                    if not self.structured_output:
                        return (
                            {"error": "No structured idea available. Please structure the idea first."},
                            self._get_status_html("error", "No structured idea available")
                        )
                    
                    if not self.structured_output.basic_characters:
                        return (
                            {"error": "No characters found in the structured idea"},
                            self._get_status_html("error", "No characters found")
                        )
                    
                    character_profiles = self.character_generator.generate_complete_character_profiles(
                        self.structured_output.basic_characters,
                        self.structured_output
                    )
                    
                    if character_profiles:
                        self.character_profiles = character_profiles
                        profiles_dict = {
                            "character_count": len(character_profiles),
                            "characters": [profile.model_dump() for profile in character_profiles]
                        }
                        
                        status_html = self._get_status_html("complete", f"Generated {len(character_profiles)} character profiles!")
                        return profiles_dict, status_html
                    else:
                        return (
                            {"error": "Failed to generate character profiles"},
                            self._get_status_html("error", "Failed to generate character profiles")
                        )
                        
                except Exception as e:
                    logger.error(f"Error generating character profiles: {str(e)}")
                    return (
                        {"error": str(e)},
                        self._get_status_html("error", f"Error: {str(e)}")
                    )
            
            # Wire up event handlers
            send_btn.click(
                fn=send_message,
                inputs=[user_input, chatbot_display],
                outputs=[chatbot_display, user_input, status_display, completeness_display, conversation_display]
            )
            
            user_input.submit(
                fn=send_message,
                inputs=[user_input, chatbot_display],
                outputs=[chatbot_display, user_input, status_display, completeness_display, conversation_display]
            )
            
            clear_btn.click(
                fn=clear_chat,
                outputs=[chatbot_display, user_input, status_display, completeness_display, conversation_display]
            )
            
            reset_btn.click(
                fn=reset_session,
                outputs=[
                    chatbot_display, user_input, status_display, completeness_display,
                    conversation_display, user_idea_display, story_outline_display, character_profiles_display
                ]
            )
            
            structure_btn.click(
                fn=structure_idea,
                outputs=[user_idea_display, status_display, generate_outline_btn, generate_characters_btn]
            )
            
            generate_outline_btn.click(
                fn=generate_story_outline,
                outputs=[story_outline_display, status_display]
            )
            
            generate_characters_btn.click(
                fn=generate_character_profiles,
                outputs=[character_profiles_display, status_display]
            )
            
            # Update button interactivity based on conversation completeness
            def update_structure_button(completeness_data: Dict) -> bool:
                """Update structure button based on conversation completeness."""
                return completeness_data.get("is_complete", False)
            
            completeness_display.change(
                fn=update_structure_button,
                inputs=[completeness_display],
                outputs=[structure_btn]
            )
        
        return interface
    
    def _get_status_html(self, status_type: str, message: str) -> str:
        """Generate HTML for status display."""
        status_classes = {
            "complete": "status-complete",
            "incomplete": "status-incomplete",
            "error": "status-error"
        }
        
        status_class = status_classes.get(status_type, "status-incomplete")
        return f'<div class="status-indicator {status_class}">{message}</div>'
    
    def launch(self, **kwargs) -> None:
        """Launch the Gradio interface."""
        interface = self.create_interface()
        
        # Default launch parameters
        launch_params = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "debug": True,
            "show_error": True
        }
        
        # Override with user parameters
        launch_params.update(kwargs)
        
        logger.info(f"Launching Gradio interface on {launch_params['server_name']}:{launch_params['server_port']}")
        interface.launch(**launch_params)


def create_chatbot_interface() -> ChatbotGradioInterface:
    """Factory function to create a chatbot interface."""
    return ChatbotGradioInterface()


def launch_chatbot_interface(**kwargs) -> None:
    """Convenience function to launch the chatbot interface."""
    interface = create_chatbot_interface()
    interface.launch(**kwargs)


if __name__ == "__main__":
    # Launch the interface when run directly
    launch_chatbot_interface()