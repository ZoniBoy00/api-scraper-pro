"""
Data Normalizer - PII Anonymization & Data Cleaning
===================================================

Normalizes and anonymizes personally identifiable information.
"""

from typing import Any, Dict, List, Set
import re
from loguru import logger


class DataNormalizer:
    """Normalizes and anonymizes API data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.compliance = config.get('compliance', {})
        self.anonymize_pii = self.compliance.get('anonymize_pii', True)
        self.pii_fields = set(self.compliance.get('pii_fields', []))
        
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        }
    
    def anonymize(self, data: Any, depth: int = 0, max_depth: int = 10) -> Any:
        """Anonymize PII in data."""
        if not self.anonymize_pii or depth >= max_depth:
            return data
        
        if isinstance(data, dict):
            return {key: self._anonymize_value(key, value, depth) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.anonymize(item, depth + 1, max_depth) for item in data]
        else:
            return data
    
    def _anonymize_value(self, key: str, value: Any, depth: int) -> Any:
        """Anonymize single value."""
        if key.lower() in self.pii_fields:
            return self._mask_value(value)
        
        if isinstance(value, (dict, list)):
            return self.anonymize(value, depth + 1)
        
        if isinstance(value, str):
            return self._mask_pii_in_string(value)
        
        return value
    
    def _mask_value(self, value: Any) -> str:
        """Mask value with asterisks."""
        if value is None:
            return None
        
        value_str = str(value)
        if len(value_str) <= 2:
            return '*' * len(value_str)
        
        return value_str[0] + '*' * (len(value_str) - 2) + value_str[-1]
    
    def _mask_pii_in_string(self, text: str) -> str:
        """Mask PII patterns in string."""
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                masked = self._mask_value(match)
                text = text.replace(match, masked)
                logger.debug(f"Anonymized {pii_type}: {match} -> {masked}")
        return text
    
    def detect_pii(self, data: Any) -> Dict[str, List[str]]:
        """Detect PII fields in data."""
        found_pii = {pii_type: [] for pii_type in self.patterns.keys()}
        self._detect_pii_recursive(data, found_pii)
        return {k: v for k, v in found_pii.items() if v}
    
    def _detect_pii_recursive(self, data: Any, found_pii: Dict[str, List[str]], depth: int = 0, max_depth: int = 10):
        """Recursive PII detection."""
        if depth >= max_depth:
            return
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in self.pii_fields and value:
                    for pii_type in self.patterns.keys():
                        if pii_type in key.lower():
                            found_pii[pii_type].append(str(value))
                            break
                
                if isinstance(value, str):
                    self._detect_pii_in_string(value, found_pii)
                elif isinstance(value, (dict, list)):
                    self._detect_pii_recursive(value, found_pii, depth + 1)
        
        elif isinstance(data, list):
            for item in data:
                self._detect_pii_recursive(item, found_pii, depth + 1)
    
    def _detect_pii_in_string(self, text: str, found_pii: Dict[str, List[str]]):
        """Detect PII patterns in string."""
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                found_pii[pii_type].extend(matches)
