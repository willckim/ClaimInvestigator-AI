/**
 * ClaimInvestigator AI - API Client
 * Type-safe API client for claims investigation endpoints
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// ===================
// Types
// ===================

export type ClaimType = 'auto_bi' | 'auto_pd' | 'gl' | 'wc' | 'property' | 'professional';
export type LLMProvider = 'claude' | 'openai' | 'gemini' | 'azure' | 'auto';
export type Priority = 'high' | 'medium' | 'low';
export type CoverageStatus = 'confirmed' | 'pending' | 'issue_identified' | 'denied';

export interface PolicyInfo {
  policy_number: string;
  effective_date: string;
  expiration_date: string;
  coverage_limits: Record<string, number>;
  deductible?: number;
  named_insureds: string[];
  additional_insureds: string[];
  endorsements: string[];
}

export interface FNOLInput {
  claim_number?: string;
  date_of_loss: string;
  time_of_loss?: string;
  location: string;
  description: string;
  reported_by: string;
  reported_date: string;
  injuries_reported: boolean;
  injury_description?: string;
  property_damage_reported: boolean;
  property_damage_description?: string;
  witnesses: string[];
  police_report_number?: string;
}

export interface ClaimInvestigationRequest {
  fnol: FNOLInput;
  policy: PolicyInfo;
  jurisdiction: string;
  claim_type?: ClaimType;
  additional_context?: string;
  preferred_model?: LLMProvider;
}

export interface QuestionGenerationRequest {
  claim_summary: string;
  claim_type: ClaimType;
  party_type: 'claimant' | 'witness' | 'insured' | 'employer';
  specific_issues?: string[];
  preferred_model?: LLMProvider;
}

export interface FileNoteRequest {
  claim_number: string;
  actions_completed: string[];
  contact_summaries: Array<{ party: string; summary: string }>;
  findings: string[];
  next_steps: string[];
  preferred_model?: LLMProvider;
}

// Response types
export interface TaskItem {
  task: string;
  priority: Priority;
  deadline_guidance: string;
  category: string;
  notes?: string;
}

export interface TriageResult {
  claim_type: ClaimType;
  confidence: number;
  severity_assessment: string;
  complexity_rating: 'simple' | 'moderate' | 'complex';
  recommended_handler_level: string;
  key_concerns: string[];
}

export interface InvestigationChecklist {
  triage: TriageResult;
  immediate_tasks: TaskItem[];
  short_term_tasks: TaskItem[];
  ongoing_tasks: TaskItem[];
  documents_to_request: string[];
  parties_to_contact: Array<{ party: string; reason: string; priority?: string }>;
}

export interface QuestionSet {
  party_type: string;
  liability_questions: string[];
  damages_questions: string[];
  coverage_questions: string[];
  follow_up_triggers: Array<{ if: string; then: string }>;
}

export interface CoverageIssue {
  issue_type: string;
  description: string;
  severity: string;
  action_required: string;
  questions_to_resolve: string[];
}

export interface CoverageAnalysis {
  coverage_status: CoverageStatus;
  coverage_issues: CoverageIssue[];
  liability_issues: CoverageIssue[];
  key_coverage_points: string[];
  key_liability_questions: string[];
  red_flags: string[];
  recommended_reserves_range?: string;
}

export interface FileNote {
  note_date: string;
  claim_number: string;
  summary: string;
  detailed_notes: string;
  action_plan: string[];
  reserve_recommendation?: string;
  follow_up_date: string;
}

// API Responses
export interface InvestigationResponse {
  success: boolean;
  checklist?: InvestigationChecklist;
  model_used: string;
  processing_time_ms: number;
  pii_redacted: boolean;
  error?: string;
}

export interface QuestionsResponse {
  success: boolean;
  questions?: QuestionSet;
  model_used: string;
  processing_time_ms: number;
  error?: string;
}

export interface CoverageResponse {
  success: boolean;
  analysis?: CoverageAnalysis;
  model_used: string;
  processing_time_ms: number;
  error?: string;
}

export interface FileNoteResponse {
  success: boolean;
  file_note?: FileNote;
  model_used: string;
  processing_time_ms: number;
  error?: string;
}

export interface ModelInfo {
  provider: string;
  model_name: string;
  available: boolean;
  best_for: string[];
}

export interface APIStatus {
  status: string;
  version: string;
  available_models: ModelInfo[];
  pii_redaction_enabled: boolean;
  supported_claim_types: string[];
  supported_jurisdictions: string[];
}

// ===================
// API Client
// ===================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ClaimInvestigatorAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000, // 2 minutes for LLM responses
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ===================
  // Health Endpoints
  // ===================

  async getHealth(): Promise<{ status: string; service: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async getStatus(): Promise<APIStatus> {
    const response = await this.client.get('/health/status');
    return response.data;
  }

  // ===================
  // Claims Endpoints
  // ===================

  async analyzeClaim(request: ClaimInvestigationRequest): Promise<InvestigationResponse> {
    const response = await this.client.post('/claims/analyze', request);
    return response.data;
  }

  async generateQuestions(request: QuestionGenerationRequest): Promise<QuestionsResponse> {
    const response = await this.client.post('/claims/questions', request);
    return response.data;
  }

  async analyzeCoverage(request: ClaimInvestigationRequest): Promise<CoverageResponse> {
    const response = await this.client.post('/claims/coverage', request);
    return response.data;
  }

  async generateFileNote(request: FileNoteRequest): Promise<FileNoteResponse> {
    const response = await this.client.post('/claims/file-note', request);
    return response.data;
  }

  async getClaimTypes(): Promise<{ claim_types: Array<{ code: string; name: string; description: string }> }> {
    const response = await this.client.get('/claims/claim-types');
    return response.data;
  }

  async getAvailableModels(): Promise<{
    available_providers: string[];
    routing_strategy: Record<string, { recommended: string; reason: string }>;
    fallback_enabled: boolean;
    fallback_order: string[];
  }> {
    const response = await this.client.get('/claims/models');
    return response.data;
  }
}

// Export singleton instance
export const api = new ClaimInvestigatorAPI();

// Export class for testing
export { ClaimInvestigatorAPI };