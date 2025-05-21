"""
Security Module

This module provides security-related functionality including PII detection and masking.
"""

import re
from typing import Dict, List, Set, Optional
import spacy
from pydantic import BaseModel
from app.core.monitoring import log_security_event

class PIIPattern(BaseModel):
    """Configuration for a PII pattern"""
    name: str
    pattern: str
    mask_with: str
    priority: int = 0

class PIIDetector:
    """
    Detects PII using both regex patterns and NLP-based entity recognition.
    """
    
    def __init__(self):
        """Initialize the PII detector with common patterns and NLP model."""
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
            
        # Common PII patterns
        self.patterns = [
            PIIPattern(
                name="email",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                mask_with="[EMAIL]",
                priority=1
            ),
            PIIPattern(
                name="phone",
                pattern=r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
                mask_with="[PHONE]",
                priority=1
            ),
            PIIPattern(
                name="ssn",
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                mask_with="[SSN]",
                priority=2
            ),
            PIIPattern(
                name="credit_card",
                pattern=r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
                mask_with="[CREDIT_CARD]",
                priority=2
            ),
            PIIPattern(
                name="ip_address",
                pattern=r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                mask_with="[IP_ADDRESS]",
                priority=1
            )
        ]
        
        # NER entity types to mask
        self.ner_types = {
            "PERSON": "[PERSON]",
            "ORG": "[ORGANIZATION]",
            "GPE": "[LOCATION]",
            "MONEY": "[MONEY_AMOUNT]",
            "DATE": "[DATE]"
        }

    async def detect_regex_pii(self, text: str) -> List[Dict]:
        """
        Detect PII using regex patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dictionaries containing PII matches and their positions
        """
        matches = []
        for pattern in self.patterns:
            for match in re.finditer(pattern.pattern, text):
                matches.append({
                    "start": match.start(),
                    "end": match.end(),
                    "value": match.group(),
                    "type": pattern.name,
                    "mask": pattern.mask_with,
                    "priority": pattern.priority
                })
        return matches

    async def detect_ner_pii(self, text: str) -> List[Dict]:
        """
        Detect PII using NLP-based named entity recognition.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dictionaries containing PII matches and their positions
        """
        doc = self.nlp(text)
        matches = []
        
        for ent in doc.ents:
            if ent.label_ in self.ner_types:
                matches.append({
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "value": ent.text,
                    "type": ent.label_,
                    "mask": self.ner_types[ent.label_],
                    "priority": 1
                })
        return matches

class DataMasker:
    """
    Handles masking of detected PII in text.
    """
    
    def __init__(self):
        """Initialize the data masker."""
        pass

    async def mask_text(self, text: str, matches: List[Dict]) -> str:
        """
        Mask PII in text based on detected matches.
        
        Args:
            text: Original text
            matches: List of PII matches with positions and mask values
            
        Returns:
            Text with PII masked
        """
        # Sort matches by start position in reverse order
        # This allows us to replace from end to start without affecting positions
        matches.sort(key=lambda x: (-x["start"], -x["priority"]))
        
        # Create list from string for character-by-character replacement
        chars = list(text)
        
        # Track masked ranges to avoid double-masking
        masked_ranges: Set[range] = set()
        
        for match in matches:
            match_range = range(match["start"], match["end"])
            
            # Check if this range overlaps with any already masked range
            overlap = any(
                len(set(match_range).intersection(masked_range)) > 0
                for masked_range in masked_ranges
            )
            
            if not overlap:
                # Replace characters with mask
                chars[match["start"]:match["end"]] = list(match["mask"])
                masked_ranges.add(match_range)
        
        return "".join(chars)

class PIIHandler:
    """
    Unified interface for PII detection and masking.
    """
    
    def __init__(self):
        """Initialize the PII handler with detector and masker."""
        self.detector = PIIDetector()
        self.masker = DataMasker()

    async def process_text(self, text: str) -> str:
        """
        Process text to detect and mask PII.
        
        Args:
            text: Text to process
            
        Returns:
            Text with PII masked
        """
        try:
            # Detect PII using both methods
            regex_matches = await self.detector.detect_regex_pii(text)
            ner_matches = await self.detector.detect_ner_pii(text)
            
            # Combine all matches
            all_matches = regex_matches + ner_matches
            
            # If PII was found, log the event (without the actual PII values)
            if all_matches:
                await log_security_event(
                    event_type="pii_detected",
                    pii_types=[match["type"] for match in all_matches],
                    count=len(all_matches)
                )
            
            # Mask the text
            masked_text = await self.masker.mask_text(text, all_matches)
            
            return masked_text
            
        except Exception as e:
            await log_security_event(
                event_type="pii_processing_error",
                error_type=str(type(e).__name__),
                error_message=str(e)
            )
            # On error, return the original text to avoid breaking the chat flow
            # but log the error for monitoring
            return text 