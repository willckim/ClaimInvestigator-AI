"""
ClaimInvestigator AI - PII Redaction Service
Privacy-first transformer that redacts PII before sending to external LLMs
"""
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PIIMapping:
    """Stores mapping between original PII and placeholder"""
    original: str
    placeholder: str
    entity_type: str
    start: int
    end: int


@dataclass
class RedactionResult:
    """Result of PII redaction"""
    redacted_text: str
    mappings: List[PIIMapping] = field(default_factory=list)
    entities_found: Dict[str, int] = field(default_factory=dict)
    

class PIIRedactor:
    """
    Privacy-first PII redaction service.
    
    Detects and replaces sensitive information with placeholders before
    sending text to external LLM providers. Maintains a mapping to restore
    original values if needed (mapping stays local, never sent to LLMs).
    
    Supported PII Types:
    - Names (PERSON)
    - Phone numbers
    - Email addresses
    - SSN
    - Driver's license numbers
    - Credit card numbers
    - IP addresses
    - Dates
    - Addresses/Locations
    - Claim/Policy numbers
    - Medical record numbers
    """
    
    def __init__(self):
        self.enabled = settings.ENABLE_PII_REDACTION
        self.entities_to_redact = settings.PII_ENTITIES_TO_REDACT
        
        # Counters for generating unique placeholders
        self._counters: Dict[str, int] = {}
        
        # Regex patterns for PII detection
        self._patterns = self._compile_patterns()
        
        logger.info(f"PIIRedactor initialized. Enabled: {self.enabled}")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection"""
        return {
            # SSN: XXX-XX-XXXX or XXXXXXXXX
            "US_SSN": re.compile(
                r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
            ),
            # Phone: Various formats
            "PHONE_NUMBER": re.compile(
                r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
            ),
            # Email
            "EMAIL_ADDRESS": re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ),
            # Credit Card (basic patterns)
            "CREDIT_CARD": re.compile(
                r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
            ),
            # IP Address
            "IP_ADDRESS": re.compile(
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ),
            # Date patterns (MM/DD/YYYY, YYYY-MM-DD, etc.)
            "DATE_TIME": re.compile(
                r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
            ),
            # Claim numbers (common patterns)
            "CLAIM_NUMBER": re.compile(
                r'\b(?:CLM|CLAIM|CL)[-#]?\d{6,12}\b',
                re.IGNORECASE
            ),
            # Policy numbers
            "POLICY_NUMBER": re.compile(
                r'\b(?:POL|POLICY|PL)[-#]?\d{6,12}\b',
                re.IGNORECASE
            ),
            # Driver's license (generic pattern - state-specific would be better)
            "US_DRIVER_LICENSE": re.compile(
                r'\b[A-Z]{1,2}\d{6,8}\b'
            ),
            # Medical Record Number
            "MEDICAL_LICENSE": re.compile(
                r'\b(?:MRN|MR)[-#]?\d{6,10}\b',
                re.IGNORECASE
            ),
            # Street addresses (simplified)
            "LOCATION": re.compile(
                r'\b\d{1,5}\s+[\w\s]{1,30}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Circle|Cir)\.?\b',
                re.IGNORECASE
            ),
        }
        
    def _get_placeholder(self, entity_type: str) -> str:
        """Generate a unique placeholder for an entity type"""
        if entity_type not in self._counters:
            self._counters[entity_type] = 0
        self._counters[entity_type] += 1
        
        # Create readable placeholders
        type_map = {
            "PERSON": "PERSON",
            "PHONE_NUMBER": "PHONE",
            "EMAIL_ADDRESS": "EMAIL",
            "US_SSN": "SSN",
            "CREDIT_CARD": "CC",
            "IP_ADDRESS": "IP",
            "DATE_TIME": "DATE",
            "CLAIM_NUMBER": "CLAIM_NUM",
            "POLICY_NUMBER": "POLICY_NUM",
            "US_DRIVER_LICENSE": "DL",
            "MEDICAL_LICENSE": "MRN",
            "LOCATION": "LOCATION",
        }
        
        prefix = type_map.get(entity_type, entity_type)
        return f"[{prefix}_{self._counters[entity_type]}]"
    
    def _detect_names(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Detect potential person names in text.
        Uses heuristics since we're avoiding heavy NLP libraries.
        """
        names = []
        
        # Common name patterns
        # Title + Name: "Mr. John Smith", "Dr. Jane Doe"
        title_pattern = re.compile(
            r'\b(Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        )
        
        # Two capitalized words that might be names
        two_caps_pattern = re.compile(
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
        )
        
        # Find title + name patterns
        for match in title_pattern.finditer(text):
            names.append((match.start(), match.end(), "PERSON"))
        
        # Find potential two-word names (more false positives, but safer)
        # Exclude common non-name pairs
        exclude_pairs = {
            'First Notice', 'Notice Loss', 'Property Damage', 'Bodily Injury',
            'General Liability', 'Workers Compensation', 'United States',
            'New York', 'Los Angeles', 'San Francisco', 'San Diego',
            'Police Report', 'Medical Records', 'Insurance Company'
        }
        
        for match in two_caps_pattern.finditer(text):
            full_match = match.group(0)
            if full_match not in exclude_pairs:
                # Check if it's not already captured by title pattern
                already_captured = any(
                    start <= match.start() < end for start, end, _ in names
                )
                if not already_captured:
                    names.append((match.start(), match.end(), "PERSON"))
        
        return names
    
    def redact(self, text: str) -> RedactionResult:
        """
        Redact PII from text.
        
        Args:
            text: Input text potentially containing PII
            
        Returns:
            RedactionResult with redacted text and mappings
        """
        if not self.enabled:
            return RedactionResult(redacted_text=text)
        
        if not text:
            return RedactionResult(redacted_text="")
        
        # Reset counters for this redaction session
        self._counters = {}
        
        # Collect all PII matches
        all_matches: List[Tuple[int, int, str, str]] = []  # (start, end, type, original)
        
        # Detect regex-based patterns
        for entity_type, pattern in self._patterns.items():
            if entity_type in self.entities_to_redact or entity_type in [
                "CLAIM_NUMBER", "POLICY_NUMBER"  # Always redact these
            ]:
                for match in pattern.finditer(text):
                    all_matches.append((
                        match.start(),
                        match.end(),
                        entity_type,
                        match.group(0)
                    ))
        
        # Detect names if PERSON is in entities to redact
        if "PERSON" in self.entities_to_redact:
            for start, end, entity_type in self._detect_names(text):
                all_matches.append((start, end, entity_type, text[start:end]))
        
        # Sort matches by start position (descending) to replace from end
        all_matches.sort(key=lambda x: x[0], reverse=True)
        
        # Remove overlapping matches (keep longer ones)
        filtered_matches = []
        for match in all_matches:
            start, end, _, _ = match
            overlaps = False
            for f_start, f_end, _, _ in filtered_matches:
                if not (end <= f_start or start >= f_end):
                    overlaps = True
                    break
            if not overlaps:
                filtered_matches.append(match)
        
        # Apply redactions
        redacted_text = text
        mappings = []
        entities_found: Dict[str, int] = {}
        
        for start, end, entity_type, original in filtered_matches:
            placeholder = self._get_placeholder(entity_type)
            
            # Create mapping
            mapping = PIIMapping(
                original=original,
                placeholder=placeholder,
                entity_type=entity_type,
                start=start,
                end=end
            )
            mappings.append(mapping)
            
            # Count entities
            entities_found[entity_type] = entities_found.get(entity_type, 0) + 1
            
            # Replace in text
            redacted_text = redacted_text[:start] + placeholder + redacted_text[end:]
        
        # Reverse mappings to match original order
        mappings.reverse()
        
        if entities_found:
            logger.info(f"Redacted PII: {entities_found}")
        
        return RedactionResult(
            redacted_text=redacted_text,
            mappings=mappings,
            entities_found=entities_found
        )
    
    def restore(self, redacted_text: str, mappings: List[PIIMapping]) -> str:
        """
        Restore original PII from redacted text using mappings.
        
        WARNING: Only use this for internal processing, never send
        restored text to external services.
        
        Args:
            redacted_text: Text with placeholders
            mappings: List of PII mappings
            
        Returns:
            Text with original PII restored
        """
        restored_text = redacted_text
        
        # Sort by placeholder to handle them in order
        for mapping in sorted(mappings, key=lambda m: m.placeholder, reverse=True):
            restored_text = restored_text.replace(
                mapping.placeholder,
                mapping.original
            )
        
        return restored_text
    
    def get_redaction_summary(self, result: RedactionResult) -> str:
        """Generate a human-readable summary of redactions"""
        if not result.entities_found:
            return "No PII detected"
        
        summary_parts = []
        for entity_type, count in result.entities_found.items():
            summary_parts.append(f"{count} {entity_type.lower().replace('_', ' ')}(s)")
        
        return f"Redacted: {', '.join(summary_parts)}"


# Singleton instance
_redactor: Optional[PIIRedactor] = None


def get_redactor() -> PIIRedactor:
    """Get singleton PIIRedactor instance"""
    global _redactor
    if _redactor is None:
        _redactor = PIIRedactor()
    return _redactor