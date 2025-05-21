"""
OpenAI Model Implementation

This module implements the OpenAI model integration for the AI service.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class OpenAIConfig(BaseModel):
    """Configuration for OpenAI model"""
    model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=1000)
    temperature: float = Field(default=0.7)
    timeout: float = Field(default=30.0)

class OpenAIModel:
    """
    Implementation of the OpenAI model integration.
    
    This class handles communication with the OpenAI API for generating
    responses to user messages.
    """
    
    def __init__(self):
        """Initialize the OpenAI model"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY environment variable not set")
            
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=OpenAIConfig().timeout
        )
        self.config = OpenAIConfig()
    
    async def generate(
        self,
        message: str,
        context: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using the OpenAI API.
        
        Args:
            message: The user's message
            context: Previous conversation messages formatted as [{role: "user"|"assistant", content: str}]
            max_tokens: Maximum tokens to generate (optional)
            temperature: Temperature parameter (optional)
            
        Returns:
            Dictionary containing response content, model used, and tokens used
            
        Raises:
            Exception: If OpenAI API call fails
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
            
        # Convert our context format to OpenAI's expected format if needed
        messages = self._format_messages(context, message)
        
        # Set optional parameters or use defaults
        actual_max_tokens = max_tokens or self.config.max_tokens
        actual_temperature = temperature or self.config.temperature
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=actual_max_tokens,
                temperature=actual_temperature
            )
            
            # Extract the response content and usage information
            content = response.choices[0].message.content
            model_used = response.model
            tokens_used = response.usage.total_tokens
            
            logger.info(
                f"OpenAI response generated successfully: {tokens_used} tokens used"
            )
            
            return {
                "content": content,
                "model_used": model_used,
                "tokens_used": tokens_used
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _format_messages(
        self,
        context: List[Dict[str, Any]],
        current_message: str
    ) -> List[Dict[str, str]]:
        """
        Format the conversation context and current message into OpenAI's expected format.
        
        Args:
            context: Previous conversation context
            current_message: The current user message
            
        Returns:
            List of messages in OpenAI's format
        """
        # Initialize with a system message if needed
        formatted_messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # Add context messages in the right format
        if context:
            for msg in context:
                role = "assistant" if msg.get("is_bot", False) else "user"
                formatted_messages.append(
                    {"role": role, "content": msg.get("content", "")}
                )
        
        # Add the current message
        formatted_messages.append({"role": "user", "content": current_message})
        
        return formatted_messages 