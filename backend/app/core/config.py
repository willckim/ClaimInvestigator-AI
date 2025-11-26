"""
ClaimInvestigator AI - Configuration Settings
Supports multiple LLM providers for claims investigation
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # ===================
    # App Settings
    # ===================
    APP_NAME: str = "ClaimInvestigator AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # ===================
    # API Settings
    # ===================
    API_V1_PREFIX: str = "/api/v1"
    
    # ===================
    # CORS Settings
    # ===================
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://claim-investigator.vercel.app"
    ]
    
    # ===================
    # Database
    # ===================
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/claims_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ===================
    # LLM Provider Settings
    # ===================
    
    # Default model for routing
    DEFAULT_LLM_PROVIDER: str = "claude"  # claude, openai, gemini, azure
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # ===================
    # LLM Routing Strategy
    # ===================
    # Which model to use for specific tasks
    ROUTING_STRATEGY: dict = {
        "claim_triage": "claude",           # Long reasoning for classification
        "question_generation": "claude",     # Complex question drafting
        "coverage_analysis": "claude",       # Legal/coverage reasoning
        "file_notes": "openai",             # Structured JSON output
        "extraction": "gemini",              # Fast extraction tasks
        "enterprise_demo": "azure"           # Enterprise compliance demo
    }
    
    # ===================
    # PII Redaction Settings
    # ===================
    ENABLE_PII_REDACTION: bool = True
    PII_ENTITIES_TO_REDACT: List[str] = [
        "PERSON",
        "PHONE_NUMBER", 
        "EMAIL_ADDRESS",
        "US_SSN",
        "US_DRIVER_LICENSE",
        "CREDIT_CARD",
        "IP_ADDRESS",
        "DATE_TIME",
        "LOCATION",
        "US_PASSPORT",
        "MEDICAL_LICENSE"
    ]
    
    # ===================
    # Claims Settings
    # ===================
    SUPPORTED_CLAIM_TYPES: List[str] = [
        "auto_bi",      # Auto Bodily Injury
        "auto_pd",      # Auto Property Damage
        "gl",           # General Liability
        "wc",           # Workers Compensation
        "property",     # Property Claims
        "professional"  # Professional Liability
    ]
    
    SUPPORTED_JURISDICTIONS: List[str] = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()