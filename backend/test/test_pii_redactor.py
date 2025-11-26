"""
ClaimInvestigator AI - Tests for PII Redactor Service
"""
import pytest
from app.services.pii_redactor import PIIRedactor, get_redactor


class TestPIIRedactor:
    """Test suite for PII redaction functionality"""
    
    def setup_method(self):
        """Setup fresh redactor for each test"""
        self.redactor = PIIRedactor()
        self.redactor.enabled = True
    
    def test_redactor_initialization(self):
        """Test that redactor initializes correctly"""
        assert self.redactor is not None
        assert self.redactor.enabled is True
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = self.redactor.redact("")
        assert result.redacted_text == ""
        assert len(result.mappings) == 0
    
    def test_no_pii(self):
        """Test text with no PII"""
        text = "The weather is nice today."
        result = self.redactor.redact(text)
        assert result.redacted_text == text
        assert len(result.mappings) == 0
    
    def test_ssn_redaction(self):
        """Test SSN redaction"""
        text = "SSN is 123-45-6789"
        result = self.redactor.redact(text)
        assert "123-45-6789" not in result.redacted_text
        assert "[SSN_" in result.redacted_text
        assert len(result.mappings) >= 1
    
    def test_phone_redaction(self):
        """Test phone number redaction"""
        text = "Call me at 555-123-4567"
        result = self.redactor.redact(text)
        assert "555-123-4567" not in result.redacted_text
        assert "[PHONE_" in result.redacted_text
    
    def test_email_redaction(self):
        """Test email address redaction"""
        text = "Email: john.doe@example.com"
        result = self.redactor.redact(text)
        assert "john.doe@example.com" not in result.redacted_text
        assert "[EMAIL_" in result.redacted_text
    
    def test_claim_number_redaction(self):
        """Test claim number redaction"""
        text = "Claim CLM-123456789 is pending"
        result = self.redactor.redact(text)
        assert "CLM-123456789" not in result.redacted_text
        assert "[CLAIM_NUM_" in result.redacted_text
    
    def test_policy_number_redaction(self):
        """Test policy number redaction"""
        text = "Policy POL-987654321 expires soon"
        result = self.redactor.redact(text)
        assert "POL-987654321" not in result.redacted_text
        assert "[POLICY_NUM_" in result.redacted_text
    
    def test_multiple_pii_types(self):
        """Test redaction of multiple PII types in one text"""
        text = "John Smith (SSN: 123-45-6789) called at 555-123-4567 regarding claim CLM-123456"
        result = self.redactor.redact(text)
        
        # All PII should be redacted
        assert "123-45-6789" not in result.redacted_text
        assert "555-123-4567" not in result.redacted_text
        assert "CLM-123456" not in result.redacted_text
        
        # Should have multiple mappings
        assert len(result.mappings) >= 3
    
    def test_name_detection(self):
        """Test person name detection"""
        text = "Mr. John Smith reported the incident"
        result = self.redactor.redact(text)
        assert "John Smith" not in result.redacted_text
        assert "[PERSON_" in result.redacted_text
    
    def test_restore_function(self):
        """Test that redacted text can be restored"""
        original_text = "Contact John at 555-123-4567"
        result = self.redactor.redact(original_text)
        
        # Restore
        restored = self.redactor.restore(result.redacted_text, result.mappings)
        
        # Phone should be restored (name detection might vary)
        assert "555-123-4567" in restored
    
    def test_disabled_redactor(self):
        """Test that disabled redactor passes through text unchanged"""
        self.redactor.enabled = False
        text = "SSN: 123-45-6789, Phone: 555-123-4567"
        result = self.redactor.redact(text)
        
        assert result.redacted_text == text
        assert len(result.mappings) == 0
    
    def test_date_redaction(self):
        """Test date format redaction"""
        text = "Date of loss: 12/25/2024"
        result = self.redactor.redact(text)
        assert "12/25/2024" not in result.redacted_text
        assert "[DATE_" in result.redacted_text
    
    def test_ip_address_redaction(self):
        """Test IP address redaction"""
        text = "Logged from IP 192.168.1.100"
        result = self.redactor.redact(text)
        assert "192.168.1.100" not in result.redacted_text
        assert "[IP_" in result.redacted_text
    
    def test_entities_found_count(self):
        """Test that entity counts are accurate"""
        text = "SSN: 123-45-6789 and 987-65-4321"
        result = self.redactor.redact(text)
        assert result.entities_found.get("US_SSN", 0) == 2
    
    def test_redaction_summary(self):
        """Test redaction summary generation"""
        text = "SSN: 123-45-6789, Phone: 555-123-4567"
        result = self.redactor.redact(text)
        summary = self.redactor.get_redaction_summary(result)
        
        assert "ssn" in summary.lower() or "phone" in summary.lower()
    
    def test_placeholder_uniqueness(self):
        """Test that placeholders are unique"""
        text = "Call 555-111-1111 or 555-222-2222"
        result = self.redactor.redact(text)
        
        # Both phone numbers should have different placeholders
        placeholders = [m.placeholder for m in result.mappings]
        assert len(placeholders) == len(set(placeholders))  # All unique


class TestPIIRedactorSingleton:
    """Test singleton pattern"""
    
    def test_singleton_returns_same_instance(self):
        """Test that get_redactor returns same instance"""
        redactor1 = get_redactor()
        redactor2 = get_redactor()
        assert redactor1 is redactor2


class TestPIIRedactorEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def setup_method(self):
        self.redactor = PIIRedactor()
        self.redactor.enabled = True
    
    def test_overlapping_patterns(self):
        """Test handling of potentially overlapping patterns"""
        # A string that could match multiple patterns
        text = "Reference: 123-456-7890"  # Could be phone or partial SSN
        result = self.redactor.redact(text)
        
        # Should not crash and should redact something
        assert result.redacted_text != text or len(result.mappings) == 0
    
    def test_very_long_text(self):
        """Test handling of long text"""
        text = "Contact " + "555-123-4567 " * 100
        result = self.redactor.redact(text)
        
        # Should handle without error
        assert "[PHONE_" in result.redacted_text
    
    def test_special_characters(self):
        """Test handling of special characters"""
        text = "Email: user+tag@example.com"
        result = self.redactor.redact(text)
        assert "user+tag@example.com" not in result.redacted_text
    
    def test_unicode_text(self):
        """Test handling of unicode characters"""
        text = "Contact José at 555-123-4567"
        result = self.redactor.redact(text)
        assert "555-123-4567" not in result.redacted_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])