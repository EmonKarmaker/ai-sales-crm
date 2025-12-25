import json
from app.models import Lead, ResponseCategory
from app.services.llm_service import llm_service


CLASSIFIER_SYSTEM_PROMPT = """You are an email response classifier for sales teams.

Classify email responses into one of these categories:
- interested: Shows genuine interest, wants to learn more, asks questions
- not_interested: Declines, says no, not a fit
- needs_more_info: Asks for details, pricing, case studies
- out_of_office: Auto-reply, vacation, OOO message
- unsubscribe: Asks to be removed, stop contacting

Respond ONLY with valid JSON:
{
    "category": "interested" | "not_interested" | "needs_more_info" | "out_of_office" | "unsubscribe",
    "confidence": <number 0-100>,
    "summary": "<brief summary of the response>"
}"""


class ResponseClassifier:
    async def classify_response(self, lead: Lead, response_text: str) -> Lead:
        """Classify an email response from a lead."""
        
        prompt = f"""Classify this email response:

From: {lead.name} ({lead.email})
Company: {lead.company}

Response:
{response_text}

What category does this response fall into?"""

        try:
            response = await llm_service.generate_json(prompt, CLASSIFIER_SYSTEM_PROMPT)
            
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            data = json.loads(response)
            
            category = data.get("category", "needs_more_info")
            lead.response_category = category
            
            # Update status based on response
            if category == "interested":
                lead.status = "responded"
            elif category == "not_interested":
                lead.status = "unresponsive"
            elif category == "unsubscribe":
                lead.status = "unresponsive"
            else:
                lead.status = "responded"
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error for lead {lead.id}: {e}")
            lead.response_category = ResponseCategory.NEEDS_MORE_INFO
            lead.status = "responded"
        except Exception as e:
            print(f"Classification error for lead {lead.id}: {e}")
            lead.response_category = ResponseCategory.NEEDS_MORE_INFO
            lead.status = "responded"
        
        return lead


# Singleton instance
response_classifier = ResponseClassifier()