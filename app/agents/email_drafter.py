from app.models import Lead
from app.services.llm_service import llm_service


EMAIL_SYSTEM_PROMPT = """You are a professional sales copywriter. Write short, personalized cold outreach emails.

Guidelines:
- Keep it under 150 words
- Personalize based on their role, company, and industry
- Focus on value, not features
- Include a clear but soft call-to-action
- Be professional but conversational
- Don't be pushy or salesy

Write ONLY the email body. No subject line, no signature, no explanations."""


class EmailDrafter:
    async def draft_email(self, lead: Lead, product_description: str = None) -> Lead:
        """Draft a personalized outreach email for a lead."""
        
        product_desc = product_description or "an AI-powered CRM solution that helps sales teams automate lead scoring, personalize outreach, and close deals faster"
        
        prompt = f"""Write a personalized cold outreach email for:

Name: {lead.name}
Job Title: {lead.job_title or 'Professional'}
Company: {lead.company or 'their company'}
Industry: {lead.industry or 'their industry'}
Persona: {lead.persona or 'Business professional'}
Priority Reason: {lead.priority_reason or 'Potential fit'}

Product/Service: {product_desc}

Write a short, personalized email that would resonate with this specific person."""

        try:
            response = await llm_service.generate(prompt, EMAIL_SYSTEM_PROMPT)
            lead.email_draft = response.strip()
        except Exception as e:
            print(f"Email drafting error for lead {lead.id}: {e}")
            lead.email_draft = f"""Hi {lead.name},

I came across {lead.company or 'your company'} and was impressed by what you're building in the {lead.industry or 'industry'} space.

I'd love to share how our AI-powered CRM solution could help your team work more efficiently. Would you be open to a brief chat?

Best regards"""
        
        return lead


# Singleton instance
email_drafter = EmailDrafter()