from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class LeadPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    CONVERTED = "converted"
    UNRESPONSIVE = "unresponsive"


class ResponseCategory(str, Enum):
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    NEEDS_MORE_INFO = "needs_more_info"
    OUT_OF_OFFICE = "out_of_office"
    UNSUBSCRIBE = "unsubscribe"
    NO_RESPONSE = "no_response"


class Lead(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    
    # AI-enriched fields
    persona: Optional[str] = None
    priority: Optional[LeadPriority] = None
    priority_score: Optional[int] = None  # 1-100
    priority_reason: Optional[str] = None
    
    # Campaign tracking
    status: LeadStatus = LeadStatus.NEW
    email_draft: Optional[str] = None
    response_category: Optional[ResponseCategory] = None
    
    class Config:
        use_enum_values = True


class CampaignStats(BaseModel):
    total_leads: int = 0
    leads_contacted: int = 0
    leads_responded: int = 0
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    response_rate: float = 0.0