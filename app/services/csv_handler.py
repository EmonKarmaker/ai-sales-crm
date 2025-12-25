import pandas as pd
import numpy as np
from typing import List, Optional
from app.models import Lead
from app.config import settings


class CSVHandler:
    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or settings.leads_csv_path
    
    def read_leads(self) -> List[Lead]:
        """Read all leads from CSV file."""
        try:
            df = pd.read_csv(self.csv_path)
            
            leads = []
            for _, row in df.iterrows():
                lead_dict = row.to_dict()
                # Convert NaN, empty strings, and 'nan' to None
                cleaned_dict = {}
                for k, v in lead_dict.items():
                    if pd.isna(v) or v == "" or v == "nan":
                        cleaned_dict[k] = None
                    else:
                        cleaned_dict[k] = v
                
                leads.append(Lead(**cleaned_dict))
            
            return leads
        except FileNotFoundError:
            print(f"CSV file not found at {self.csv_path}")
            return []
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []
    
    def write_leads(self, leads: List[Lead]) -> bool:
        """Write all leads back to CSV file."""
        try:
            # Convert leads to list of dicts
            data = [lead.model_dump() for lead in leads]
            df = pd.DataFrame(data)
            
            # Define column order to match original CSV
            columns = [
                "id", "name", "email", "company", "job_title", 
                "industry", "company_size", "location", "persona",
                "priority", "priority_score", "priority_reason",
                "status", "email_draft", "response_category"
            ]
            df = df[columns]
            
            df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error writing CSV: {e}")
            return False
    
    def update_lead(self, lead: Lead) -> bool:
        """Update a single lead in the CSV."""
        leads = self.read_leads()
        
        for i, existing_lead in enumerate(leads):
            if existing_lead.id == lead.id:
                leads[i] = lead
                return self.write_leads(leads)
        
        return False
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Get a single lead by ID."""
        leads = self.read_leads()
        for lead in leads:
            if lead.id == lead_id:
                return lead
        return None
    
    def get_leads_by_status(self, status: str) -> List[Lead]:
        """Get all leads with a specific status."""
        leads = self.read_leads()
        return [lead for lead in leads if lead.status == status]


# Singleton instance
csv_handler = CSVHandler()