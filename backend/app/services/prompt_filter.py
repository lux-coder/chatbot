"""
Prompt Filter Service Module

This module provides comprehensive prompt filtering functionality including:
- Regex-based pattern filtering (configurable via JSON)
- OpenAI Moderation API integration
- Configurable actions (block/sanitize)
- Graceful error handling
"""

import json
import re
import os
import time
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel
import httpx
import logging
import structlog
from enum import Enum

from app.core.config import Settings
from app.core.monitoring import log_security_event

# Configure structured logger for this module
logger = structlog.get_logger(__name__)

class FilterAction(str, Enum):
    """Available filter actions"""
    BLOCK = "block"
    SANITIZE = "sanitize"
    ALLOW = "allow"

class FilterResult(BaseModel):
    """Result of prompt filtering"""
    is_allowed: bool
    action: FilterAction
    filtered_content: Optional[str] = None
    message: Optional[str] = None
    triggered_filters: List[str] = []
    moderation_flagged: bool = False
    moderation_categories: List[str] = []

class RegexFilter(BaseModel):
    """Configuration for a regex filter"""
    name: str
    pattern: str
    action: FilterAction
    message: str
    replacement: Optional[str] = None

class FilterConfig(BaseModel):
    """Configuration for all filters"""
    regex_filters: List[RegexFilter]
    settings: Dict[str, Any]

class OpenAIModerationResult(BaseModel):
    """Result from OpenAI Moderation API"""
    flagged: bool
    categories: Dict[str, bool]
    category_scores: Dict[str, float]

