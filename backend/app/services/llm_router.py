"""
ClaimInvestigator AI - LLM Router Service
Intelligent multi-model routing for claims investigation tasks

Routes tasks to optimal LLM providers:
- Claude: Long reasoning, complex analysis, question generation
- OpenAI: Structured JSON output, fast responses
- Gemini: Extraction tasks, document processing
- Azure OpenAI: Enterprise compliance, regulated environments
"""
import logging
import time
import json
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.models.claim_models import LLMProvider

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of tasks for intelligent routing"""
    CLAIM_TRIAGE = "claim_triage"
    QUESTION_GENERATION = "question_generation"
    COVERAGE_ANALYSIS = "coverage_analysis"
    FILE_NOTES = "file_notes"
    EXTRACTION = "extraction"
    GENERAL = "general"


class LLMRouter:
    """
    Intelligent LLM Router for claims investigation.
    
    Features:
    - Smart routing based on task type
    - Automatic fallback on provider failure
    - Response caching (optional)
    - Cost tracking
    - Latency monitoring
    """
    
    def __init__(self):
        self.default_provider = settings.DEFAULT_LLM_PROVIDER
        self.routing_strategy = settings.ROUTING_STRATEGY
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(timeout=180.0)
        
        # Track which providers are available
        self._available_providers = self._check_available_providers()
        
        logger.info(f"LLMRouter initialized. Available providers: {self._available_providers}")
    
    def _check_available_providers(self) -> List[str]:
        """Check which LLM providers have API keys configured"""
        available = []
        
        if settings.ANTHROPIC_API_KEY:
            available.append("claude")
        if settings.OPENAI_API_KEY:
            available.append("openai")
        if settings.GOOGLE_API_KEY:
            available.append("gemini")
        if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            available.append("azure")
        
        return available
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return self._available_providers.copy()
    
    def _select_provider(
        self,
        task_type: TaskType,
        preferred: Optional[LLMProvider] = None
    ) -> str:
        """
        Select optimal provider for a task.
        
        Priority:
        1. User preference (if available)
        2. Task-optimized routing
        3. Default provider
        4. First available provider
        """
        # If user specified a preference and it's available
        if preferred and preferred != LLMProvider.AUTO:
            provider = preferred.value
            if provider in self._available_providers:
                return provider
            logger.warning(f"Preferred provider {provider} not available, using routing")
        
        # Task-optimized routing
        optimal = self.routing_strategy.get(task_type.value, self.default_provider)
        if optimal in self._available_providers:
            return optimal
        
        # Fallback to default
        if self.default_provider in self._available_providers:
            return self.default_provider
        
        # Fallback to any available
        if self._available_providers:
            return self._available_providers[0]
        
        raise ValueError("No LLM providers available. Please configure at least one API key.")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        response = await self.client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": settings.CLAUDE_MODEL,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": messages
            }
        )
        response.raise_for_status()
        return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        request_body = {
            "model": settings.OPENAI_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                *messages
            ]
        }
        
        if json_mode:
            request_body["response_format"] = {"type": "json_object"}
        
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=request_body
        )
        response.raise_for_status()
        return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Call Google Gemini API"""
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        response = await self.client.post(
            f"https://generativelanguage.googleapis.com/v1/models/{settings.GEMINI_MODEL}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": settings.GOOGLE_API_KEY},
            json={
                "contents": contents,
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_azure(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Call Azure OpenAI API"""
        endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip('/')
        deployment = settings.AZURE_OPENAI_DEPLOYMENT
        api_version = settings.AZURE_OPENAI_API_VERSION
        
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
        
        response = await self.client.post(
            url,
            headers={
                "api-key": settings.AZURE_OPENAI_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *messages
                ]
            }
        )
        response.raise_for_status()
        return response.json()
    
    def _extract_response_text(self, provider: str, response: Dict[str, Any]) -> str:
        """Extract text content from provider-specific response format"""
        try:
            if provider == "claude":
                return response["content"][0]["text"]
            elif provider in ["openai", "azure"]:
                return response["choices"][0]["message"]["content"]
            elif provider == "gemini":
                return response["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract response from {provider}: {e}")
            raise ValueError(f"Invalid response format from {provider}")
    
    async def complete(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL,
        preferred_provider: Optional[LLMProvider] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Complete a prompt using optimal LLM provider.
        
        Args:
            prompt: The user prompt
            task_type: Type of task for intelligent routing
            preferred_provider: User's preferred provider (optional)
            system_prompt: System prompt to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            json_mode: Request JSON output (OpenAI only)
            
        Returns:
            Dict with 'text', 'provider', 'model', 'latency_ms'
        """
        start_time = time.time()
        
        # Select provider
        provider = self._select_provider(task_type, preferred_provider)
        
        # Default system prompt
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt(task_type)
        
        messages = [{"role": "user", "content": prompt}]
        
        logger.info(f"Routing {task_type.value} task to {provider}")
        
        try:
            if provider == "claude":
                response = await self._call_claude(
                    messages, system_prompt, max_tokens, temperature
                )
            elif provider == "openai":
                response = await self._call_openai(
                    messages, system_prompt, max_tokens, temperature, json_mode
                )
            elif provider == "gemini":
                response = await self._call_gemini(
                    messages, system_prompt, max_tokens, temperature
                )
            elif provider == "azure":
                response = await self._call_azure(
                    messages, system_prompt, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            text = self._extract_response_text(provider, response)
            latency_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Completed {task_type.value} with {provider} in {latency_ms:.0f}ms")
            
            return {
                "text": text,
                "provider": provider,
                "model": self._get_model_name(provider),
                "latency_ms": latency_ms
            }
            
        except Exception as e:
            logger.error(f"Error with {provider}: {e}")
            # Try fallback
            return await self._try_fallback(
                provider, messages, system_prompt, max_tokens, temperature, task_type, start_time
            )
    
    async def _try_fallback(
        self,
        failed_provider: str,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        task_type: TaskType,
        start_time: float
    ) -> Dict[str, Any]:
        """Try fallback providers on failure"""
        fallback_order = ["claude", "openai", "gemini", "azure"]
        
        for provider in fallback_order:
            if provider == failed_provider:
                continue
            if provider not in self._available_providers:
                continue
            
            logger.info(f"Trying fallback provider: {provider}")
            
            try:
                if provider == "claude":
                    response = await self._call_claude(
                        messages, system_prompt, max_tokens, temperature
                    )
                elif provider == "openai":
                    response = await self._call_openai(
                        messages, system_prompt, max_tokens, temperature
                    )
                elif provider == "gemini":
                    response = await self._call_gemini(
                        messages, system_prompt, max_tokens, temperature
                    )
                elif provider == "azure":
                    response = await self._call_azure(
                        messages, system_prompt, max_tokens, temperature
                    )
                
                text = self._extract_response_text(provider, response)
                latency_ms = (time.time() - start_time) * 1000
                
                logger.info(f"Fallback successful with {provider}")
                
                return {
                    "text": text,
                    "provider": provider,
                    "model": self._get_model_name(provider),
                    "latency_ms": latency_ms,
                    "fallback": True
                }
                
            except Exception as e:
                logger.error(f"Fallback {provider} also failed: {e}")
                continue
        
        raise RuntimeError("All LLM providers failed")
    
    def _get_model_name(self, provider: str) -> str:
        """Get the model name for a provider"""
        model_map = {
            "claude": settings.CLAUDE_MODEL,
            "openai": settings.OPENAI_MODEL,
            "gemini": settings.GEMINI_MODEL,
            "azure": settings.AZURE_OPENAI_DEPLOYMENT
        }
        return model_map.get(provider, "unknown")
    
    def _get_default_system_prompt(self, task_type: TaskType) -> str:
        """Get default system prompt for task type"""
        prompts = {
            TaskType.CLAIM_TRIAGE: """You are an expert insurance claims analyst specializing in claim triage and classification.
Your role is to analyze First Notice of Loss (FNOL) information and provide structured investigation guidance.
Be thorough, professional, and focus on actionable insights that help claims handlers efficiently investigate claims.
Always consider coverage implications, liability factors, and potential red flags.""",

            TaskType.QUESTION_GENERATION: """You are an experienced claims investigator who specializes in developing comprehensive interview questions.
Generate questions that help uncover liability, assess damages, and identify coverage issues.
Questions should be clear, non-leading, and designed to elicit detailed responses.
Consider the specific claim type and tailor questions appropriately.""",

            TaskType.COVERAGE_ANALYSIS: """You are a coverage specialist with expertise in insurance policy analysis.
Analyze claims against policy terms to identify coverage issues, exclusions, and conditions.
Highlight potential coverage defenses, late notice issues, and other red flags.
Provide clear, actionable guidance while noting this is for educational purposes only.""",

            TaskType.FILE_NOTES: """You are a senior claims professional who writes excellent file documentation.
Create clear, professional claim notes that document investigation activities, findings, and next steps.
Notes should be concise yet comprehensive, suitable for regulatory review.
Follow best practices for claims documentation.""",

            TaskType.EXTRACTION: """You are a data extraction specialist.
Extract structured information from unstructured text accurately and completely.
Return data in clean, well-organized JSON format.
Flag any ambiguous or missing information.""",

            TaskType.GENERAL: """You are an AI assistant specializing in insurance claims investigation.
Provide helpful, accurate, and professional responses to claims-related questions.
Focus on practical guidance while noting limitations and the need for professional judgment."""
        }
        
        return prompts.get(task_type, prompts[TaskType.GENERAL])
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Mock responses for development without API keys
MOCK_RESPONSES = {
    TaskType.CLAIM_TRIAGE: """Based on the FNOL analysis, here is the claim triage:

**Claim Classification:** Auto Bodily Injury (BI)
**Confidence:** 0.92
**Severity:** Moderate to High
**Complexity:** Moderate

**Immediate Actions (24-48 hours):**
1. Contact claimant to obtain recorded statement
2. Contact insured for their version of events
3. Request police report
4. Send medical authorization forms

**Key Concerns:**
- Multiple parties involved
- Injuries reported at scene
- Potential comparative negligence issues

**Documents to Request:**
- Police report
- Medical records and bills
- Wage verification (if lost wages claimed)
- Photos of vehicles and scene""",

    TaskType.QUESTION_GENERATION: """**Claimant Questions - Liability:**
1. Can you describe exactly what happened leading up to the accident?
2. What were you doing immediately before the impact?
3. Did you see the other vehicle before the collision?
4. What was the weather and road conditions?
5. Were there any traffic signals or signs at the location?

**Claimant Questions - Damages:**
1. What injuries did you sustain?
2. Did you seek medical treatment at the scene?
3. Which medical providers have you seen?
4. Are you still receiving treatment?
5. Have you missed any work due to this accident?

**Coverage Red Flags:**
1. When did you first notice symptoms?
2. Have you had any prior injuries to the same body parts?
3. Were you on any medications before the accident?"""
}


class MockLLMRouter(LLMRouter):
    """Mock router for development/testing without API keys"""
    
    async def complete(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL,
        **kwargs
    ) -> Dict[str, Any]:
        """Return mock response"""
        logger.info(f"[MOCK] Processing {task_type.value} task")
        
        # Simulate some latency
        await asyncio.sleep(0.5)
        
        mock_text = MOCK_RESPONSES.get(
            task_type,
            f"[MOCK RESPONSE]\n\nThis is a mock response for task type: {task_type.value}\n\nIn production, this would be processed by an LLM provider."
        )
        
        return {
            "text": mock_text,
            "provider": "mock",
            "model": "mock-v1",
            "latency_ms": 500,
            "mock": True
        }


import asyncio

# Singleton instance
_router: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get singleton LLMRouter instance"""
    global _router
    if _router is None:
        # Use mock router if no providers available
        temp_router = LLMRouter()
        if not temp_router.get_available_providers():
            logger.warning("No LLM providers configured, using mock router")
            _router = MockLLMRouter()
        else:
            _router = temp_router
    return _router