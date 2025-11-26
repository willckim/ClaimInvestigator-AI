'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  FileText,
  Search,
  MessageSquare,
  ClipboardList,
  Loader2,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Clock,
  User,
  Building,
  Car,
  HardHat,
  Home,
  Briefcase,
  Cpu,
} from 'lucide-react';
import {
  api,
  ClaimInvestigationRequest,
  QuestionGenerationRequest,
  FileNoteRequest,
  ClaimType,
  LLMProvider,
  InvestigationChecklist,
  QuestionSet,
  CoverageAnalysis,
  FileNote,
} from '@/lib/api';

// Claim type options with icons
const CLAIM_TYPES = [
  { value: 'auto_bi', label: 'Auto Bodily Injury', icon: Car },
  { value: 'auto_pd', label: 'Auto Property Damage', icon: Car },
  { value: 'gl', label: 'General Liability', icon: Building },
  { value: 'wc', label: 'Workers Compensation', icon: HardHat },
  { value: 'property', label: 'Property', icon: Home },
  { value: 'professional', label: 'Professional Liability', icon: Briefcase },
];

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

const LLM_PROVIDERS = [
  { value: 'auto', label: 'Auto (Smart Routing)', description: 'Let AI pick the best model' },
  { value: 'claude', label: 'Claude', description: 'Best for complex reasoning' },
  { value: 'openai', label: 'OpenAI GPT-4', description: 'Great for structured output' },
  { value: 'gemini', label: 'Google Gemini', description: 'Fast extraction tasks' },
  { value: 'azure', label: 'Azure OpenAI', description: 'Enterprise compliance' },
];

