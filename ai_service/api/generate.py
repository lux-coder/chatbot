"""
Generation API Module

This module provides the main API endpoints for text generation with
integrated PII protection.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from ..models.openai import OpenAIModel
from ..models.llama import LlamaModel
from ..security.pii_handler import PIIHandler
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerationRequest(BaseModel):
    """Request model for text generation"""
    message: str = Field(..., description="The user's message")
    context: List[Dict[str, Any]] = Field(default_factory=list, description="Previous conversation context")
    model_type: str = Field(default="openai", description="Model to use (openai/llama)")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, description="Temperature for generation")

class GenerationResponse(BaseModel):
    """Response model for text generation"""
    content: str = Field(..., description="Generated response")
    model_used: str = Field(..., description="Model that generated the response")
    tokens_used: int = Field(..., description="Number of tokens used")

async def get_pii_handler() -> PIIHandler:
    """Dependency for PII handler"""
    return PIIHandler(enable_logging=True)

async def get_model(model_type: str):
    """Get the appropriate model based on type"""
    if model_type == "openai":
        return OpenAIModel()
    elif model_type == "llama":
        return LlamaModel()
    raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")

@router.post("/generate", response_model=GenerationResponse)
async def generate_response(
    request: GenerationRequest,
    pii_handler: PIIHandler = Depends(get_pii_handler),
    model: Any = Depends(get_model)
) -> GenerationResponse:
    """
    Generate a response to user input with PII protection.
    
    Args:
        request: Generation request containing message and context
        pii_handler: PII detection and masking handler
        model: AI model to use for generation
        
    Returns:
        Generated response with PII protection
    """
    try:
        # Process user message to remove PII
        cleaned_message = pii_handler.process_text(request.message)
        
        # Process context messages
        cleaned_context = []
        for msg in request.context:
            if isinstance(msg.get("content"), str):
                msg = msg.copy()
                msg["content"] = pii_handler.process_text(msg["content"])
            cleaned_context.append(msg)
        
        # Generate response
        response = await model.generate(
            message=cleaned_message,
            context=cleaned_context,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Process response to ensure no PII was generated
        cleaned_response = pii_handler.process_text(response.content)
        
        return GenerationResponse(
            content=cleaned_response,
            model_used=response.model_used,
            tokens_used=response.tokens_used
        )
        
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate response"
        ) 