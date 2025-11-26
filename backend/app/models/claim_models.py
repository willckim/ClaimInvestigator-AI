"""
ClaimInvestigator AI - Data Models
Pydantic models for claims investigation workflow
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ===================
# Enums
# ===================

class ClaimType(str, Enum):
    """Supported claim types"""
    AUTO_BI = "auto_bi"          # Auto Bodily Injury
    AUTO_PD = "auto_pd"          # Auto Property Damage
    GL = "gl"                     # General Liability
    WC = "wc"                     # Workers Compensation
    PROPERTY = "property"         # Property Claims
    PROFESSIONAL = "professional" # Professional Liability


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    AZURE = "azure"
    AUTO = "auto"  # Let the router decide


class Priority(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CoverageStatus(str, Enum):
    """Coverage evaluation status"""
    CONFIRMED = "confirmed"
    PENDING = "pending"
    ISSUE_IDENTIFIED = "issue_identified"
    DENIED = "denied"


# ===================
# Input Models
# ===================

class PolicyInfo(BaseModel):
    """Policy information structure"""
    policy_number: str = Field(..., description="Policy number (will be redacted)")
    effective_date: str = Field(..., description="Policy effective date")
    expiration_date: str = Field(..., description="Policy expiration date")
    coverage_limits: Dict[str, Any] = Field(
        default_factory=dict,
        description="Coverage limits (e.g., {'bi_per_person': 100000, 'bi_per_accident': 300000})"
    )
    deductible: Optional[float] = Field(None, description="Deductible amount")
    named_insureds: List[str] = Field(default_factory=list, description="Named insureds (will be redacted)")
    additional_insureds: List[str] = Field(default_factory=list, description="Additional insureds")
    endorsements: List[str] = Field(default_factory=list, description="Policy endorsements")


class FNOLInput(BaseModel):
    """First Notice of Loss input structure"""
    claim_number: Optional[str] = Field(None, description="Claim number if assigned")
    date_of_loss: str = Field(..., description="Date of loss/incident")
    time_of_loss: Optional[str] = Field(None, description="Time of loss")
    location: str = Field(..., description="Location of incident")
    description: str = Field(..., description="Description of what happened")
    reported_by: str = Field(..., description="Who reported the claim")
    reported_date: str = Field(..., description="Date claim was reported")
    injuries_reported: bool = Field(False, description="Were injuries reported?")
    injury_description: Optional[str] = Field(None, description="Description of injuries if any")
    property_damage_reported: bool = Field(False, description="Was property damage reported?")
    property_damage_description: Optional[str] = Field(None, description="Description of property damage")
    witnesses: List[str] = Field(default_factory=list, description="Witness names (will be redacted)")
    police_report_number: Optional[str] = Field(None, description="Police report number if available")


class ClaimInvestigationRequest(BaseModel):
    """Main request model for claim investigation"""
    fnol: FNOLInput = Field(..., description="First Notice of Loss information")
    policy: PolicyInfo = Field(..., description="Policy information")
    jurisdiction: str = Field(..., description="State jurisdiction (2-letter code)")
    claim_type: Optional[ClaimType] = Field(None, description="Claim type if known, otherwise will be classified")
    additional_context: Optional[str] = Field(None, description="Any additional context or notes")
    preferred_model: LLMProvider = Field(
        LLMProvider.AUTO,
        description="Preferred LLM provider (auto = smart routing)"
    )


class QuestionGenerationRequest(BaseModel):
    """Request for generating investigation questions"""
    claim_summary: str = Field(..., description="Summary of the claim")
    claim_type: ClaimType = Field(..., description="Type of claim")
    party_type: str = Field(..., description="Party to question: claimant, witness, insured, employer")
    specific_issues: List[str] = Field(default_factory=list, description="Specific issues to address")
    preferred_model: LLMProvider = Field(LLMProvider.AUTO)


class FileNoteRequest(BaseModel):
    """Request for generating file notes"""
    claim_number: str = Field(..., description="Claim number")
    actions_completed: List[str] = Field(..., description="List of actions completed")
    contact_summaries: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Summaries of contacts made (e.g., {'party': 'claimant', 'summary': '...'})"
    )
    findings: List[str] = Field(default_factory=list, description="Key findings")
    next_steps: List[str] = Field(default_factory=list, description="Planned next steps")
    preferred_model: LLMProvider = Field(LLMProvider.AUTO)


# ===================
# Output Models
# ===================

class TaskItem(BaseModel):
    """Individual task in investigation checklist"""
    task: str = Field(..., description="Task description")
    priority: Priority = Field(..., description="Task priority")
    deadline_guidance: str = Field(..., description="Suggested deadline or timing")
    category: str = Field(..., description="Task category (contact, document, review, etc.)")
    notes: Optional[str] = Field(None, description="Additional notes")


class TriageResult(BaseModel):
    """Result of claim triage and classification"""
    claim_type: ClaimType = Field(..., description="Classified claim type")
    confidence: float = Field(..., description="Classification confidence (0-1)")
    severity_assessment: str = Field(..., description="Initial severity assessment")
    complexity_rating: str = Field(..., description="Complexity rating (simple, moderate, complex)")
    recommended_handler_level: str = Field(..., description="Recommended handler experience level")
    key_concerns: List[str] = Field(default_factory=list, description="Initial key concerns identified")


class InvestigationChecklist(BaseModel):
    """Complete investigation checklist"""
    triage: TriageResult = Field(..., description="Triage results")
    immediate_tasks: List[TaskItem] = Field(..., description="Tasks for first 24-48 hours")
    short_term_tasks: List[TaskItem] = Field(..., description="Tasks for first week")
    ongoing_tasks: List[TaskItem] = Field(..., description="Ongoing investigation tasks")
    documents_to_request: List[str] = Field(..., description="Documents to request")
    parties_to_contact: List[Dict[str, str]] = Field(..., description="Parties to contact with reason")


class QuestionSet(BaseModel):
    """Set of investigation questions for a party"""
    party_type: str = Field(..., description="Type of party (claimant, witness, etc.)")
    liability_questions: List[str] = Field(..., description="Questions related to liability")
    damages_questions: List[str] = Field(..., description="Questions related to damages")
    coverage_questions: List[str] = Field(..., description="Questions related to coverage red flags")
    follow_up_triggers: List[Dict[str, str]] = Field(
        default_factory=list,
        description="If-then follow-up question triggers"
    )


class CoverageIssue(BaseModel):
    """Identified coverage or liability issue"""
    issue_type: str = Field(..., description="Type of issue (coverage, liability, damages)")
    description: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity (high, medium, low)")
    action_required: str = Field(..., description="Action required to resolve")
    questions_to_resolve: List[str] = Field(..., description="Questions that need answers")


class CoverageAnalysis(BaseModel):
    """Coverage and liability analysis result"""
    coverage_status: CoverageStatus = Field(..., description="Overall coverage status")
    coverage_issues: List[CoverageIssue] = Field(default_factory=list, description="Coverage issues identified")
    liability_issues: List[CoverageIssue] = Field(default_factory=list, description="Liability issues identified")
    key_coverage_points: List[str] = Field(..., description="Key coverage points to confirm")
    key_liability_questions: List[str] = Field(..., description="Key liability questions to resolve")
    red_flags: List[str] = Field(default_factory=list, description="Red flags identified")
    recommended_reserves_range: Optional[str] = Field(None, description="Initial reserve range suggestion")


class FileNote(BaseModel):
    """Generated file note / diary entry"""
    note_date: str = Field(..., description="Date of note")
    claim_number: str = Field(..., description="Claim number")
    summary: str = Field(..., description="Professional summary of activities")
    detailed_notes: str = Field(..., description="Detailed notes with all information")
    action_plan: List[str] = Field(..., description="Next action items with dates")
    reserve_recommendation: Optional[str] = Field(None, description="Reserve recommendation if applicable")
    follow_up_date: str = Field(..., description="Recommended follow-up date")


# ===================
# Response Wrappers
# ===================

class InvestigationResponse(BaseModel):
    """Full investigation response"""
    success: bool = Field(..., description="Whether the request was successful")
    checklist: Optional[InvestigationChecklist] = Field(None, description="Investigation checklist")
    model_used: str = Field(..., description="LLM model used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    pii_redacted: bool = Field(..., description="Whether PII was redacted")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")


class QuestionsResponse(BaseModel):
    """Questions generation response"""
    success: bool
    questions: Optional[QuestionSet] = None
    model_used: str
    processing_time_ms: float
    error: Optional[str] = None


class CoverageResponse(BaseModel):
    """Coverage analysis response"""
    success: bool
    analysis: Optional[CoverageAnalysis] = None
    model_used: str
    processing_time_ms: float
    error: Optional[str] = None


class FileNoteResponse(BaseModel):
    """File note generation response"""
    success: bool
    file_note: Optional[FileNote] = None
    model_used: str
    processing_time_ms: float
    error: Optional[str] = None


# ===================
# API Info Models
# ===================

class ModelInfo(BaseModel):
    """Information about an LLM model"""
    provider: str
    model_name: str
    available: bool
    best_for: List[str]


class APIStatus(BaseModel):
    """API status information"""
    status: str
    version: str
    available_models: List[ModelInfo]
    pii_redaction_enabled: bool
    supported_claim_types: List[str]
    supported_jurisdictions: List[str]