type TabType = 'investigate' | 'questions' | 'coverage' | 'notes';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('investigate');
  const [selectedProvider, setSelectedProvider] = useState<LLMProvider>('auto');
  
  // Results state
  const [checklist, setChecklist] = useState<InvestigationChecklist | null>(null);
  const [questions, setQuestions] = useState<QuestionSet | null>(null);
  const [coverageAnalysis, setCoverageAnalysis] = useState<CoverageAnalysis | null>(null);
  const [fileNote, setFileNote] = useState<FileNote | null>(null);
  
  // Form state for claim investigation
  const [claimForm, setClaimForm] = useState({
    // FNOL
    date_of_loss: '',
    time_of_loss: '',
    location: '',
    description: '',
    reported_by: '',
    reported_date: new Date().toISOString().split('T')[0],
    injuries_reported: false,
    injury_description: '',
    property_damage_reported: false,
    property_damage_description: '',
    // Policy
    policy_number: 'POL-DEMO-12345',
    effective_date: '2024-01-01',
    expiration_date: '2025-01-01',
    bi_limit: 100000,
    pd_limit: 50000,
    deductible: 500,
    // Claim info
    jurisdiction: 'CA',
    claim_type: '' as ClaimType | '',
    additional_context: '',
  });

  // Question generation form
  const [questionForm, setQuestionForm] = useState({
    claim_summary: '',
    claim_type: 'auto_bi' as ClaimType,
    party_type: 'claimant' as 'claimant' | 'witness' | 'insured' | 'employer',
    specific_issues: '',
  });

  // File note form
  const [noteForm, setNoteForm] = useState({
    claim_number: 'CLM-2024-00001',
    actions_completed: '',
    contacts_made: '',
    findings: '',
    next_steps: '',
  });

  // API Status
  const { data: apiStatus } = useQuery({
    queryKey: ['api-status'],
    queryFn: () => api.getStatus(),
    refetchInterval: 30000,
  });

  // Mutations
  const analyzeMutation = useMutation({
    mutationFn: (request: ClaimInvestigationRequest) => api.analyzeClaim(request),
    onSuccess: (data) => {
      if (data.success && data.checklist) {
        setChecklist(data.checklist);
        toast.success(`Analysis complete! (${data.model_used})`);
      } else {
        toast.error(data.error || 'Analysis failed');
      }
    },
    onError: (error) => {
      toast.error('Failed to analyze claim');
      console.error(error);
    },
  });

  const questionsMutation = useMutation({
    mutationFn: (request: QuestionGenerationRequest) => api.generateQuestions(request),
    onSuccess: (data) => {
      if (data.success && data.questions) {
        setQuestions(data.questions);
        toast.success(`Questions generated! (${data.model_used})`);
      } else {
        toast.error(data.error || 'Question generation failed');
      }
    },
    onError: (error) => {
      toast.error('Failed to generate questions');
      console.error(error);
    },
  });

  const coverageMutation = useMutation({
    mutationFn: (request: ClaimInvestigationRequest) => api.analyzeCoverage(request),
    onSuccess: (data) => {
      if (data.success && data.analysis) {
        setCoverageAnalysis(data.analysis);
        toast.success(`Coverage analysis complete! (${data.model_used})`);
      } else {
        toast.error(data.error || 'Coverage analysis failed');
      }
    },
    onError: (error) => {
      toast.error('Failed to analyze coverage');
      console.error(error);
    },
  });

  const noteMutation = useMutation({
    mutationFn: (request: FileNoteRequest) => api.generateFileNote(request),
    onSuccess: (data) => {
      if (data.success && data.file_note) {
        setFileNote(data.file_note);
        toast.success(`File note generated! (${data.model_used})`);
      } else {
        toast.error(data.error || 'File note generation failed');
      }
    },
    onError: (error) => {
      toast.error('Failed to generate file note');
      console.error(error);
    },
  });

  // Build request from form
  const buildClaimRequest = (): ClaimInvestigationRequest => ({
    fnol: {
      date_of_loss: claimForm.date_of_loss,
      time_of_loss: claimForm.time_of_loss || undefined,
      location: claimForm.location,
      description: claimForm.description,
      reported_by: claimForm.reported_by,
      reported_date: claimForm.reported_date,
      injuries_reported: claimForm.injuries_reported,
      injury_description: claimForm.injury_description || undefined,
      property_damage_reported: claimForm.property_damage_reported,
      property_damage_description: claimForm.property_damage_description || undefined,
      witnesses: [],
    },
    policy: {
      policy_number: claimForm.policy_number,
      effective_date: claimForm.effective_date,
      expiration_date: claimForm.expiration_date,
      coverage_limits: {
        bi_per_person: claimForm.bi_limit,
        bi_per_accident: claimForm.bi_limit * 3,
        pd: claimForm.pd_limit,
      },
      deductible: claimForm.deductible,
      named_insureds: ['[INSURED_NAME]'],
      additional_insureds: [],
      endorsements: [],
    },
    jurisdiction: claimForm.jurisdiction,
    claim_type: claimForm.claim_type as ClaimType || undefined,
    additional_context: claimForm.additional_context || undefined,
    preferred_model: selectedProvider,
  });

  const handleAnalyzeClaim = () => {
    if (!claimForm.description || !claimForm.date_of_loss || !claimForm.location) {
      toast.error('Please fill in required fields');
      return;
    }
    analyzeMutation.mutate(buildClaimRequest());
  };

  const handleAnalyzeCoverage = () => {
    if (!claimForm.description || !claimForm.date_of_loss) {
      toast.error('Please fill in claim details first');
      return;
    }
    coverageMutation.mutate(buildClaimRequest());
  };

  const handleGenerateQuestions = () => {
    if (!questionForm.claim_summary) {
      toast.error('Please provide a claim summary');
      return;
    }
    questionsMutation.mutate({
      claim_summary: questionForm.claim_summary,
      claim_type: questionForm.claim_type,
      party_type: questionForm.party_type,
      specific_issues: questionForm.specific_issues.split('\n').filter(Boolean),
      preferred_model: selectedProvider,
    });
  };

  const handleGenerateNote = () => {
    if (!noteForm.actions_completed) {
      toast.error('Please list actions completed');
      return;
    }
    noteMutation.mutate({
      claim_number: noteForm.claim_number,
      actions_completed: noteForm.actions_completed.split('\n').filter(Boolean),
      contact_summaries: noteForm.contacts_made.split('\n').filter(Boolean).map(c => ({
        party: 'Contact',
        summary: c,
      })),
      findings: noteForm.findings.split('\n').filter(Boolean),
      next_steps: noteForm.next_steps.split('\n').filter(Boolean),
      preferred_model: selectedProvider,
    });
  };

  const tabs = [
    { id: 'investigate', label: 'Investigate Claim', icon: Search },
    { id: 'questions', label: 'Generate Questions', icon: MessageSquare },
    { id: 'coverage', label: 'Coverage Analysis', icon: AlertTriangle },
    { id: 'notes', label: 'File Notes', icon: FileText },
  ];

  const isLoading = analyzeMutation.isPending || questionsMutation.isPending || 
                    coverageMutation.isPending || noteMutation.isPending;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Claims Investigation Dashboard</h1>
        <p className="text-gray-600 mt-1">
          AI-powered tools for efficient claims investigation workflow
        </p>
      </div>

      {/* Model Selector */}
      <div className="card p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-brand-600" />
            <span className="font-medium text-gray-700">AI Model:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {LLM_PROVIDERS.map((provider) => (
              <button
                key={provider.value}
                onClick={() => setSelectedProvider(provider.value as LLMProvider)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedProvider === provider.value
                    ? 'bg-brand-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={provider.description}
              >
                {provider.label}
              </button>
            ))}
          </div>
          {apiStatus && (
            <div className="ml-auto flex items-center gap-2 text-sm text-gray-500">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              {apiStatus.available_models.filter(m => m.available).length} models available
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs mb-6">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={activeTab === tab.id ? 'tab-active' : 'tab'}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: Form */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">
              {activeTab === 'investigate' && 'Claim Information'}
              {activeTab === 'questions' && 'Question Parameters'}
              {activeTab === 'coverage' && 'Coverage Review'}
              {activeTab === 'notes' && 'Activity Summary'}
            </h2>
          </div>
          <div className="card-body space-y-4">
            <AnimatePresence mode="wait">
              {activeTab === 'investigate' && (
                <motion.div
                  key="investigate"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  {/* FNOL Section */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Date of Loss *</label>
                      <input
                        type="date"
                        className="form-input"
                        value={claimForm.date_of_loss}
                        onChange={(e) => setClaimForm({ ...claimForm, date_of_loss: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label">Time of Loss</label>
                      <input
                        type="time"
                        className="form-input"
                        value={claimForm.time_of_loss}
                        onChange={(e) => setClaimForm({ ...claimForm, time_of_loss: e.target.value })}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="form-label">Location of Incident *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g., Intersection of Main St & Oak Ave, Los Angeles, CA"
                      value={claimForm.location}
                      onChange={(e) => setClaimForm({ ...claimForm, location: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">Incident Description *</label>
                    <textarea
                      className="form-textarea"
                      rows={4}
                      placeholder="Describe what happened..."
                      value={claimForm.description}
                      onChange={(e) => setClaimForm({ ...claimForm, description: e.target.value })}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Reported By</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="Name of reporter"
                        value={claimForm.reported_by}
                        onChange={(e) => setClaimForm({ ...claimForm, reported_by: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label">Jurisdiction</label>
                      <select
                        className="form-select"
                        value={claimForm.jurisdiction}
                        onChange={(e) => setClaimForm({ ...claimForm, jurisdiction: e.target.value })}
                      >
                        {US_STATES.map((state) => (
                          <option key={state} value={state}>{state}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        className="w-4 h-4 text-brand-600 rounded"
                        checked={claimForm.injuries_reported}
                        onChange={(e) => setClaimForm({ ...claimForm, injuries_reported: e.target.checked })}
                      />
                      <span className="text-sm text-gray-700">Injuries Reported</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        className="w-4 h-4 text-brand-600 rounded"
                        checked={claimForm.property_damage_reported}
                        onChange={(e) => setClaimForm({ ...claimForm, property_damage_reported: e.target.checked })}
                      />
                      <span className="text-sm text-gray-700">Property Damage</span>
                    </label>
                  </div>

                  {claimForm.injuries_reported && (
                    <div>
                      <label className="form-label">Injury Description</label>
                      <textarea
                        className="form-textarea"
                        rows={2}
                        placeholder="Describe reported injuries..."
                        value={claimForm.injury_description}
                        onChange={(e) => setClaimForm({ ...claimForm, injury_description: e.target.value })}
                      />
                    </div>
                  )}

                  <div>
                    <label className="form-label">Claim Type (optional)</label>
                    <select
                      className="form-select"
                      value={claimForm.claim_type}
                      onChange={(e) => setClaimForm({ ...claimForm, claim_type: e.target.value as ClaimType })}
                    >
                      <option value="">Auto-detect</option>
                      {CLAIM_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                    <p className="form-helper">Leave blank to let AI classify the claim type</p>
                  </div>

                  <div>
                    <label className="form-label">Additional Context</label>
                    <textarea
                      className="form-textarea"
                      rows={2}
                      placeholder="Any additional notes or context..."
                      value={claimForm.additional_context}
                      onChange={(e) => setClaimForm({ ...claimForm, additional_context: e.target.value })}
                    />
                  </div>

                  <button
                    onClick={handleAnalyzeClaim}
                    disabled={isLoading}
                    className="btn-primary w-full"
                  >
                    {analyzeMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Analyze Claim & Generate Checklist
                      </>
                    )}
                  </button>
                </motion.div>
              )}

              {activeTab === 'questions' && (
                <motion.div
                  key="questions"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  <div>
                    <label className="form-label">Claim Summary *</label>
                    <textarea
                      className="form-textarea"
                      rows={4}
                      placeholder="Brief summary of the claim for question context..."
                      value={questionForm.claim_summary}
                      onChange={(e) => setQuestionForm({ ...questionForm, claim_summary: e.target.value })}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Claim Type</label>
                      <select
                        className="form-select"
                        value={questionForm.claim_type}
                        onChange={(e) => setQuestionForm({ ...questionForm, claim_type: e.target.value as ClaimType })}
                      >
                        {CLAIM_TYPES.map((type) => (
                          <option key={type.value} value={type.value}>{type.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Party to Question</label>
                      <select
                        className="form-select"
                        value={questionForm.party_type}
                        onChange={(e) => setQuestionForm({ ...questionForm, party_type: e.target.value as any })}
                      >
                        <option value="claimant">Claimant</option>
                        <option value="witness">Witness</option>
                        <option value="insured">Insured</option>
                        <option value="employer">Employer (WC)</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="form-label">Specific Issues to Address</label>
                    <textarea
                      className="form-textarea"
                      rows={3}
                      placeholder="One issue per line (optional)..."
                      value={questionForm.specific_issues}
                      onChange={(e) => setQuestionForm({ ...questionForm, specific_issues: e.target.value })}
                    />
                    <p className="form-helper">Leave blank for general questions</p>
                  </div>

                  <button
                    onClick={handleGenerateQuestions}
                    disabled={isLoading}
                    className="btn-primary w-full"
                  >
                    {questionsMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Generate Investigation Questions
                      </>
                    )}
                  </button>
                </motion.div>
              )}

              {activeTab === 'coverage' && (
                <motion.div
                  key="coverage"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-sm text-amber-800">
                      <strong>Note:</strong> This uses the claim information from the "Investigate Claim" tab.
                      Fill in the claim details there first.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">BI Limit (per person)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={claimForm.bi_limit}
                        onChange={(e) => setClaimForm({ ...claimForm, bi_limit: parseInt(e.target.value) || 0 })}
                      />
                    </div>
                    <div>
                      <label className="form-label">PD Limit</label>
                      <input
                        type="number"
                        className="form-input"
                        value={claimForm.pd_limit}
                        onChange={(e) => setClaimForm({ ...claimForm, pd_limit: parseInt(e.target.value) || 0 })}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Policy Effective</label>
                      <input
                        type="date"
                        className="form-input"
                        value={claimForm.effective_date}
                        onChange={(e) => setClaimForm({ ...claimForm, effective_date: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label">Policy Expiration</label>
                      <input
                        type="date"
                        className="form-input"
                        value={claimForm.expiration_date}
                        onChange={(e) => setClaimForm({ ...claimForm, expiration_date: e.target.value })}
                      />
                    </div>
                  </div>

                  <button
                    onClick={handleAnalyzeCoverage}
                    disabled={isLoading}
                    className="btn-primary w-full"
                  >
                    {coverageMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-4 h-4 mr-2" />
                        Analyze Coverage & Liability Issues
                      </>
                    )}
                  </button>
                </motion.div>
              )}

              {activeTab === 'notes' && (
                <motion.div
                  key="notes"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  <div>
                    <label className="form-label">Claim Number</label>
                    <input
                      type="text"
                      className="form-input"
                      value={noteForm.claim_number}
                      onChange={(e) => setNoteForm({ ...noteForm, claim_number: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">Actions Completed *</label>
                    <textarea
                      className="form-textarea"
                      rows={3}
                      placeholder="One action per line:&#10;Called claimant at 2pm&#10;Requested police report&#10;Sent medical auth forms"
                      value={noteForm.actions_completed}
                      onChange={(e) => setNoteForm({ ...noteForm, actions_completed: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">Contact Summaries</label>
                    <textarea
                      className="form-textarea"
                      rows={3}
                      placeholder="One contact per line:&#10;Claimant: Confirmed injuries to neck and back&#10;Witness: States other driver ran red light"
                      value={noteForm.contacts_made}
                      onChange={(e) => setNoteForm({ ...noteForm, contacts_made: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">Key Findings</label>
                    <textarea
                      className="form-textarea"
                      rows={2}
                      placeholder="Important findings from investigation..."
                      value={noteForm.findings}
                      onChange={(e) => setNoteForm({ ...noteForm, findings: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="form-label">Next Steps</label>
                    <textarea
                      className="form-textarea"
                      rows={2}
                      placeholder="Planned next steps..."
                      value={noteForm.next_steps}
                      onChange={(e) => setNoteForm({ ...noteForm, next_steps: e.target.value })}
                    />
                  </div>

                  <button
                    onClick={handleGenerateNote}
                    disabled={isLoading}
                    className="btn-primary w-full"
                  >
                    {noteMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Generate Professional File Note
                      </>
                    )}
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right: Results */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Results</h2>
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-brand-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                Processing...
              </div>
            )}
          </div>
          <div className="card-body">
            <AnimatePresence mode="wait">
              {/* Investigation Checklist Results */}
              {activeTab === 'investigate' && checklist && (
                <motion.div
                  key="checklist-result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* Triage */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <ClipboardList className="w-5 h-5 text-brand-600" />
                      Claim Triage
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Type</p>
                        <p className="font-medium">{checklist.triage.claim_type.replace('_', ' ').toUpperCase()}</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Confidence</p>
                        <p className="font-medium">{(checklist.triage.confidence * 100).toFixed(0)}%</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Complexity</p>
                        <p className="font-medium capitalize">{checklist.triage.complexity_rating}</p>
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Handler Level</p>
                        <p className="font-medium capitalize">{checklist.triage.recommended_handler_level}</p>
                      </div>
                    </div>
                    {checklist.triage.key_concerns.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-gray-700 mb-2">Key Concerns:</p>
                        <div className="flex flex-wrap gap-2">
                          {checklist.triage.key_concerns.map((concern, i) => (
                            <span key={i} className="badge-yellow">{concern}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Immediate Tasks */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Clock className="w-5 h-5 text-red-500" />
                      Immediate Tasks (24-48 hrs)
                    </h3>
                    <ul className="space-y-2">
                      {checklist.immediate_tasks.map((task, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <span className={`priority-${task.priority} mt-0.5`}>
                            {task.priority.charAt(0).toUpperCase()}
                          </span>
                          <div>
                            <p className="text-gray-800">{task.task}</p>
                            <p className="text-xs text-gray-500">{task.deadline_guidance}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Documents */}
                  {checklist.documents_to_request.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-brand-600" />
                        Documents to Request
                      </h3>
                      <ul className="grid grid-cols-2 gap-2">
                        {checklist.documents_to_request.map((doc, i) => (
                          <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                            <ChevronRight className="w-4 h-4 text-gray-400" />
                            {doc}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Parties to Contact */}
                  {checklist.parties_to_contact.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <User className="w-5 h-5 text-brand-600" />
                        Parties to Contact
                      </h3>
                      <ul className="space-y-2">
                        {checklist.parties_to_contact.map((party, i) => (
                          <li key={i} className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded">
                            <span className="font-medium">{party.party}</span>
                            <span className="text-gray-600">{party.reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}

              {/* Questions Results */}
              {activeTab === 'questions' && questions && (
                <motion.div
                  key="questions-result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  <div className="p-3 bg-brand-50 rounded-lg">
                    <p className="text-sm text-brand-800">
                      Questions for: <strong className="capitalize">{questions.party_type}</strong>
                    </p>
                  </div>

                  {questions.liability_questions.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Liability Questions</h3>
                      <ol className="space-y-2 list-decimal list-inside">
                        {questions.liability_questions.map((q, i) => (
                          <li key={i} className="text-sm text-gray-700">{q}</li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {questions.damages_questions.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Damages Questions</h3>
                      <ol className="space-y-2 list-decimal list-inside">
                        {questions.damages_questions.map((q, i) => (
                          <li key={i} className="text-sm text-gray-700">{q}</li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {questions.coverage_questions.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Coverage Red Flag Questions</h3>
                      <ol className="space-y-2 list-decimal list-inside">
                        {questions.coverage_questions.map((q, i) => (
                          <li key={i} className="text-sm text-gray-700">{q}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                </motion.div>
              )}

              {/* Coverage Results */}
              {activeTab === 'coverage' && coverageAnalysis && (
                <motion.div
                  key="coverage-result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  <div className={`p-3 rounded-lg ${
                    coverageAnalysis.coverage_status === 'confirmed' ? 'bg-green-50' :
                    coverageAnalysis.coverage_status === 'pending' ? 'bg-yellow-50' :
                    coverageAnalysis.coverage_status === 'issue_identified' ? 'bg-orange-50' :
                    'bg-red-50'
                  }`}>
                    <p className={`text-sm font-medium ${
                      coverageAnalysis.coverage_status === 'confirmed' ? 'text-green-800' :
                      coverageAnalysis.coverage_status === 'pending' ? 'text-yellow-800' :
                      coverageAnalysis.coverage_status === 'issue_identified' ? 'text-orange-800' :
                      'text-red-800'
                    }`}>
                      Coverage Status: {coverageAnalysis.coverage_status.replace('_', ' ').toUpperCase()}
                    </p>
                  </div>

                  {coverageAnalysis.red_flags.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                        Red Flags
                      </h3>
                      <ul className="space-y-2">
                        {coverageAnalysis.red_flags.map((flag, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-red-700">
                            <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0" />
                            {flag}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {coverageAnalysis.coverage_issues.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Coverage Issues</h3>
                      {coverageAnalysis.coverage_issues.map((issue, i) => (
                        <div key={i} className="p-3 bg-orange-50 rounded-lg mb-2">
                          <p className="font-medium text-orange-900">{issue.description}</p>
                          <p className="text-sm text-orange-700 mt-1">Action: {issue.action_required}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {coverageAnalysis.key_liability_questions.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">Key Liability Questions</h3>
                      <ul className="space-y-2">
                        {coverageAnalysis.key_liability_questions.map((q, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <span className="w-1.5 h-1.5 bg-brand-500 rounded-full mt-1.5 flex-shrink-0" />
                            {q}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}

              {/* File Note Results */}
              {activeTab === 'notes' && fileNote && (
                <motion.div
                  key="note-result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Claim: {fileNote.claim_number}</span>
                    <span>{fileNote.note_date}</span>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                      {fileNote.summary}
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Detailed Notes</h3>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg whitespace-pre-wrap">
                      {fileNote.detailed_notes}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Action Plan</h3>
                    <ul className="space-y-2">
                      {fileNote.action_plan.map((action, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm">
                          <CheckCircle className="w-4 h-4 text-brand-600" />
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3 bg-brand-50 rounded-lg text-sm">
                    <p className="text-brand-800">
                      <strong>Next Follow-up:</strong> {fileNote.follow_up_date}
                    </p>
                  </div>
                </motion.div>
              )}

              {/* Empty state */}
              {!isLoading && 
                ((activeTab === 'investigate' && !checklist) ||
                 (activeTab === 'questions' && !questions) ||
                 (activeTab === 'coverage' && !coverageAnalysis) ||
                 (activeTab === 'notes' && !fileNote)) && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Search className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-500">
                    Fill in the form and click the button to generate results
                  </p>
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}