import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings
from app.models import Lead


class EmailService:
    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.sender = settings.sender_email
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """Send an email via SMTP."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.sender
            message["To"] = to_email
            message["Subject"] = subject
            
            # Attach body
            content_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, content_type))
            
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username or None,
                password=self.password or None,
                use_tls=False,
                start_tls=False
            )
            
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    async def send_outreach_email(self, lead: Lead) -> bool:
        """Send an outreach email to a lead using their drafted email."""
        if not lead.email_draft:
            print(f"No email draft for lead {lead.id}")
            return False
        
        subject = f"Quick question for {lead.name.split()[0]} at {lead.company or 'your company'}"
        
        # Add signature to email
        full_body = f"""{lead.email_draft}

--
Best regards,
AI Sales Team
"""
        
        success = await self.send_email(
            to_email=lead.email,
            subject=subject,
            body=full_body
        )
        
        if success:
            lead.status = "contacted"
        
        return success


# Singleton instance
email_service = EmailService()