
# AI-Enhanced Sales Campaign CRM (MVP)

An AI-powered Sales Campaign CRM that automates lead scoring, enrichment, personalized outreach, and campaign reporting using Groq's LLM API.

## Features

- **Lead Ingestion**: Read leads from CSV file
- **AI Lead Scoring**: Automatically score and prioritize leads based on job title, company size, and industry
- **Lead Enrichment**: Generate buyer personas and fill missing details
- **Personalized Email Drafting**: Create tailored outreach emails for each lead
- **Email Sending**: Send emails via SMTP (MailHog for local testing)
- **Response Classification**: Categorize email responses automatically
- **Campaign Reporting**: Generate AI-written markdown reports with stats and insights

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **LLM**: Groq API (Llama 3.1 8B)
- **Email**: aiosmtplib + MailHog
- **Data**: Pandas + CSV
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Groq API Key (free at https://console.groq.com)

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/ai-sales-crm.git
   cd ai-sales-crm
```

2. **Create `.env` file**
```bash
   cp .env.example .env
```

3. **Add your Groq API key to `.env`**
```
   GROQ_API_KEY=your_groq_api_key_here
```

4. **Run with Docker Compose**
```bash
   docker compose up --build
```

5. **Access the services**
   - API Docs: http://localhost:8000/docs
   - MailHog (Email UI): http://localhost:8025

## Usage

### Run Full Campaign Pipeline
```bash
curl -X POST "http://localhost:8000/campaign/run"
```

### Check Pipeline Status
```bash
curl "http://localhost:8000/campaign/status"
```

### Generate Report
```bash
curl -X POST "http://localhost:8000/campaign/report"
```

### View All Leads
```bash
curl "http://localhost:8000/leads"
```

### Classify Email Response
```bash
curl -X POST "http://localhost:8000/response/classify" \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 1, "response_text": "Thanks for reaching out! Id love to learn more."}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and available endpoints |
| GET | `/leads` | List all leads |
| GET | `/leads/{id}` | Get specific lead |
| POST | `/campaign/run` | Start full campaign pipeline |
| GET | `/campaign/status` | Check pipeline progress |
| POST | `/campaign/report` | Generate campaign report |
| POST | `/response/classify` | Classify email response |
| GET | `/health` | Health check |

## Project Structure
```
ai-sales-crm/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings & environment
│   ├── models.py            # Pydantic models
│   ├── agents/              # AI agents
│   │   ├── lead_scorer.py
│   │   ├── lead_enricher.py
│   │   ├── email_drafter.py
│   │   └── response_classifier.py
│   └── services/            # Core services
│       ├── csv_handler.py
│       ├── llm_service.py
│       ├── email_service.py
│       └── report_generator.py
├── data/
│   └── leads.csv            # Sample leads (25+)
├── reports/                 # Generated reports
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Pipeline Flow

1. **Load Leads** → Read from CSV
2. **Score Leads** → AI assigns priority (high/medium/low) and score (1-100)
3. **Enrich Leads** → AI generates buyer personas
4. **Draft Emails** → AI creates personalized outreach
5. **Send Emails** → Deliver via SMTP/MailHog
6. **Update CSV** → Write back enriched data
7. **Generate Report** → AI-written campaign summary

## Sample Output

### Lead Scoring
```
Lead: Sarah Johnson - VP of Engineering at TechCorp
Priority: high
Score: 92/100
Reason: C-level decision maker in large tech company
```

### Generated Email
```
Hi Sarah,

I came across TechCorp's innovative work in the tech space...
```

### Campaign Report
- Total Leads: 25
- High Priority: 40%
- Emails Sent: 25/25
- AI-generated insights and recommendations

## License

MIT