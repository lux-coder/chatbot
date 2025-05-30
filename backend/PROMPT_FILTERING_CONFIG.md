# Prompt Filtering Configuration Guide

This document explains how to configure the prompt filtering system that was added to your chatbot backend.

## Overview

The prompt filtering system provides two layers of protection:

1. **Regex-based filtering**: Configurable patterns to block or sanitize content
2. **OpenAI Moderation API**: Real-time content moderation using OpenAI's moderation endpoint

## Environment Variables

Add these variables to your `.env` file:

```bash
# OpenAI Moderation API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODERATION_ENABLED=true
OPENAI_MODERATION_TIMEOUT=10.0

# Prompt Filtering Configuration
PROMPT_FILTER_ENABLED=true
PROMPT_FILTER_CONFIG_PATH=app/core/config/prompt_filters.json
PROMPT_FILTER_STRICT_MODE=true
```

### Configuration Explanations

- **OPENAI_API_KEY**: Your OpenAI API key for accessing the moderation endpoint
- **OPENAI_MODERATION_ENABLED**: Whether to enable OpenAI moderation checks (true/false)
- **OPENAI_MODERATION_TIMEOUT**: Timeout in seconds for moderation API calls
- **PROMPT_FILTER_ENABLED**: Master switch for all prompt filtering (true/false)
- **PROMPT_FILTER_CONFIG_PATH**: Path to the regex patterns configuration file
- **PROMPT_FILTER_STRICT_MODE**: If true, blocks prompts when moderation API fails; if false, allows them

## Regex Patterns Configuration

The regex patterns are configured in `backend/app/core/config/prompt_filters.json`. This file contains:

### Filter Structure

Each filter has the following properties:

```json
{
  "name": "filter_name",
  "pattern": "regex_pattern",
  "action": "block|sanitize",
  "message": "User-facing message",
  "replacement": "replacement_text" // only for sanitize action
}
```

### Available Actions

- **block**: Completely blocks the message and returns an error message
- **sanitize**: Replaces matching content with a replacement string

### Current Filters

The system includes these pre-configured filters:

1. **sql_injection**: Blocks SQL injection attempts
2. **script_injection**: Blocks JavaScript/script injection
3. **profanity_basic**: Sanitizes basic profanity
4. **hate_speech**: Blocks hate speech
5. **personal_info_patterns**: Blocks patterns that look like sensitive data
6. **excessive_profanity**: Blocks excessive profanity
7. **spam_patterns**: Blocks spam-like content
8. **prompt_injection**: Blocks prompt manipulation attempts

## How It Works

When a user sends a message:

1. **Length Check**: Ensures message isn't too long
2. **Regex Filtering**: Applies all regex patterns
   - If any "block" filter matches → message blocked
   - If "sanitize" filters match → content is cleaned
3. **OpenAI Moderation**: Checks sanitized content with OpenAI
   - If flagged → message blocked
4. **PII Detection**: Existing PII masking (unchanged)
5. **AI Processing**: Send to LLM if all checks pass

## Customizing Filters

### Adding New Patterns

Edit `backend/app/core/config/prompt_filters.json`:

```json
{
  "regex_filters": [
    {
      "name": "custom_filter",
      "pattern": "(?i)your_pattern_here",
      "action": "block",
      "message": "🚫 Your custom message here."
    }
  ]
}
```

### Pattern Tips

- Use `(?i)` at the start for case-insensitive matching
- Use `\\b` for word boundaries
- Escape special regex characters: `( ) [ ] { } + * ? ^ $ | . \`
- Test patterns carefully to avoid false positives

### Reloading Configuration

The service automatically loads configuration at startup. To reload without restart, you can call the `reload_config()` method on the PromptFilterService.

## API Responses

### Blocked Messages

When a message is blocked, the API returns:

```json
{
  "message_id": "uuid",
  "conversation_id": "uuid", 
  "content": "🚫 Your input was flagged as inappropriate.",
  "role": "system",
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "filter_block": true
  }
}
```

### Sanitized Messages

When content is sanitized, the response includes a warning:

```json
{
  "message_id": "uuid",
  "conversation_id": "uuid",
  "content": "AI response here",
  "role": "assistant", 
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "sanitization_warning": "⚠️ Your message contained inappropriate language that has been filtered."
  }
}
```

## Monitoring and Logging

The system logs all filtering events:

- `PROMPT_BLOCKED_REGEX`: Message blocked by regex filter
- `PROMPT_BLOCKED_MODERATION`: Message blocked by OpenAI moderation
- `PROMPT_SANITIZED`: Message content was sanitized
- `PROMPT_FILTER_ERROR`: Error in filtering process

## Security Considerations

1. **API Key Security**: Keep your OpenAI API key secure
2. **Strict Mode**: Consider enabling strict mode in production
3. **Log Review**: Regularly review filtering logs for effectiveness
4. **Pattern Updates**: Keep regex patterns updated for new threats
5. **False Positives**: Monitor for legitimate content being blocked

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Check API key and network connectivity
2. **Regex Errors**: Validate regex patterns before deploying
3. **Performance**: Too many complex patterns may slow response time
4. **False Positives**: Overly broad patterns may block legitimate content

### Testing Filters

You can test individual patterns using Python:

```python
import re

pattern = r"(?i)your_pattern"
test_text = "your test message"
match = re.search(pattern, test_text)
print(f"Match found: {bool(match)}")
```

## Cost Considerations

- OpenAI Moderation API calls cost money
- Consider disabling for development/testing
- Monitor usage in production
- Each message is one API call

## Disabling Filtering

To disable filtering temporarily:

```bash
PROMPT_FILTER_ENABLED=false
```

To disable only OpenAI moderation:

```bash
OPENAI_MODERATION_ENABLED=false
``` 