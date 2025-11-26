"""
ClaimInvestigator AI - Claim Analyzer Service
Main business logic for claims investigation workflow
"""
import logging
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.services.llm_router import get_router, TaskType, LLMRouter
from app.services.pii_redactor import get_redactor, PIIRedactor, RedactionResult
from app.models.claim_models import (
    ClaimInvestigationRequest,
    QuestionGenerationRequest,
    FileNoteRequest,
    ClaimType,
    LLMProvider,
    Priority,
    CoverageStatus,
    # Output models
    TriageResult,
    TaskItem,
    InvestigationChecklist,
    QuestionSet,
    CoverageIssue,
    CoverageAnalysis,
    FileNote
)

logger = logging.getLogger(__name__)


class ClaimAnalyzer:
    """
    Main service for analyzing insurance claims and generating
    investigation guidance, questions, and documentation.
    """
    
    def __init__(self):
        self.router: LLMRouter = get_router()
        self.redactor: PIIRedactor = get_redactor()
        
    def _build_fnol_summary(self, request: ClaimInvestigationRequest) -> str:
        """Build a summary of the FNOL for analysis"""
        fnol = request.fnol
        policy = request.policy
        
        summary = f"""
FIRST NOTICE OF LOSS SUMMARY
============================
Date of Loss: {fnol.date_of_loss}
Time of Loss: {fnol.time_of_loss or 'Not specified'}
Location: {fnol.location}
Jurisdiction: {request.jurisdiction}

INCIDENT DESCRIPTION:
{fnol.description}

REPORTED BY: {fnol.reported_by}
DATE REPORTED: {fnol.reported_date}

INJURIES: {'Yes' if fnol.injuries_reported else 'No'}
{f'Injury Details: {fnol.injury_description}' if fnol.injury_description else ''}

PROPERTY DAMAGE: {'Yes' if fnol.property_damage_reported else 'No'}
{f'Damage Details: {fnol.property_damage_description}' if fnol.property_damage_description else ''}

WITNESSES: {len(fnol.witnesses)} reported
POLICE REPORT: {fnol.police_report_number or 'Not available'}

POLICY INFORMATION:
- Policy Number: {policy.policy_number}
- Effective: {policy.effective_date} to {policy.expiration_date}
- Coverage Limits: {json.dumps(policy.coverage_limits, indent=2)}
- Deductible: ${policy.deductible or 'N/A'}
- Named Insureds: {len(policy.named_insureds)}
- Endorsements: {', '.join(policy.endorsements) if policy.endorsements else 'None'}

ADDITIONAL CONTEXT:
{request.additional_context or 'None provided'}
"""
        return summary
    
    async def analyze_claim(
        self,
        request: ClaimInvestigationRequest
    ) -> Dict[str, Any]:
        """
        Analyze a new claim and generate investigation checklist.
        
        Returns triage results and comprehensive investigation plan.
        """
        start_time = time.time()
        
        # Build summary and redact PII
        summary = self._build_fnol_summary(request)
        redaction_result = self.redactor.redact(summary)
        
        # Build the analysis prompt
        prompt = f"""Analyze this insurance claim FNOL and provide a comprehensive investigation plan.

{redaction_result.redacted_text}

Please provide your analysis in the following JSON format:
{{
    "triage": {{
        "claim_type": "auto_bi|auto_pd|gl|wc|property|professional",
        "confidence": 0.0-1.0,
        "severity_assessment": "string describing severity",
        "complexity_rating": "simple|moderate|complex",
        "recommended_handler_level": "junior|standard|senior|specialist",
        "key_concerns": ["list", "of", "concerns"]
    }},
    "immediate_tasks": [
        {{
            "task": "task description",
            "priority": "high|medium|low",
            "deadline_guidance": "within 24 hours",
            "category": "contact|document|review|legal|medical",
            "notes": "optional notes"
        }}
    ],
    "short_term_tasks": [
        // same format, for first week
    ],
    "ongoing_tasks": [
        // same format, ongoing investigation
    ],
    "documents_to_request": ["list of documents"],
    "parties_to_contact": [
        {{"party": "Claimant", "reason": "Obtain recorded statement", "priority": "high"}}
    ]
}}

Be thorough and specific to this claim type and jurisdiction ({request.jurisdiction}).
Consider coverage implications and potential red flags.
Ensure tasks are actionable and prioritized appropriately."""

        # Route to LLM
        result = await self.router.complete(
            prompt=prompt,
            task_type=TaskType.CLAIM_TRIAGE,
            preferred_provider=request.preferred_model if request.preferred_model != LLMProvider.AUTO else None,
            temperature=0.2  # Lower temperature for more consistent structured output
        )
        
        # Parse response
        try:
            # Try to extract JSON from response
            response_text = result["text"]
            
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(response_text.strip())
            
            # Build structured response
            checklist = self._build_checklist(analysis)
            
            return {
                "success": True,
                "checklist": checklist,
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "pii_redacted": bool(redaction_result.entities_found)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Return raw response as fallback
            return {
                "success": True,
                "raw_analysis": result["text"],
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "pii_redacted": bool(redaction_result.entities_found),
                "parse_warning": "Response was not valid JSON, returning raw analysis"
            }
    
    def _build_checklist(self, analysis: Dict[str, Any]) -> InvestigationChecklist:
        """Build structured InvestigationChecklist from analysis"""
        triage_data = analysis.get("triage", {})
        
        triage = TriageResult(
            claim_type=ClaimType(triage_data.get("claim_type", "auto_bi")),
            confidence=triage_data.get("confidence", 0.8),
            severity_assessment=triage_data.get("severity_assessment", "Moderate"),
            complexity_rating=triage_data.get("complexity_rating", "moderate"),
            recommended_handler_level=triage_data.get("recommended_handler_level", "standard"),
            key_concerns=triage_data.get("key_concerns", [])
        )
        
        def parse_tasks(task_list: list) -> list:
            return [
                TaskItem(
                    task=t.get("task", ""),
                    priority=Priority(t.get("priority", "medium")),
                    deadline_guidance=t.get("deadline_guidance", "As soon as possible"),
                    category=t.get("category", "general"),
                    notes=t.get("notes")
                )
                for t in task_list if t.get("task")
            ]
        
        return InvestigationChecklist(
            triage=triage,
            immediate_tasks=parse_tasks(analysis.get("immediate_tasks", [])),
            short_term_tasks=parse_tasks(analysis.get("short_term_tasks", [])),
            ongoing_tasks=parse_tasks(analysis.get("ongoing_tasks", [])),
            documents_to_request=analysis.get("documents_to_request", []),
            parties_to_contact=analysis.get("parties_to_contact", [])
        )
    
    async def generate_questions(
        self,
        request: QuestionGenerationRequest
    ) -> Dict[str, Any]:
        """Generate investigation questions for a specific party."""
        start_time = time.time()
        
        # Redact PII from summary
        redaction_result = self.redactor.redact(request.claim_summary)
        
        prompt = f"""Generate comprehensive investigation questions for a {request.party_type} 
in a {request.claim_type.value} claim.

CLAIM SUMMARY:
{redaction_result.redacted_text}

SPECIFIC ISSUES TO ADDRESS:
{chr(10).join(f'- {issue}' for issue in request.specific_issues) if request.specific_issues else 'None specified'}

Generate questions in this JSON format:
{{
    "party_type": "{request.party_type}",
    "liability_questions": [
        "Question 1 about liability/fault",
        "Question 2..."
    ],
    "damages_questions": [
        "Question 1 about damages/injuries",
        "Question 2..."
    ],
    "coverage_questions": [
        "Question 1 about coverage red flags",
        "Question 2..."
    ],
    "follow_up_triggers": [
        {{"if": "response condition", "then": "follow-up question"}}
    ]
}}

Questions should be:
- Clear and non-leading
- Specific to the claim type ({request.claim_type.value})
- Designed to elicit detailed responses
- Progressive (start broad, then specific)
Include at least 5 questions per category."""

        result = await self.router.complete(
            prompt=prompt,
            task_type=TaskType.QUESTION_GENERATION,
            preferred_provider=request.preferred_model if request.preferred_model != LLMProvider.AUTO else None
        )
        
        try:
            response_text = result["text"]
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            questions_data = json.loads(response_text.strip())
            
            questions = QuestionSet(
                party_type=questions_data.get("party_type", request.party_type),
                liability_questions=questions_data.get("liability_questions", []),
                damages_questions=questions_data.get("damages_questions", []),
                coverage_questions=questions_data.get("coverage_questions", []),
                follow_up_triggers=questions_data.get("follow_up_triggers", [])
            )
            
            return {
                "success": True,
                "questions": questions,
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            
        except json.JSONDecodeError:
            return {
                "success": True,
                "raw_questions": result["text"],
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "parse_warning": "Response was not valid JSON"
            }
    
    async def analyze_coverage(
        self,
        request: ClaimInvestigationRequest
    ) -> Dict[str, Any]:
        """Analyze coverage and liability issues for a claim."""
        start_time = time.time()
        
        summary = self._build_fnol_summary(request)
        redaction_result = self.redactor.redact(summary)
        
        prompt = f"""Analyze this claim for coverage and liability issues.

{redaction_result.redacted_text}

Provide analysis in this JSON format:
{{
    "coverage_status": "confirmed|pending|issue_identified|denied",
    "coverage_issues": [
        {{
            "issue_type": "coverage",
            "description": "description of issue",
            "severity": "high|medium|low",
            "action_required": "what to do",
            "questions_to_resolve": ["questions to answer"]
        }}
    ],
    "liability_issues": [
        // same format
    ],
    "key_coverage_points": ["points to confirm with policy"],
    "key_liability_questions": ["questions to resolve"],
    "red_flags": ["any red flags identified"],
    "recommended_reserves_range": "Initial reserve range suggestion or null"
}}

Consider:
- Policy effective dates vs date of loss
- Coverage limits and deductibles
- Named insureds and drivers
- Exclusions and endorsements
- Comparative negligence ({request.jurisdiction} law)
- Late reporting issues
- Pre-existing conditions

This is for EDUCATIONAL/TRAINING purposes - note that actual coverage determinations require licensed adjusters."""

        result = await self.router.complete(
            prompt=prompt,
            task_type=TaskType.COVERAGE_ANALYSIS,
            preferred_provider=request.preferred_model if request.preferred_model != LLMProvider.AUTO else None
        )
        
        try:
            response_text = result["text"]
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            analysis_data = json.loads(response_text.strip())
            
            def parse_issues(issues_list: list) -> list:
                return [
                    CoverageIssue(
                        issue_type=i.get("issue_type", "coverage"),
                        description=i.get("description", ""),
                        severity=i.get("severity", "medium"),
                        action_required=i.get("action_required", ""),
                        questions_to_resolve=i.get("questions_to_resolve", [])
                    )
                    for i in issues_list
                ]
            
            analysis = CoverageAnalysis(
                coverage_status=CoverageStatus(analysis_data.get("coverage_status", "pending")),
                coverage_issues=parse_issues(analysis_data.get("coverage_issues", [])),
                liability_issues=parse_issues(analysis_data.get("liability_issues", [])),
                key_coverage_points=analysis_data.get("key_coverage_points", []),
                key_liability_questions=analysis_data.get("key_liability_questions", []),
                red_flags=analysis_data.get("red_flags", []),
                recommended_reserves_range=analysis_data.get("recommended_reserves_range")
            )
            
            return {
                "success": True,
                "analysis": analysis,
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "pii_redacted": bool(redaction_result.entities_found)
            }
            
        except json.JSONDecodeError:
            return {
                "success": True,
                "raw_analysis": result["text"],
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "parse_warning": "Response was not valid JSON"
            }
    
    async def generate_file_note(
        self,
        request: FileNoteRequest
    ) -> Dict[str, Any]:
        """Generate professional file note / diary entry."""
        start_time = time.time()
        
        # Build input for redaction
        input_text = f"""
Claim: {request.claim_number}
Actions: {json.dumps(request.actions_completed)}
Contacts: {json.dumps(request.contact_summaries)}
Findings: {json.dumps(request.findings)}
Next Steps: {json.dumps(request.next_steps)}
"""
        redaction_result = self.redactor.redact(input_text)
        
        today = datetime.now().strftime("%Y-%m-%d")
        follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        prompt = f"""Generate a professional insurance claim file note.

{redaction_result.redacted_text}

Create the note in this JSON format:
{{
    "note_date": "{today}",
    "claim_number": "{request.claim_number}",
    "summary": "2-3 sentence executive summary",
    "detailed_notes": "Full detailed notes with all activities documented professionally",
    "action_plan": [
        "Next action item with target date",
        "Another action item"
    ],
    "reserve_recommendation": "Reserve recommendation if applicable, or null",
    "follow_up_date": "{follow_up}"
}}

The note should:
- Be professional and suitable for regulatory review
- Document WHO was contacted, WHAT was discussed, WHEN
- Include all relevant findings
- Have clear, prioritized next steps
- Follow claims documentation best practices"""

        result = await self.router.complete(
            prompt=prompt,
            task_type=TaskType.FILE_NOTES,
            preferred_provider=request.preferred_model if request.preferred_model != LLMProvider.AUTO else None
        )
        
        try:
            response_text = result["text"]
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            note_data = json.loads(response_text.strip())
            
            file_note = FileNote(
                note_date=note_data.get("note_date", today),
                claim_number=note_data.get("claim_number", request.claim_number),
                summary=note_data.get("summary", ""),
                detailed_notes=note_data.get("detailed_notes", ""),
                action_plan=note_data.get("action_plan", []),
                reserve_recommendation=note_data.get("reserve_recommendation"),
                follow_up_date=note_data.get("follow_up_date", follow_up)
            )
            
            return {
                "success": True,
                "file_note": file_note,
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            
        except json.JSONDecodeError:
            return {
                "success": True,
                "raw_note": result["text"],
                "model_used": f"{result['provider']}/{result['model']}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "parse_warning": "Response was not valid JSON"
            }


# Singleton instance
_analyzer: Optional[ClaimAnalyzer] = None


def get_analyzer() -> ClaimAnalyzer:
    """Get singleton ClaimAnalyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ClaimAnalyzer()
    return _analyzer