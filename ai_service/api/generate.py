"""
Generation API Module

This module provides the main API endpoints for text generation with
integrated PII protection.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, ValidationError
from models.openai import OpenAIModel
from models.llama import LlamaModel
from security.pii_handler import PIIHandler
import logging
from fastapi.responses import JSONResponse

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

async def get_pii_handler():
    """Get PII handler with dependency injection"""
    return PIIHandler()

def get_model_instance(model_type: str):
    """Get the appropriate model based on type"""
    if model_type == "openai":
        return OpenAIModel()
    elif model_type == "llama":
        return LlamaModel()
    raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")

@router.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    pii_handler=Depends(get_pii_handler)
):
    """
    Generate text response based on user message and conversation context.
    
    This endpoint:
    1. Detects and masks PII in the user message
    2. Passes the cleaned message to the selected AI model
    3. Returns the model's response
    
    Args:
        request: The generation request containing message, context, and model preferences
        pii_handler: The PII detection and masking handler
        
    Returns:
        GenerationResponse containing the model's response
        
    Raises:
        HTTPException: If model generation fails or parameters are invalid
    """
    try:
        logger.info(f"Received request: {request.dict()}")
        # Log the request (without PII)
        logger.info(
            f"Generation request received",
            extra={
                "model_type": request.model_type,
                "context_length": len(request.context),
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
        )
        
        # Get the appropriate model
        model = get_model_instance(request.model_type)
        
        # Process PII in the message
        masked_message = await pii_handler.process_text(request.message)
        
        # Call the appropriate model
        model_response = await model.generate(
            message=masked_message,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Format the response
        response = GenerationResponse(
            content=model_response["content"],
            model_used=model_response["model_used"],
            tokens_used=model_response["tokens_used"]
        )
        
        # Log response info (without actual content)
        logger.info(
            f"Generation response sent",
            extra={
                "model_used": response.model_used,
                "tokens_used": response.tokens_used
            }
        )
        
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        raise
    except Exception as e:
        logger.error(f"Error in generation request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during text generation")
