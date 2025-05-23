"""
Data Masker Module

This module provides functionality to mask or redact PII from text while
preserving the context and readability of the content.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib
from security.pii_detector import PIIMatch

@dataclass
class MaskingConfig:
    """Configuration for PII masking"""
    mask_char: str = "*"
    preserve_length: bool = True
    hash_mode: bool = False
    keep_prefix: int = 0
    keep_suffix: int = 0

class DataMasker:
    """
    Handles masking of PII in text with configurable strategies.
    """
    
    # Default masking configurations per PII type
    DEFAULT_CONFIGS = {
        'email': MaskingConfig(
            mask_char="*",
            preserve_length=False,
            hash_mode=False,
            keep_prefix=2,
            keep_suffix=4  # Keep domain
        ),
        'phone': MaskingConfig(
            mask_char="*",
            preserve_length=True,
            keep_prefix=2,
            keep_suffix=2
        ),
        'credit_card': MaskingConfig(
            mask_char="*",
            preserve_length=True,
            keep_suffix=4
        ),
        'ssn': MaskingConfig(
            mask_char="*",
            preserve_length=True,
            keep_suffix=4
        ),
        'person': MaskingConfig(
            mask_char="*",
            preserve_length=False,
            hash_mode=True
        ),
        'default': MaskingConfig(
            mask_char="*",
            preserve_length=True
        )
    }
    
    def __init__(self, custom_configs: Optional[Dict[str, MaskingConfig]] = None):
        """
        Initialize the data masker.
        
        Args:
            custom_configs: Optional custom masking configurations per PII type
        """
        self.configs = self.DEFAULT_CONFIGS.copy()
        if custom_configs:
            self.configs.update(custom_configs)

    def mask_text(self, text: str, pii_matches: List[PIIMatch]) -> str:
        """
        Mask PII in text based on detected matches.
        
        Args:
            text: Original text containing PII
            pii_matches: List of detected PII matches
            
        Returns:
            Text with PII masked according to configuration
        """
        if not pii_matches:
            return text
            
        # Sort matches in reverse order to process from end to start
        # This prevents position shifts when replacing text
        pii_matches.sort(key=lambda x: x.start, reverse=True)
        
        # Create a mutable list of characters
        chars = list(text)
        
        for match in pii_matches:
            masked_value = self._mask_value(
                match.text,
                match.pii_type.lower(),
                self.configs.get(match.pii_type.lower(), self.configs['default'])
            )
            
            # Replace the original text with masked version
            chars[match.start:match.end] = masked_value
        
        return ''.join(chars)

    def _mask_value(self, value: str, pii_type: str, config: MaskingConfig) -> str:
        """
        Mask a single PII value according to its configuration.
        
        Args:
            value: Original PII value
            pii_type: Type of PII
            config: Masking configuration to apply
            
        Returns:
            Masked value
        """
        if config.hash_mode:
            # Create a deterministic hash for consistent replacement
            return hashlib.md5(value.encode()).hexdigest()[:8]
        
        # Handle prefix/suffix preservation
        prefix = value[:config.keep_prefix] if config.keep_prefix > 0 else ""
        suffix = value[-config.keep_suffix:] if config.keep_suffix > 0 else ""
        
        # Calculate the length of the part to be masked
        mask_length = len(value) - len(prefix) - len(suffix)
        if mask_length <= 0:
            return value
        
        # Create the masked portion
        if config.preserve_length:
            masked_part = config.mask_char * mask_length
        else:
            masked_part = config.mask_char * 3
        
        return f"{prefix}{masked_part}{suffix}"

    def unmask_for_logging(self, masked_text: str, original_text: str) -> str:
        """
        Create a version for logging that shows mask locations without revealing PII.
        
        Args:
            masked_text: Text with PII masked
            original_text: Original text with PII
            
        Returns:
            Text with mask locations marked for logging
        """
        differences = []
        for i, (m, o) in enumerate(zip(masked_text, original_text)):
            if m != o:
                if not differences or differences[-1][1] != i - 1:
                    differences.append([i, i])
                else:
                    differences[-1][1] = i
        
        result = list(masked_text)
        for start, end in differences:
            result[start] = f"[MASKED:{end-start+1}]"
            result[start+1:end+1] = [""] * (end - start)
        
        return "".join(result) 