class PromptFilterService:
    """
    Service for filtering prompts using regex patterns and OpenAI moderation.
    
    This service provides:
    - Configurable regex-based filtering
    - OpenAI Moderation API integration
    - Multiple action types (block, sanitize)
    - Comprehensive logging and monitoring
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the prompt filter service.
        
        Args:
            settings: Application settings containing filter configuration
        """
        self.settings = settings
        self.openai_client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=settings.OPENAI_MODERATION_TIMEOUT
        )
        
        # Load filter configuration
        self.filter_config = self._load_filter_config()
        self.compiled_patterns = self._compile_regex_patterns()
        
        # Log service initialization
        logger.info(
            "prompt_filter_service_initialized",
            filter_enabled=settings.PROMPT_FILTER_ENABLED,
            moderation_enabled=settings.OPENAI_MODERATION_ENABLED,
            strict_mode=settings.PROMPT_FILTER_STRICT_MODE,
            total_regex_filters=len(self.compiled_patterns),
            config_path=settings.PROMPT_FILTER_CONFIG_PATH
        )
        
    def _load_filter_config(self) -> FilterConfig:
        """
        Load filter configuration from JSON file.
        
        Returns:
            FilterConfig object containing all filter rules
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        config_path = self.settings.PROMPT_FILTER_CONFIG_PATH
        
        # Handle relative paths from app root
        if not os.path.isabs(config_path):
            # Get the directory where this module is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to app directory and then to the config path
            app_dir = os.path.dirname(os.path.dirname(current_dir))
            config_path = os.path.join(app_dir, config_path)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            config = FilterConfig(**config_data)
            
            logger.info(
                "filter_config_loaded",
                config_path=config_path,
                regex_filters_count=len(config.regex_filters),
                settings=config.settings
            )
            
            return config
            
        except FileNotFoundError:
            logger.error(
                "filter_config_file_not_found",
                config_path=config_path
            )
            # Return empty config to allow service to continue
            return FilterConfig(regex_filters=[], settings={})
            
        except json.JSONDecodeError as e:
            logger.error(
                "filter_config_invalid_json",
                config_path=config_path,
                error=str(e)
            )
            return FilterConfig(regex_filters=[], settings={})
            
        except Exception as e:
            logger.error(
                "filter_config_load_error",
                config_path=config_path,
                error=str(e),
                error_type=type(e).__name__
            )
            return FilterConfig(regex_filters=[], settings={})
    
    def _compile_regex_patterns(self) -> Dict[str, Tuple[re.Pattern, RegexFilter]]:
        """
        Compile regex patterns for better performance.
        
        Returns:
            Dictionary mapping filter names to compiled patterns and filter configs
        """
        compiled = {}
        compilation_errors = []
        
        for filter_rule in self.filter_config.regex_filters:
            try:
                flags = 0
                if not self.filter_config.settings.get("case_sensitive", False):
                    flags |= re.IGNORECASE
                    
                pattern = re.compile(filter_rule.pattern, flags)
                compiled[filter_rule.name] = (pattern, filter_rule)
                
                logger.debug(
                    "regex_pattern_compiled",
                    filter_name=filter_rule.name,
                    action=filter_rule.action,
                    pattern_length=len(filter_rule.pattern)
                )
                
            except re.error as e:
                error_info = {
                    "filter_name": filter_rule.name,
                    "pattern": filter_rule.pattern,
                    "error": str(e)
                }
                compilation_errors.append(error_info)
                logger.error(
                    "regex_pattern_compilation_failed",
                    **error_info
                )
                continue
        
        logger.info(
            "regex_patterns_compilation_complete",
            total_filters=len(self.filter_config.regex_filters),
            successful_compilations=len(compiled),
            failed_compilations=len(compilation_errors),
            compilation_errors=compilation_errors if compilation_errors else None
        )
                
        return compiled
    
    async def _check_openai_moderation(self, content: str) -> OpenAIModerationResult:
        """
        Check content using OpenAI Moderation API.
        
        Args:
            content: Text content to check
            
        Returns:
            OpenAIModerationResult containing moderation results
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        if not self.settings.OPENAI_API_KEY:
            logger.warning(
                "openai_moderation_skipped",
                reason="api_key_not_configured"
            )
            return OpenAIModerationResult(
                flagged=False,
                categories={},
                category_scores={}
            )
        
        start_time = time.time()
        
        try:
            logger.debug(
                "openai_moderation_request_start",
                content_length=len(content),
                timeout=self.settings.OPENAI_MODERATION_TIMEOUT
            )
            
            response = await self.openai_client.post(
                "/moderations",
                json={"input": content}
            )
            response.raise_for_status()
            
            data = response.json()
            result = data["results"][0]
            
            response_time = time.time() - start_time
            
            moderation_result = OpenAIModerationResult(
                flagged=result["flagged"],
                categories=result["categories"],
                category_scores=result["category_scores"]
            )
            
            # Log detailed moderation result
            flagged_categories = [
                category for category, flagged 
                in result["categories"].items() 
                if flagged
            ]
            
            logger.info(
                "openai_moderation_completed",
                flagged=result["flagged"],
                flagged_categories=flagged_categories,
                category_scores=result["category_scores"],
                response_time_ms=round(response_time * 1000, 2),
                content_length=len(content)
            )
            
            return moderation_result
            
        except httpx.HTTPError as e:
            response_time = time.time() - start_time
            
            logger.error(
                "openai_moderation_http_error",
                error=str(e),
                status_code=getattr(e.response, 'status_code', None),
                response_time_ms=round(response_time * 1000, 2),
                strict_mode=self.settings.PROMPT_FILTER_STRICT_MODE
            )
            
            # In strict mode, treat API errors as violations
            if self.settings.PROMPT_FILTER_STRICT_MODE:
                return OpenAIModerationResult(
                    flagged=True,
                    categories={"api_error": True},
                    category_scores={"api_error": 1.0}
                )
            else:
                # In non-strict mode, allow content if API fails
                return OpenAIModerationResult(
                    flagged=False,
                    categories={},
                    category_scores={}
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            
            logger.error(
                "openai_moderation_unexpected_error",
                error=str(e),
                error_type=type(e).__name__,
                response_time_ms=round(response_time * 1000, 2),
                strict_mode=self.settings.PROMPT_FILTER_STRICT_MODE
            )
            
            # Same strict mode logic for unexpected errors
            if self.settings.PROMPT_FILTER_STRICT_MODE:
                return OpenAIModerationResult(
                    flagged=True,
                    categories={"system_error": True},
                    category_scores={"system_error": 1.0}
                )
            else:
                return OpenAIModerationResult(
                    flagged=False,
                    categories={},
                    category_scores={}
                )
    
    def _apply_regex_filters(self, content: str) -> FilterResult:
        """
        Apply regex filters to content.
        
        Args:
            content: Text content to filter
            
        Returns:
            FilterResult indicating filtering outcome
        """
        start_time = time.time()
        triggered_filters = []
        filtered_content = content
        block_messages = []
        sanitize_messages = []
        
        logger.debug(
            "regex_filtering_start",
            content_length=len(content),
            total_patterns=len(self.compiled_patterns)
        )
        
        for filter_name, (pattern, filter_rule) in self.compiled_patterns.items():
            if pattern.search(content):
                triggered_filters.append(filter_name)
                
                logger.info(
                    "regex_filter_triggered",
                    filter_name=filter_name,
                    action=filter_rule.action,
                    content_length=len(content)
                )
                
                if filter_rule.action == FilterAction.BLOCK:
                    processing_time = time.time() - start_time
                    
                    logger.warning(
                        "content_blocked_by_regex",
                        filter_name=filter_name,
                        message=filter_rule.message,
                        processing_time_ms=round(processing_time * 1000, 2),
                        triggered_filters=triggered_filters
                    )
                    
                    # Block immediately on first blocking filter
                    return FilterResult(
                        is_allowed=False,
                        action=FilterAction.BLOCK,
                        message=filter_rule.message,
                        triggered_filters=triggered_filters
                    )
                    
                elif filter_rule.action == FilterAction.SANITIZE:
                    # Apply sanitization
                    replacement = filter_rule.replacement or "***"
                    original_content = filtered_content
                    filtered_content = pattern.sub(replacement, filtered_content)
                    sanitize_messages.append(filter_rule.message)
                    
                    logger.info(
                        "content_sanitized_by_regex",
                        filter_name=filter_name,
                        replacement=replacement,
                        original_length=len(original_content),
                        filtered_length=len(filtered_content)
                    )
        
        processing_time = time.time() - start_time
        
        # If we get here, no blocking filters were triggered
        if triggered_filters:
            # Some sanitization occurred
            message = sanitize_messages[0] if sanitize_messages else None
            
            logger.info(
                "regex_filtering_completed_with_sanitization",
                triggered_filters=triggered_filters,
                original_length=len(content),
                filtered_length=len(filtered_content),
                processing_time_ms=round(processing_time * 1000, 2)
            )
            
            return FilterResult(
                is_allowed=True,
                action=FilterAction.SANITIZE,
                filtered_content=filtered_content,
                message=message,
                triggered_filters=triggered_filters
            )
        else:
            # No filters triggered
            logger.debug(
                "regex_filtering_completed_no_matches",
                content_length=len(content),
                processing_time_ms=round(processing_time * 1000, 2)
            )
            
            return FilterResult(
                is_allowed=True,
                action=FilterAction.ALLOW,
                filtered_content=filtered_content,
                triggered_filters=[]
            )
    
    async def filter_prompt(
        self,
        content: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> FilterResult:
        """
        Apply all filters to a prompt.
        
        Args:
            content: The prompt content to filter
            user_id: Optional user ID for logging
            tenant_id: Optional tenant ID for logging
            
        Returns:
            FilterResult containing the filtering outcome
        """
        start_time = time.time()
        
        logger.info(
            "prompt_filtering_start",
            user_id=user_id,
            tenant_id=tenant_id,
            content_length=len(content),
            filter_enabled=self.settings.PROMPT_FILTER_ENABLED,
            moderation_enabled=self.settings.OPENAI_MODERATION_ENABLED
        )
        
        if not self.settings.PROMPT_FILTER_ENABLED:
            logger.info(
                "prompt_filtering_disabled",
                user_id=user_id,
                tenant_id=tenant_id
            )
            return FilterResult(
                is_allowed=True,
                action=FilterAction.ALLOW,
                filtered_content=content
            )
        
        try:
            # Check message length
            max_length = self.filter_config.settings.get("max_message_length", 4096)
            if len(content) > max_length:
                logger.warning(
                    "prompt_length_exceeded",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    content_length=len(content),
                    max_length=max_length
                )
                
                await log_security_event(
                    event_type="PROMPT_LENGTH_EXCEEDED",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    details={
                        "content_length": len(content),
                        "max_length": max_length
                    }
                )
                return FilterResult(
                    is_allowed=False,
                    action=FilterAction.BLOCK,
                    message=f"🚫 Your message is too long. Maximum length is {max_length} characters."
                )
            
            # Apply regex filters first
            regex_result = self._apply_regex_filters(content)
            
            if not regex_result.is_allowed:
                total_time = time.time() - start_time
                
                logger.warning(
                    "prompt_blocked_by_regex_filter",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    triggered_filters=regex_result.triggered_filters,
                    action=regex_result.action,
                    total_processing_time_ms=round(total_time * 1000, 2)
                )
                
                # Log blocked content (without the actual content for security)
                await log_security_event(
                    event_type="PROMPT_BLOCKED_REGEX",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    details={
                        "triggered_filters": regex_result.triggered_filters,
                        "action": regex_result.action
                    }
                )
                return regex_result
            
            # Use filtered content for moderation check
            content_to_check = regex_result.filtered_content or content
            
            # Check with OpenAI moderation if enabled
            moderation_result = None
            if self.settings.OPENAI_MODERATION_ENABLED:
                moderation_result = await self._check_openai_moderation(content_to_check)
                
                if moderation_result.flagged:
                    total_time = time.time() - start_time
                    flagged_categories = [
                        category for category, flagged 
                        in moderation_result.categories.items() 
                        if flagged
                    ]
                    
                    logger.warning(
                        "prompt_blocked_by_moderation",
                        user_id=user_id,
                        tenant_id=tenant_id,
                        flagged_categories=flagged_categories,
                        category_scores=moderation_result.category_scores,
                        total_processing_time_ms=round(total_time * 1000, 2)
                    )
                    
                    await log_security_event(
                        event_type="PROMPT_BLOCKED_MODERATION",
                        user_id=user_id,
                        tenant_id=tenant_id,
                        details={
                            "flagged_categories": flagged_categories
                        }
                    )
                    
                    return FilterResult(
                        is_allowed=False,
                        action=FilterAction.BLOCK,
                        message="🚫 Your input was flagged as inappropriate by our moderation system.",
                        triggered_filters=regex_result.triggered_filters,
                        moderation_flagged=True,
                        moderation_categories=flagged_categories
                    )
            
            # If we get here, content passed all checks
            total_time = time.time() - start_time
            
            final_result = FilterResult(
                is_allowed=True,
                action=regex_result.action,
                filtered_content=regex_result.filtered_content,
                message=regex_result.message,
                triggered_filters=regex_result.triggered_filters,
                moderation_flagged=False,
                moderation_categories=[]
            )
            
            # Log successful filtering if any filters were applied
            if regex_result.triggered_filters:
                logger.info(
                    "prompt_sanitized_successfully",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    triggered_filters=regex_result.triggered_filters,
                    action=regex_result.action,
                    total_processing_time_ms=round(total_time * 1000, 2)
                )
                
                await log_security_event(
                    event_type="PROMPT_SANITIZED",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    details={
                        "triggered_filters": regex_result.triggered_filters,
                        "action": regex_result.action
                    }
                )
            else:
                logger.debug(
                    "prompt_passed_all_filters",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    total_processing_time_ms=round(total_time * 1000, 2)
                )
            
            return final_result
            
        except Exception as e:
            total_time = time.time() - start_time
            
            logger.error(
                "prompt_filtering_error",
                user_id=user_id,
                tenant_id=tenant_id,
                error=str(e),
                error_type=type(e).__name__,
                total_processing_time_ms=round(total_time * 1000, 2),
                strict_mode=self.settings.PROMPT_FILTER_STRICT_MODE
            )
            
            # Log the error
            await log_security_event(
                event_type="PROMPT_FILTER_ERROR",
                user_id=user_id,
                tenant_id=tenant_id,
                details={
                    "error": str(e)
                },
                severity="ERROR"
            )
            
            # In strict mode, block on errors; otherwise allow
            if self.settings.PROMPT_FILTER_STRICT_MODE:
                return FilterResult(
                    is_allowed=False,
                    action=FilterAction.BLOCK,
                    message="🚫 An error occurred while checking your input. Please try again."
                )
            else:
                return FilterResult(
                    is_allowed=True,
                    action=FilterAction.ALLOW,
                    filtered_content=content
                )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        logger.info("prompt_filter_service_shutdown")
        await self.openai_client.aclose()
    
    async def reload_config(self) -> bool:
        """
        Reload the filter configuration from file.
        
        Returns:
            True if reload was successful, False otherwise
        """
        logger.info("prompt_filter_config_reload_start")
        
        try:
            new_config = self._load_filter_config()
            new_patterns = self._compile_regex_patterns()
            
            old_pattern_count = len(self.compiled_patterns)
            
            self.filter_config = new_config
            self.compiled_patterns = new_patterns
            
            logger.info(
                "prompt_filter_config_reloaded_successfully",
                old_pattern_count=old_pattern_count,
                new_pattern_count=len(new_patterns),
                config_path=self.settings.PROMPT_FILTER_CONFIG_PATH
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "prompt_filter_config_reload_failed",
                error=str(e),
                error_type=type(e).__name__,
                config_path=self.settings.PROMPT_FILTER_CONFIG_PATH
            )
            return False 