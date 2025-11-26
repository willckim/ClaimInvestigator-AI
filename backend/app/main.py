"""
ClaimInvestigator AI - Main FastAPI Application
Enterprise AI-powered claims investigation workflow assistant
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.routers import health, claims

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📋 Default LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    logger.info(f"🔒 PII Redaction: {'Enabled' if settings.ENABLE_PII_REDACTION else 'Disabled'}")
    
    # Log available providers
    providers = []
    if settings.ANTHROPIC_API_KEY:
        providers.append("Claude")
    if settings.OPENAI_API_KEY:
        providers.append("OpenAI")
    if settings.GOOGLE_API_KEY:
        providers.append("Gemini")
    if settings.AZURE_OPENAI_API_KEY:
        providers.append("Azure OpenAI")
    
    if providers:
        logger.info(f"✅ Available LLM Providers: {', '.join(providers)}")
    else:
        logger.warning("⚠️ No LLM API keys configured - using mock responses")
    
    yield
    
    # Shutdown
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## ClaimInvestigator AI
    
    An enterprise AI-powered claims investigation workflow assistant that helps 
    claims specialists go from "new claim just came in" to structured investigation 
    plan + draft file notes.
    
    ### Features
    
    - **Claim Triage & Checklist Generator** - Classify claims and generate investigation to-do lists
    - **Investigation Question Drafts** - Generate questions for claimants, witnesses, and insureds
    - **Coverage & Liability Issue Spotter** - Identify potential coverage and liability issues
    - **File Note Generator** - Generate professional claim notes and diary entries
    - **Multi-Model AI Routing** - Intelligently routes to Claude, GPT-4, Gemini, or Azure OpenAI
    - **PII Redaction** - Privacy-first design with automatic PII detection and masking
    
    ### Supported Claim Types
    
    - Auto Bodily Injury (BI)
    - Auto Property Damage (PD)
    - General Liability (GL)
    - Workers Compensation (WC)
    - Property Claims
    - Professional Liability
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    prefix=f"{settings.API_V1_PREFIX}/health",
    tags=["Health"]
)

app.include_router(
    claims.router,
    prefix=f"{settings.API_V1_PREFIX}/claims",
    tags=["Claims Investigation"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered claims investigation workflow assistant",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )