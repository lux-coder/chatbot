"""
PII Detector Module

This module provides functionality to detect and identify PII (Personally Identifiable Information)
in text using pattern matching, NLP, and rule-based approaches.
"""

import re
from typing import List, Dict, Set, Pattern, Tuple
from dataclasses import dataclass
import spacy
from spacy.language import Language
from spacy.tokens import Doc

@dataclass
class PIIMatch:
    """Represents a PII match in text"""
    start: int
    end: int
    text: str
    pii_type: str
    confidence: float

class PIIPatterns:
    """Common PII patterns for detection"""
    
    # Email addresses
    EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Phone numbers (international format)
    PHONE = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    
    # Credit card numbers
    CREDIT_CARD = r'\b(?:\d[ -]*?){13,16}\b'
    
    # Social Security Numbers (US)
    SSN = r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
    
    # IP Addresses
    IP_ADDRESS = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    
    # URLs
    URL = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    
    # Date of Birth
    DOB = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'

class PIIDetector:
    """
    Detector for PII in text using both pattern matching and NLP.
    """
    
    def __init__(self):
        """Initialize the PII detector with patterns and NLP model"""
        # Compile regex patterns
        self.patterns: Dict[str, Pattern] = {
            'email': re.compile(PIIPatterns.EMAIL, re.IGNORECASE),
            'phone': re.compile(PIIPatterns.PHONE),
            'credit_card': re.compile(PIIPatterns.CREDIT_CARD),
            'ssn': re.compile(PIIPatterns.SSN),
            'ip_address': re.compile(PIIPatterns.IP_ADDRESS),
            'url': re.compile(PIIPatterns.URL),
            'dob': re.compile(PIIPatterns.DOB)
        }
        
        # Load spaCy model for NER
        self.nlp: Language = spacy.load("en_core_web_sm")
        
        # NER labels that might contain PII
        self.ner_pii_labels: Set[str] = {
            'PERSON', 'ORG', 'GPE', 'LOC', 'MONEY'
        }

    def _find_pattern_matches(self, text: str) -> List[PIIMatch]:
        """
        Find PII using regex patterns.
        
        Args:
            text: Input text to search
            
        Returns:
            List of PIIMatch objects
        """
        matches: List[PIIMatch] = []
        
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                matches.append(PIIMatch(
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    pii_type=pii_type,
                    confidence=1.0  # Pattern matches are certain
                ))
        
        return matches

    def _find_ner_matches(self, doc: Doc) -> List[PIIMatch]:
        """
        Find PII using Named Entity Recognition.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of PIIMatch objects
        """
        matches: List[PIIMatch] = []
        
        for ent in doc.ents:
            if ent.label_ in self.ner_pii_labels:
                matches.append(PIIMatch(
                    start=ent.start_char,
                    end=ent.end_char,
                    text=ent.text,
                    pii_type=ent.label_.lower(),
                    confidence=0.8  # NER matches are less certain
                ))
        
        return matches

    def detect(self, text: str) -> List[PIIMatch]:
        """
        Detect PII in text using both pattern matching and NER.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of PIIMatch objects representing found PII
        """
        # Find pattern matches
        pattern_matches = self._find_pattern_matches(text)
        
        # Process with spaCy for NER
        doc = self.nlp(text)
        ner_matches = self._find_ner_matches(doc)
        
        # Combine and sort matches by position
        all_matches = pattern_matches + ner_matches
        all_matches.sort(key=lambda x: x.start)
        
        # Remove overlapping matches, preferring higher confidence
        return self._remove_overlaps(all_matches)

    def _remove_overlaps(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        """
        Remove overlapping matches, keeping the ones with higher confidence.
        
        Args:
            matches: List of PIIMatch objects
            
        Returns:
            List of non-overlapping PIIMatch objects
        """
        if not matches:
            return []
            
        result = [matches[0]]
        
        for current in matches[1:]:
            prev = result[-1]
            
            # Check for overlap
            if current.start <= prev.end:
                # Keep the match with higher confidence
                if current.confidence > prev.confidence:
                    result[-1] = current
            else:
                result.append(current)
        
        return result

    def validate_pii_removal(self, original_text: str, masked_text: str) -> bool:
        """
        Validate that all PII has been properly masked.
        
        Args:
            original_text: Original text before masking
            masked_text: Text after masking
            
        Returns:
            True if all PII appears to be properly masked
        """
        # Detect PII in masked text
        remaining_pii = self.detect(masked_text)
        
        # Check if any high-confidence PII remains
        return not any(match.confidence > 0.8 for match in remaining_pii) 