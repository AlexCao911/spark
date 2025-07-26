# Gradio Chatbot Testing Interface

This module provides a comprehensive Gradio web interface for testing and interacting with the Spark AI chatbot components.

## Features

### 🎯 Core Functionality
- **Interactive Chat Interface**: Real-time conversation with the AI chatbot
- **Message History**: Complete conversation tracking with structured display
- **Structured Output Display**: JSON visualization of extracted user ideas
- **Story Outline Generation**: Automated story outline creation from conversations
- **Character Profile Generation**: Complete character profiles with visual descriptions

### 📊 Testing & Analysis
- **Idea Completeness Analysis**: Real-time assessment of conversation completeness
- **Status Indicators**: Visual feedback on conversation and processing status
- **Raw Conversation Export**: Access to full conversation history for debugging
- **Error Handling**: Graceful error display and recovery

### 🔧 Development Tools
- **Session Management**: Reset and clear functionality for testing
- **Component Integration**: Tests all chatbot pipeline components together
- **Rapid Prototyping**: Quick iteration on chatbot behavior and responses

## Usage

### Quick Start

```python
from spark.chatbot.gradio_interface import launch_chatbot_interface

# Launch with default settings
launch_chatbot_interface()

# Launch with custom settings
launch_chatbot_interface(
    server_port=8080,
    share=True,  # Create public link
    debug=True
)
```

### Advanced Usage

```python
from spark.chatbot.gradio_interface import ChatbotGradioInterface

# Create interface instance
interface = ChatbotGradioInterface()

# Launch with custom configuration
interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    debug=True,
    show_error=True
)
```

### Testing Script

Run the included test script to launch the interface:

```bash
python test_gradio_interface.py
```

## Interface Components

### Chat Interface
- **Chatbot Display**: Shows conversation history in a clean, scrollable format
- **Message Input**: Text input for user messages with send button
- **Control Buttons**: Clear chat and reset session functionality

### Status Panel
- **Session Status**: Visual indicator of current conversation state
- **Completeness Analysis**: JSON display of idea completeness metrics
- **Action Buttons**: Structure idea, generate outline, and create character profiles

### Output Tabs
1. **User Idea JSON**: Structured representation of extracted user idea
2. **Story Outline**: Generated story outline with title, summary, and narrative
3. **Character Profiles**: Complete character profiles with descriptions
4. **Raw Conversation**: Full conversation history for debugging

## API Reference

### ChatbotGradioInterface

Main interface class that orchestrates all components.

#### Methods

- `create_interface() -> gr.Blocks`: Creates the Gradio interface
- `launch(**kwargs) -> None`: Launches the interface with specified parameters
- `_get_status_html(status_type: str, message: str) -> str`: Generates status HTML

#### Properties

- `chatbot_core`: Instance of ChatbotCore for conversation management
- `idea_structurer`: Instance of IdeaStructurer for idea extraction
- `character_generator`: Instance of CharacterProfileGenerator
- `structured_output`: Current structured UserIdea object
- `story_outline`: Generated StoryOutline object
- `character_profiles`: List of generated CharacterProfile objects

### Factory Functions

- `create_chatbot_interface() -> ChatbotGradioInterface`: Creates interface instance
- `launch_chatbot_interface(**kwargs) -> None`: Convenience function to launch interface

## Configuration

The interface uses the same configuration as the main chatbot components:

- **API Keys**: Set via environment variables or config files
- **Model Settings**: Configured through the main config system
- **Retry Logic**: Uses the same error handling and retry mechanisms

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
python -m pytest tests/test_gradio_interface.py -v
```

### Simple Tests

Run basic functionality tests:

```bash
python test_interface_simple.py
```

### Manual Testing

1. Launch the interface
2. Start a conversation about a video idea
3. Watch the completeness analysis update
4. Use the "Structure Current Idea" button when ready
5. Generate story outline and character profiles
6. Review all outputs in the tabs

## Workflow

### Typical Testing Session

1. **Start Conversation**: Enter initial video idea
2. **Iterate**: Continue conversation until idea is complete
3. **Structure**: Click "Structure Current Idea" to extract structured data
4. **Generate Content**: Create story outline and character profiles
5. **Review**: Examine all outputs in the respective tabs
6. **Reset**: Clear session and start over for new tests

### Status Indicators

- 🟢 **Complete**: Idea is ready for structuring
- 🟡 **Incomplete**: Still gathering information
- 🔴 **Error**: Something went wrong, check error message

## Troubleshooting

### Common Issues

1. **Interface won't start**: Check that all dependencies are installed
2. **API errors**: Verify API keys and endpoint configuration
3. **Slow responses**: Check network connection and API rate limits
4. **Empty outputs**: Ensure conversation has enough content before structuring

### Debug Mode

Enable debug mode for detailed error information:

```python
launch_chatbot_interface(debug=True, show_error=True)
```

### Logging

The interface uses Python logging. Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Extending the Interface

To add new functionality:

1. Add new Gradio components in `create_interface()`
2. Create corresponding event handlers
3. Wire up the components with `.click()` or `.change()` events
4. Update the return types and outputs accordingly

### Custom Styling

Modify the CSS in the `create_interface()` method:

```python
css = """
.custom-class { 
    /* Your custom styles */ 
}
"""
```

### Integration with Other Components

The interface is designed to work with:
- `ChatbotCore`: Main conversation logic
- `IdeaStructurer`: Conversation to structured data conversion
- `CharacterProfileGenerator`: Character profile creation
- All data models from `spark.models`

## Performance Considerations

- **Memory Usage**: Interface keeps conversation history in memory
- **API Calls**: Each message triggers API calls to the language model
- **Concurrent Users**: Single instance supports one conversation at a time
- **Session Management**: Use reset functionality to clear memory

## Security Notes

- **API Keys**: Never expose API keys in the interface
- **User Input**: All user input is sanitized before processing
- **Error Messages**: Sensitive information is filtered from error displays
- **Network**: Consider firewall rules when exposing the interface

## Future Enhancements

Potential improvements:
- Multi-user support with session isolation
- Conversation export/import functionality
- Advanced analytics and metrics
- Integration with video generation pipeline
- Real-time collaboration features