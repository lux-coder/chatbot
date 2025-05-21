"""
PII Handler Module

This module provides functionality for detecting and masking personally
identifiable information (PII) in text data.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class PIIDetector:
    """
    Detector for various types of PII in text.
    
    This class provides methods to detect common PII patterns like:
    - Email addresses
    - Phone numbers
    - Social security numbers
    - Credit card numbers
    - IP addresses
    - Names (requires NLP)
    """
    
    def __init__(self):
        """Initialize the PII detector"""
        # Compile regex patterns for efficiency
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.credit_card_pattern = re.compile(r'\b(?:\d{4}[- ]?){3}\d{4}\b')
        self.ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
    
    async def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect all PII in the provided text.
        
        Args:
            text: The text to scan for PII
            
        Returns:
            List of PII matches with type, span, and value
        """
        if not text:
            return []
            
        # Collect all PII matches
        all_matches = []
        
        # Detect emails
        for match in self.email_pattern.finditer(text):
            all_matches.append({
                "type": "email",
                "span": (match.start(), match.end()),
                "value": match.group()
            })
        
        # Detect phone numbers
        for match in self.phone_pattern.finditer(text):
            all_matches.append({
                "type": "phone",
                "span": (match.start(), match.end()),
                "value": match.group()
            })
        
        # Detect SSNs
        for match in self.ssn_pattern.finditer(text):
            all_matches.append({
                "type": "ssn",
                "span": (match.start(), match.end()),
                "value": match.group()
            })
        
        # Detect credit card numbers
        for match in self.credit_card_pattern.finditer(text):
            all_matches.append({
                "type": "credit_card",
                "span": (match.start(), match.end()),
                "value": match.group()
            })
        
        # Detect IP addresses
        for match in self.ip_pattern.finditer(text):
            all_matches.append({
                "type": "ip",
                "span": (match.start(), match.end()),
                "value": match.group()
            })
        
        # Sort by span start position for easier processing
        all_matches.sort(key=lambda x: x["span"][0])
        
        return all_matches

class PIIHandler:
    """
    Handler for detecting and masking PII in text.
    
    This class combines detection and masking to provide a complete
    solution for PII protection.
    """
    
    def __init__(self, enable_logging: bool = False):
        """
        Initialize the PII handler.
        
        Args:
            enable_logging: Whether to log PII detection (without the actual PII)
        """
        self.detector = PIIDetector()
        self.enable_logging = enable_logging
    
    async def process_text(self, text: str) -> str:
        """
        Process text to detect and mask PII.
        
        Args:
            text: The text to process
            
        Returns:
            Text with PII masked
        """
        if not text:
            return text
            
        # Detect PII
        pii_matches = await self.detector.detect_pii(text)
        
        if not pii_matches:
            return text
            
        # Log PII detection (without exposing actual PII)
        if self.enable_logging:
            pii_types = [match["type"] for match in pii_matches]
            logger.info(f"Detected {len(pii_matches)} PII items of types: {', '.join(pii_types)}")
        
        # Mask PII
        return await self._mask_pii(text, pii_matches)
    
    async def _mask_pii(self, text: str, matches: List[Dict[str, Any]]) -> str:
        """
        Mask PII in the text.
        
        Args:
            text: Original text
            matches: List of PII matches with span and type information
            
        Returns:
            Text with PII masked
        """
        # If no matches, return the original text
        if not matches:
            return text
            
        # Start with the original text
        masked_text = ""
        last_end = 0
        
        # Replace each match with an appropriate mask
        for match in matches:
            start, end = match["span"]
            pii_type = match["type"]
            
            # Add text before the match
            masked_text += text[last_end:start]
            
            # Add the appropriate mask based on PII type
            masked_text += self._get_mask_for_type(pii_type)
            
            # Update the last end position
            last_end = end
        
        # Add any remaining text after the last match
        masked_text += text[last_end:]
        
        return masked_text
    
    def _get_mask_for_type(self, pii_type: str) -> str:
        """
        Get an appropriate mask string for a PII type.
        
        Args:
            pii_type: Type of PII to mask
            
        Returns:
            Mask string for the PII type
        """
        masks = {
            "email": "[EMAIL]",
            "phone": "[PHONE]",
            "ssn": "[SSN]",
            "credit_card": "[CREDIT_CARD]",
            "ip": "[IP_ADDRESS]",
            "name": "[NAME]",
            "address": "[ADDRESS]",
            "date": "[DATE]"
        }
        
        return masks.get(pii_type, "[REDACTED]") 