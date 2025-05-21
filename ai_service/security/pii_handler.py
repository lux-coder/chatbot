"""
PII Handler Module

This module provides a unified interface for PII detection and masking,
combining the functionality of the detector and masker components.
"""

from typing import Dict, Optional, List, Any
import logging
from .pii_detector import PIIDetector, PIIMatch
from .data_masker import DataMasker, MaskingConfig

logger = logging.getLogger(__name__)

class PIIHandler:
    """
    Main class for handling PII detection and masking in text.
    
    This class combines the PIIDetector and DataMasker to provide
    a complete solution for identifying and protecting PII.
    """
    
    def __init__(
        self,
        custom_masking_configs: Optional[Dict[str, MaskingConfig]] = None,
        enable_logging: bool = True
    ):
        """
        Initialize the PII handler.
        
        Args:
            custom_masking_configs: Optional custom masking configurations
            enable_logging: Whether to log PII detection events
        """
        self.detector = PIIDetector()
        self.masker = DataMasker(custom_masking_configs)
        self.enable_logging = enable_logging

    def process_text(self, text: str) -> str:
        """
        Process text to detect and mask PII.
        
        Args:
            text: Input text that may contain PII
            
        Returns:
            Text with PII masked
        """
        # Detect PII
        pii_matches = self.detector.detect(text)
        
        if pii_matches and self.enable_logging:
            self._log_pii_detection(text, pii_matches)
        
        # Mask detected PII
        masked_text = self.masker.mask_text(text, pii_matches)
        
        # Validate masking
        if not self.detector.validate_pii_removal(text, masked_text):
            logger.warning("PII masking validation failed - some PII may remain")
        
        return masked_text

    def process_dict(self, data: Dict[str, Any], sensitive_keys: List[str]) -> Dict[str, Any]:
        """
        Process a dictionary to mask PII in specified fields.
        
        Args:
            data: Dictionary that may contain PII
            sensitive_keys: List of keys that might contain PII
            
        Returns:
            Dictionary with PII masked in sensitive fields
        """
        result = data.copy()
        
        for key in sensitive_keys:
            if key in result and isinstance(result[key], str):
                result[key] = self.process_text(result[key])
        
        return result

    def _log_pii_detection(self, text: str, matches: List[PIIMatch]) -> None:
        """
        Log PII detection events without revealing the actual PII.
        
        Args:
            text: Original text
            matches: List of PII matches found
        """
        if not self.enable_logging:
            return
            
        # Create a safe logging version
        masked_text = self.masker.mask_text(text, matches)
        safe_log_text = self.masker.unmask_for_logging(masked_text, text)
        
        logger.info(
            "PII detected and masked",
            extra={
                "pii_types": [m.pii_type for m in matches],
                "match_count": len(matches),
                "masked_text": safe_log_text
            }
        )

    def validate_text(self, text: str) -> bool:
        """
        Check if text contains any PII.
        
        Args:
            text: Text to check for PII
            
        Returns:
            True if no PII is detected, False otherwise
        """
        matches = self.detector.detect(text)
        return len(matches) == 0 