"""
ClaimInvestigator AI - Health Check Router
API endpoints for health monitoring and status
"""
from fastapi import APIRouter
from app.core.config import settings
from app.services.llm_router import get_router
from app.models.claim_models import ModelInfo, APIStatus

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/status")
async def detailed_status() -> APIStatus:
    """Detailed API status including available models"""
    llm_router = get_router()
    available_providers = llm_router.get_available_providers()
    
    # Build model info list
    model_info = []
    
    model_configs = [
        {
            "provider": "claude",
            "model_name": settings.CLAUDE_MODEL,
            "best_for": ["Complex reasoning", "Question generation", "Coverage analysis"]
        },
        {
            "provider": "openai", 
            "model_name": settings.OPENAI_MODEL,
            "best_for": ["Structured JSON output", "File notes", "Fast responses"]
        },
        {
            "provider": "gemini",
            "model_name": settings.GEMINI_MODEL,
            "best_for": ["Extraction tasks", "Document processing"]
        },
        {
            "provider": "azure",
            "model_name": settings.AZURE_OPENAI_DEPLOYMENT,
            "best_for": ["Enterprise compliance", "Regulated environments"]
        }
    ]
    
    for config in model_configs:
        model_info.append(ModelInfo(
            provider=config["provider"],
            model_name=config["model_name"],
            available=config["provider"] in available_providers,
            best_for=config["best_for"]
        ))
    
    return APIStatus(
        status="healthy",
        version=settings.APP_VERSION,
        available_models=model_info,
        pii_redaction_enabled=settings.ENABLE_PII_REDACTION,
        supported_claim_types=settings.SUPPORTED_CLAIM_TYPES,
        supported_jurisdictions=settings.SUPPORTED_JURISDICTIONS
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    llm_router = get_router()
    providers = llm_router.get_available_providers()
    
    if not providers:
        return {
            "ready": True,
            "warning": "No LLM providers configured - using mock responses",
            "mode": "mock"
        }
    
    return {
        "ready": True,
        "providers": providers,
        "mode": "production"
    }