import json
from typing import Optional
from app.models import Lead, LeadPriority
from app.services.llm_service import llm_service


SCORING_SYSTEM_PROMPT = """You are a sales lead scoring expert. Analyze leads and assign priority scores.

Consider these factors:
- Job title seniority (C-level, VP, Director = higher priority)
- Company size (larger = higher budget potential)
- Industry fit (Technology, Healthcare, Finance = typically higher value)
- Decision-making authority based on role

Respond ONLY with valid JSON in this exact format:
{
    "priority": "high" | "medium" | "low",
    "priority_score": <number 1-100>,
    "priority_reason": "<brief explanation>"
}"""


class LeadScorer:
    async def score_lead(self, lead: Lead) -> Lead:
        """Score a single lead using AI."""
        prompt = f"""Score this sales lead:

Name: {lead.name}
Email: {lead.email}
Company: {lead.company or 'Unknown'}
Job Title: {lead.job_title or 'Unknown'}
Industry: {lead.industry or 'Unknown'}
Company Size: {lead.company_size or 'Unknown'}
Location: {lead.location or 'Unknown'}

Provide priority score and reasoning."""

        try:
            response = await llm_service.generate_json(prompt, SCORING_SYSTEM_PROMPT)
            
            # Clean response - remove markdown if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            data = json.loads(response)
            
            lead.priority = data.get("priority", "medium")
            lead.priority_score = data.get("priority_score", 50)
            lead.priority_reason = data.get("priority_reason", "")
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error for lead {lead.id}: {e}")
            print(f"Raw response: {response}")
            # Default scoring on error
            lead.priority = LeadPriority.MEDIUM
            lead.priority_score = 50
            lead.priority_reason = "Auto-scored due to processing error"
        except Exception as e:
            print(f"Scoring error for lead {lead.id}: {e}")
            lead.priority = LeadPriority.MEDIUM
            lead.priority_score = 50
            lead.priority_reason = "Auto-scored due to processing error"
        
        return lead


# Singleton instance
lead_scorer = LeadScorer()