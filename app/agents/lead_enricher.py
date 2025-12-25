import json
from app.models import Lead
from app.services.llm_service import llm_service


ENRICHMENT_SYSTEM_PROMPT = """You are a sales intelligence expert. Analyze leads and create buyer personas.

Based on the lead's job title, company, and industry, create a detailed buyer persona that helps sales teams understand:
- Their likely pain points
- What they care about
- How to approach them

Respond ONLY with valid JSON in this exact format:
{
    "persona": "<2-3 sentence buyer persona description>",
    "enriched_industry": "<industry if missing, otherwise same as input>",
    "enriched_company_size": "<company size if missing, otherwise same as input>"
}"""


class LeadEnricher:
    async def enrich_lead(self, lead: Lead) -> Lead:
        """Enrich a lead with persona and missing details."""
        prompt = f"""Create a buyer persona for this lead:

Name: {lead.name}
Email: {lead.email}
Company: {lead.company or 'Unknown'}
Job Title: {lead.job_title or 'Unknown'}
Industry: {lead.industry or 'Unknown'}
Company Size: {lead.company_size or 'Unknown'}
Location: {lead.location or 'Unknown'}

Create a helpful buyer persona and fill in any missing industry/company size based on context clues."""

        try:
            response = await llm_service.generate_json(prompt, ENRICHMENT_SYSTEM_PROMPT)
            
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            data = json.loads(response)
            
            lead.persona = data.get("persona", "")
            
            # Fill in missing fields if provided
            if not lead.industry and data.get("enriched_industry"):
                lead.industry = data.get("enriched_industry")
            if not lead.company_size and data.get("enriched_company_size"):
                lead.company_size = data.get("enriched_company_size")
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error for lead {lead.id}: {e}")
            lead.persona = "Business professional seeking solutions to improve operations."
        except Exception as e:
            print(f"Enrichment error for lead {lead.id}: {e}")
            lead.persona = "Business professional seeking solutions to improve operations."
        
        return lead


# Singleton instance
lead_enricher = LeadEnricher()