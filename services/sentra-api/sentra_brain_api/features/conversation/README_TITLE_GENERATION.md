# Auto-Generated Conversation Titles

This feature automatically generates meaningful titles for conversations based on the user's first message. It enhances the user experience by providing clear, descriptive titles that make it easier to navigate between multiple conversations.

## How It Works

### Trigger Conditions
- **When**: Triggered during conversation creation
- **Condition**: Only when no title is provided by the user AND the first message has content
- **Frequency**: Once per conversation (only for the first user message)

### Title Generation Process

1. **Primary Method**: LLM-based generation (when available)
   - Uses the existing LlamaServerClient for title generation
   - Employs a carefully crafted prompt for consistent, high-quality titles
   - Limits output to ~6 words for conciseness

2. **Fallback Method**: Heuristic-based generation
   - Removes common prefixes ("help me", "how do i", etc.)
   - Takes the first 6-8 meaningful words
   - Preserves question marks when appropriate
   - Always produces a result

### Title Quality Guidelines

Generated titles follow these principles:
- **Concise**: Under 6 words when possible
- **Descriptive**: Captures the essence of the request
- **Properly Capitalized**: Uses title case formatting
- **Clean**: Removes quotes and unnecessary punctuation

### Examples

| User Message | Generated Title |
|--------------|----------------|
| "How do I register a patent in Europe?" | "Register a Patent in Europe?" |
| "Help me write a business plan" | "Write a Business Plan" |
| "What is machine learning?" | "Machine Learning?" |
| "I need help with Python programming" | "Python Programming" |

## Integration Points

### Backend
- **Service**: `TitleGenerationService` handles all title generation logic
- **Integration**: `ConversationManagementService.create_conversation()` triggers title generation
- **Storage**: Updates both SQL (PostgreSQL) and NoSQL (MongoDB) records

### Frontend
- **Models**: Existing conversation models already support titles
- **API**: No changes needed - titles appear automatically in conversation lists
- **Updates**: Titles are available immediately after conversation creation

## Error Handling

The system is designed to be resilient:
- **LLM Failures**: Automatically falls back to heuristic generation
- **Generation Failures**: Conversation creation still succeeds
- **Empty Messages**: No title generation attempted
- **Existing Titles**: User-provided titles are never overwritten

## Configuration

The feature works out-of-the-box with existing infrastructure:
- Uses the same LLM client as the chat system
- Leverages existing conversation storage mechanisms
- No additional configuration required

## Testing

Comprehensive test coverage includes:
- **Unit Tests**: 13 tests for TitleGenerationService
- **Integration Tests**: 5 tests for conversation creation flow
- **Edge Cases**: Empty messages, long content, special characters
- **Error Scenarios**: LLM failures, invalid responses

## Performance Impact

- **Minimal**: Title generation uses heuristic approach by default (fast)
- **Non-blocking**: Conversation creation completes immediately
- **Efficient**: Reuses existing infrastructure and connections

## Future Enhancements

Potential improvements (not included in this implementation):
- LLM-based title generation with background processing
- Title regeneration via context menu
- Customizable title generation prompts
- Multiple language support for title generation