"""
ClaimInvestigator AI - Claims Investigation Router
Main API endpoints for claims analysis and investigation workflow
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from app.services.claim_analyzer import get_analyzer
from app.models.claim_models import (
    ClaimInvestigationRequest,
    QuestionGenerationRequest,
    FileNoteRequest,
    InvestigationResponse,
    QuestionsResponse,
    CoverageResponse,
    FileNoteResponse,
    ClaimType,
    LLMProvider
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=InvestigationResponse)
async def analyze_claim(request: ClaimInvestigationRequest):
    """
    Analyze a new claim and generate investigation checklist.
    
    Takes FNOL (First Notice of Loss) information and policy details,
    then generates:
    - Claim triage and classification
    - Prioritized investigation tasks
    - Documents to request
    - Parties to contact
    
    The request is automatically processed through PII redaction
    before being sent to the LLM provider.
    """
    try:
        analyzer = get_analyzer()
        result = await analyzer.analyze_claim(request)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        return InvestigationResponse(
            success=True,
            checklist=result.get("checklist"),
            model_used=result.get("model_used", "unknown"),
            processing_time_ms=result.get("processing_time_ms", 0),
            pii_redacted=result.get("pii_redacted", False),
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error analyzing claim: {e}")
        return InvestigationResponse(
            success=False,
            checklist=None,
            model_used="none",
            processing_time_ms=0,
            pii_redacted=False,
            error=str(e)
        )


@router.post("/questions", response_model=QuestionsResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """
    Generate investigation questions for a specific party.
    
    Creates tailored questions for:
    - Claimants
    - Witnesses
    - Insureds
    - Employers (for WC claims)
    
    Questions are categorized by:
    - Liability (fault determination)
    - Damages (injuries, property damage)
    - Coverage (red flags, exclusions)
    """
    try:
        analyzer = get_analyzer()
        result = await analyzer.generate_questions(request)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Question generation failed"))
        
        return QuestionsResponse(
            success=True,
            questions=result.get("questions"),
            model_used=result.get("model_used", "unknown"),
            processing_time_ms=result.get("processing_time_ms", 0),
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return QuestionsResponse(
            success=False,
            questions=None,
            model_used="none",
            processing_time_ms=0,
            error=str(e)
        )


@router.post("/coverage", response_model=CoverageResponse)
async def analyze_coverage(request: ClaimInvestigationRequest):
    """
    Analyze coverage and liability issues for a claim.
    
    Identifies:
    - Coverage issues (late notice, exclusions, limits)
    - Liability concerns (comparative negligence, fault)
    - Red flags (pre-existing conditions, suspicious timing)
    - Key questions to resolve
    
    **Note**: This is for educational/training purposes. Actual coverage
    determinations require licensed adjusters and legal review.
    """
    try:
        analyzer = get_analyzer()
        result = await analyzer.analyze_coverage(request)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Coverage analysis failed"))
        
        return CoverageResponse(
            success=True,
            analysis=result.get("analysis"),
            model_used=result.get("model_used", "unknown"),
            processing_time_ms=result.get("processing_time_ms", 0),
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error analyzing coverage: {e}")
        return CoverageResponse(
            success=False,
            analysis=None,
            model_used="none",
            processing_time_ms=0,
            error=str(e)
        )


@router.post("/file-note", response_model=FileNoteResponse)
async def generate_file_note(request: FileNoteRequest):
    """
    Generate professional file note / diary entry.
    
    Creates claim documentation including:
    - Executive summary
    - Detailed activity notes
    - Action plan with dates
    - Reserve recommendations (if applicable)
    - Follow-up scheduling
    
    Notes are formatted for regulatory compliance and
    follow claims documentation best practices.
    """
    try:
        analyzer = get_analyzer()
        result = await analyzer.generate_file_note(request)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "File note generation failed"))
        
        return FileNoteResponse(
            success=True,
            file_note=result.get("file_note"),
            model_used=result.get("model_used", "unknown"),
            processing_time_ms=result.get("processing_time_ms", 0),
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error generating file note: {e}")
        return FileNoteResponse(
            success=False,
            file_note=None,
            model_used="none",
            processing_time_ms=0,
            error=str(e)
        )


@router.get("/claim-types")
async def get_claim_types():
    """Get list of supported claim types with descriptions"""
    return {
        "claim_types": [
            {
                "code": "auto_bi",
                "name": "Auto Bodily Injury",
                "description": "Personal injury claims from auto accidents"
            },
            {
                "code": "auto_pd",
                "name": "Auto Property Damage",
                "description": "Vehicle and property damage from auto accidents"
            },
            {
                "code": "gl",
                "name": "General Liability",
                "description": "Third-party liability claims (slip & fall, etc.)"
            },
            {
                "code": "wc",
                "name": "Workers Compensation",
                "description": "Workplace injury and occupational illness claims"
            },
            {
                "code": "property",
                "name": "Property",
                "description": "Property damage claims (fire, theft, weather)"
            },
            {
                "code": "professional",
                "name": "Professional Liability",
                "description": "Errors & omissions, malpractice claims"
            }
        ]
    }


@router.get("/models")
async def get_available_models():
    """Get list of available LLM models and their optimal use cases"""
    from app.services.llm_router import get_router
    
    router = get_router()
    available = router.get_available_providers()
    
    return {
        "available_providers": available,
        "routing_strategy": {
            "claim_triage": {
                "recommended": "claude",
                "reason": "Best for complex reasoning and classification"
            },
            "question_generation": {
                "recommended": "claude", 
                "reason": "Excels at generating nuanced, comprehensive questions"
            },
            "coverage_analysis": {
                "recommended": "claude",
                "reason": "Strong at legal/policy reasoning"
            },
            "file_notes": {
                "recommended": "openai",
                "reason": "Reliable structured JSON output"
            },
            "extraction": {
                "recommended": "gemini",
                "reason": "Fast and cost-effective for extraction"
            },
            "enterprise_demo": {
                "recommended": "azure",
                "reason": "Demonstrates enterprise compliance capability"
            }
        },
        "fallback_enabled": True,
        "fallback_order": ["claude", "openai", "gemini", "azure"]
    }