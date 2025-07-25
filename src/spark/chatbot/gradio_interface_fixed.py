"""
Fixed Gradio interface for interactive chatbot testing.
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


class ChatbotGradioInterfaceFixed:
    """Fixed Gradio web interface for interactive chatbot testing."""
    
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
            .status-indicator { padding: 8px 12px; border-radius: 6px; font-weight: bold; margin: 4px 0; }
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
                        type="messages",
                        show_copy_button=True
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            placeholder="Describe your video idea or continue the conversation...",
                            label="Your Message",
                            scale=4,
                            lines=1
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("Clear Chat", variant="secondary")
                        reset_btn = gr.Button("Reset Session", variant="stop")
                
                with gr.Column(scale=1):
                    # Status and Controls
                    gr.Markdown("## 📊 Session Status")
                    
                    status_display = gr.HTML(
                        value=self._get_status_html("incomplete", "Ready to start"),
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
            def send_message(message: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str, str, Dict, List]:
                """Handle sending a message to the chatbot."""
                if not message.strip():
                    return history, "", self._get_status_html("error", "Please enter a message"), {}, []
                
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
                        return history, "", status_html, {}, []
                    
                    # Update chat history with new message format for Gradio
                    new_history = history + [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": response_data.get("response", "No response")}
                    ]
                    
                    # Update status
                    is_complete = response_data.get("is_complete", False)
                    missing_elements = response_data.get("missing_elements", [])
                    
                    if is_complete:
                        status_html = self._get_status_html("complete", "Idea appears complete! Ready to structure.")
                    else:
                        status_html = self._get_status_html("incomplete", f"Gathering information... Missing: {', '.join(missing_elements)}")
                    
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
                    return history, message, error_html, {}, []
            
            def clear_chat() -> Tuple[List, str, str, Dict, List]:
                """Clear the chat display but keep the session."""
                return [], "", self._get_status_html("incomplete", "Chat cleared - session maintained"), {}, []
            
            def reset_session() -> Tuple[List, str, str, Dict, List, Dict, Dict, Dict]:
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
            
            def structure_idea() -> Tuple[Dict, str]:
                """Structure the current conversation into a UserIdea."""
                try:
                    conversation_history = self.chatbot_core.get_conversation_history()
                    if not conversation_history:
                        return (
                            {"error": "No conversation to structure"},
                            self._get_status_html("error", "No conversation found")
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
                        
                        return (idea_dict, status_html)
                    else:
                        return (
                            {"error": "Failed to structure idea"},
                            self._get_status_html("error", "Failed to structure idea")
                        )
                        
                except Exception as e:
                    logger.error(f"Error structuring idea: {str(e)}")
                    return (
                        {"error": str(e)},
                        self._get_status_html("error", f"Error: {str(e)}")
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
            
            def update_structure_button_state(completeness_data: Dict) -> gr.Button:
                """Update structure button based on conversation completeness."""
                is_complete = completeness_data.get("is_complete", False) if isinstance(completeness_data, dict) else False
                return gr.Button(interactive=is_complete)
            
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
                outputs=[user_idea_display, status_display]
            )
            
            generate_outline_btn.click(
                fn=generate_story_outline,
                outputs=[story_outline_display, status_display]
            )
            
            generate_characters_btn.click(
                fn=generate_character_profiles,
                outputs=[character_profiles_display, status_display]
            )
            
            # Update button states based on completeness
            completeness_display.change(
                fn=update_structure_button_state,
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
            "share": True,  # Use share=True to avoid localhost issues
            "debug": True,
            "show_error": True,
            "inbrowser": False
        }
        
        # Override with user parameters
        launch_params.update(kwargs)
        
        logger.info(f"Launching fixed Gradio interface...")
        interface.launch(**launch_params)


def create_chatbot_interface_fixed() -> ChatbotGradioInterfaceFixed:
    """Factory function to create a fixed chatbot interface."""
    return ChatbotGradioInterfaceFixed()


def launch_chatbot_interface_fixed(**kwargs) -> None:
    """Convenience function to launch the fixed chatbot interface."""
    interface = create_chatbot_interface_fixed()
    interface.launch(**kwargs)


if __name__ == "__main__":
    # Launch the interface when run directly
    launch_chatbot_interface_fixed()