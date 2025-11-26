# ClaimInvestigator AI

<div align="center">

![ClaimInvestigator AI](https://img.shields.io/badge/ClaimInvestigator-AI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?style=flat-square&logo=typescript)

**AI-Powered Claims Investigation Workflow Assistant**

*From FNOL to Investigation Plan in Seconds*

</div>

---

## 🎯 Overview

ClaimInvestigator AI is an enterprise-grade portfolio project demonstrating how AI can transform insurance claims investigation workflows. It helps claims specialists go from raw First Notice of Loss (FNOL) data to structured investigation plans, professional file notes, and comprehensive question sets.

### Key Features

| Feature | Description |
|---------|-------------|
| **Claim Triage & Checklist** | Automatically classify claims and generate prioritized investigation to-do lists |
| **Investigation Questions** | Generate tailored questions for claimants, witnesses, insureds, and employers |
| **Coverage Issue Spotter** | Identify coverage issues, liability concerns, and red flags |
| **File Note Generator** | Create professional claim notes suitable for regulatory review |
| **Multi-Model AI Routing** | Intelligently routes to Claude, GPT-4, Gemini, or Azure OpenAI |
| **Privacy-First Design** | Automatic PII redaction before sending to external LLMs |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 14)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Triage  │  │ Questions│  │ Coverage │  │  Notes   │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
                     ┌───────▼───────┐
                     │   FastAPI     │
                     │   Backend     │
                     └───────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
      ┌───────▼───────┐ ┌────▼────┐ ┌──────▼──────┐
      │ PII Redactor  │ │  LLM    │ │   Claim     │
      │   Service     │ │ Router  │ │  Analyzer   │
      └───────────────┘ └────┬────┘ └─────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │         │         │         │         │
    ┌────▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼────┐
    │ Claude │ │ GPT-4 │ │Gemini │ │ Azure  │
    └────────┘ └───────┘ └───────┘ └────────┘
```

### Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- LiteLLM for unified LLM interface
- Pydantic for data validation
- PostgreSQL + Redis (optional)

**Frontend:**
- Next.js 14 with App Router
- TypeScript
- TailwindCSS
- React Query
- Framer Motion

**AI/ML:**
- Anthropic Claude (primary - complex reasoning)
- OpenAI GPT-4 (structured output)
- Google Gemini (fast extraction)
- Azure OpenAI (enterprise compliance)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- At least one LLM API key (Claude recommended)

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/claim-investigator-ai.git
cd claim-investigator-ai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Option 2: Docker Compose

```bash
# Configure environment
cp backend/.env.example .env
# Edit .env and add your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the application:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Recommended |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `GOOGLE_API_KEY` | Gemini API key | Optional |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | Optional |
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint URL | If using Azure |
| `DEFAULT_LLM_PROVIDER` | Default provider (claude/openai/gemini/azure) | No (default: claude) |
| `ENABLE_PII_REDACTION` | Enable PII redaction | No (default: true) |

### LLM Routing Strategy

The system intelligently routes tasks to optimal providers:

| Task Type | Recommended Provider | Reason |
|-----------|---------------------|--------|
| Claim Triage | Claude | Best for complex classification |
| Question Generation | Claude | Nuanced, comprehensive questions |
| Coverage Analysis | Claude | Strong legal/policy reasoning |
| File Notes | OpenAI | Reliable structured JSON |
| Extraction | Gemini | Fast and cost-effective |
| Enterprise Demo | Azure | Compliance-friendly |

---

## 📋 API Endpoints

### Claims Investigation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/claims/analyze` | Analyze claim and generate checklist |
| POST | `/api/v1/claims/questions` | Generate investigation questions |
| POST | `/api/v1/claims/coverage` | Analyze coverage and liability |
| POST | `/api/v1/claims/file-note` | Generate professional file note |
| GET | `/api/v1/claims/claim-types` | Get supported claim types |
| GET | `/api/v1/claims/models` | Get available LLM models |

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/status` | Detailed API status |
| GET | `/api/v1/health/ready` | Kubernetes readiness probe |

---

## 🔒 Privacy & Security

### PII Redaction

The system automatically detects and redacts sensitive information before sending to LLM providers:

- **Personal Identifiers**: Names, SSN, driver's license
- **Contact Information**: Phone numbers, email addresses, IP addresses
- **Financial Data**: Credit card numbers
- **Claim-Specific**: Claim numbers, policy numbers, medical record numbers
- **Location Data**: Addresses

Example transformation:
```
Before: "John Smith (SSN: 123-45-6789) reported the accident at 555-123-4567"
After:  "[PERSON_1] (SSN: [SSN_1]) reported the accident at [PHONE_1]"
```

### Security Best Practices

1. **API Keys**: Store in environment variables, never in code
2. **Data Retention**: Uses API endpoints (not chat UIs) for shorter retention
3. **Synthetic Data**: Sample data uses fictional names and numbers
4. **No Production Claims**: Designed for training/demo with synthetic data only

---

## 🎨 Supported Claim Types

| Code | Type | Description |
|------|------|-------------|
| `auto_bi` | Auto Bodily Injury | Personal injury from auto accidents |
| `auto_pd` | Auto Property Damage | Vehicle/property damage from auto accidents |
| `gl` | General Liability | Third-party claims (slip & fall, etc.) |
| `wc` | Workers Compensation | Workplace injuries and illness |
| `property` | Property | Property damage (fire, theft, weather) |
| `professional` | Professional Liability | E&O, malpractice claims |

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest -v

# Frontend tests
cd frontend
npm test
```

---

## 📁 Project Structure

```
claim-investigator-ai/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   │   ├── claim_analyzer.py
│   │   │   ├── llm_router.py
│   │   │   └── pii_redactor.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── dashboard/      # Main dashboard
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── lib/
│   │   └── api.ts          # Type-safe API client
│   ├── package.json
│   └── Dockerfile
├── sample_data/
│   └── sample_claims.json
├── docker-compose.yml
└── README.md
```

---

## 💼 Portfolio Value

This project demonstrates:

1. **Full-Stack Development**: Next.js 14 + FastAPI with TypeScript
2. **AI/ML Integration**: Multi-model routing with intelligent fallbacks
3. **Enterprise Architecture**: Privacy-first design, Docker deployment
4. **Domain Expertise**: Deep understanding of insurance claims workflows
5. **Production Quality**: Error handling, logging, health checks

### Interview Talking Points

> "I built a provider-agnostic LLM system that can swap vendors without rebuilding. The PII redactor ensures sensitive claimant data never leaves our environment unprotected."

> "The multi-model routing optimizes for both quality and cost—using Claude for complex reasoning tasks and Gemini for fast extraction."

---

## 📄 License

This project is for portfolio/educational purposes. Not for production claims processing.

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Open an issue or PR.

---

<div align="center">

**Built with ❤️ for the insurance industry**

[View Demo](http://localhost:3000) · [API Docs](http://localhost:8000/docs) · [Report Bug](https://github.com/yourusername/claim-investigator-ai/issues)

</div>