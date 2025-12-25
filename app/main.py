import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

from app.models import Lead
from app.services.csv_handler import csv_handler
from app.services.email_service import email_service
from app.services.report_generator import report_generator
from app.agents.lead_scorer import lead_scorer
from app.agents.lead_enricher import lead_enricher
from app.agents.email_drafter import email_drafter
from app.agents.response_classifier import response_classifier


app = FastAPI(
    title="AI Sales Campaign CRM",
    description="AI-powered lead scoring, enrichment, and outreach automation",
    version="1.0.0"
)


# Request/Response models
class CampaignRequest(BaseModel):
    product_description: Optional[str] = None


class ResponseClassifyRequest(BaseModel):
    lead_id: int
    response_text: str


class PipelineStatus(BaseModel):
    status: str
    total_leads: int
    processed: int
    contacted: int
    message: str


# Store pipeline status
pipeline_status = {
    "status": "idle",
    "total_leads": 0,
    "processed": 0,
    "contacted": 0,
    "message": "Ready to start"
}


@app.get("/")
async def root():
    return {
        "message": "AI Sales Campaign CRM",
        "status": "running",
        "endpoints": {
            "GET /leads": "List all leads",
            "POST /campaign/run": "Run full campaign pipeline",
            "GET /campaign/status": "Check pipeline status",
            "POST /campaign/report": "Generate campaign report",
            "POST /response/classify": "Classify a lead response"
        }
    }


@app.get("/leads", response_model=List[Lead])
async def get_leads():
    """Get all leads from CSV."""
    return csv_handler.read_leads()


@app.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: int):
    """Get a specific lead by ID."""
    lead = csv_handler.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


async def run_pipeline(product_description: Optional[str] = None):
    """Run the full campaign pipeline."""
    global pipeline_status
    
    pipeline_status["status"] = "running"
    pipeline_status["message"] = "Loading leads..."
    
    leads = csv_handler.read_leads()
    pipeline_status["total_leads"] = len(leads)
    
    processed_leads = []
    
    for i, lead in enumerate(leads):
        pipeline_status["processed"] = i + 1
        pipeline_status["message"] = f"Processing {lead.name}..."
        
        try:
            # Step 1: Score the lead
            lead = await lead_scorer.score_lead(lead)
            
            # Step 2: Enrich with persona
            lead = await lead_enricher.enrich_lead(lead)
            
            # Step 3: Draft personalized email
            lead = await email_drafter.draft_email(lead, product_description)
            
            # Step 4: Send email
            success = await email_service.send_outreach_email(lead)
            if success:
                pipeline_status["contacted"] += 1
            
            processed_leads.append(lead)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"Error processing lead {lead.id}: {e}")
            processed_leads.append(lead)
    
    # Save updated leads back to CSV
    csv_handler.write_leads(processed_leads)
    
    # Generate report
    pipeline_status["message"] = "Generating report..."
    await report_generator.save_report(processed_leads)
    
    pipeline_status["status"] = "completed"
    pipeline_status["message"] = f"Pipeline complete! {pipeline_status['contacted']}/{len(leads)} emails sent."


@app.post("/campaign/run")
async def start_campaign(
    background_tasks: BackgroundTasks,
    request: CampaignRequest = CampaignRequest()
):
    """Start the full campaign pipeline in the background."""
    global pipeline_status
    
    if pipeline_status["status"] == "running":
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    # Reset status
    pipeline_status = {
        "status": "starting",
        "total_leads": 0,
        "processed": 0,
        "contacted": 0,
        "message": "Starting pipeline..."
    }
    
    background_tasks.add_task(run_pipeline, request.product_description)
    
    return {"message": "Campaign pipeline started", "status_endpoint": "/campaign/status"}


@app.get("/campaign/status", response_model=PipelineStatus)
async def get_campaign_status():
    """Get current pipeline status."""
    return PipelineStatus(**pipeline_status)


@app.post("/campaign/report")
async def generate_report():
    """Generate a campaign report from current leads."""
    leads = csv_handler.read_leads()
    filepath = await report_generator.save_report(leads)
    return {"message": "Report generated", "filepath": filepath}


@app.post("/response/classify")
async def classify_response(request: ResponseClassifyRequest):
    """Classify an email response from a lead."""
    lead = csv_handler.get_lead_by_id(request.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead = await response_classifier.classify_response(lead, request.response_text)
    csv_handler.update_lead(lead)
    
    return {
        "lead_id": lead.id,
        "response_category": lead.response_category,
        "status": lead.status
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}