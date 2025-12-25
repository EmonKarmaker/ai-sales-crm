from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Groq API
    groq_api_key: str = ""
    
    # SMTP / MailHog
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_username: Optional[str] = ""
    smtp_password: Optional[str] = ""
    sender_email: str = "sales@yourcompany.com"
    
    # Paths
    leads_csv_path: str = "data/leads.csv"
    reports_path: str = "reports/"
    
    class Config:
        env_file = ".env"


settings = Settings()