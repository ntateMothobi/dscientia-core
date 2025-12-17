from typing import List, Dict, Optional
from sqlalchemy.orm import Session, sessionmaker
import logging
from datetime import datetime, timezone

from .crm import CRMIngestion
from .fb_ads import FBAdsIngestion
from .whatsapp import WhatsAppIngestion
from .base import BaseIngestion
from app.services.lead_service import upsert_lead
from app.core.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)

def discover_sources() -> Dict[str, BaseIngestion]:
    sources = {}
    for adapter_class in BaseIngestion.__subclasses__():
        instance = adapter_class()
        sources[instance.source_name] = instance
    return sources

class IngestionRegistry:
    def __init__(self):
        self._sources = discover_sources()
        self.enabled_sources = set(self._sources.keys())
        self.last_summary: Optional[Dict] = None # The registry now owns its summary

    def get_available_sources(self) -> List[str]:
        return list(self._sources.keys())

    def ingest_all(self) -> Dict:
        """
        Runs the ingestion pipeline, returns a detailed summary report,
        and stores it internally.
        """
        run_timestamp = datetime.now(timezone.utc)
        overall_summary = {
            "run_at": run_timestamp.isoformat(),
            "sources": {}
        }
        
        for source_name in self.enabled_sources:
            source_instance = self._sources[source_name]
            source_summary = {"inserted": 0, "updated": 0, "skipped": 0, "failed": 0, "status": "pending"}
            db: Session = SessionLocal()
            try:
                normalized_leads = source_instance.run()
                if not normalized_leads:
                    source_summary["status"] = "success_no_data"
                    overall_summary["sources"][source_name] = source_summary
                    continue

                processed_phones = set()
                for lead_data in normalized_leads:
                    if lead_data.phone in processed_phones:
                        source_summary["skipped"] += 1
                        continue
                    
                    _, status = upsert_lead(db, lead_data)
                    if status == "inserted":
                        source_summary["inserted"] += 1
                    elif status == "updated":
                        source_summary["updated"] += 1
                    
                    processed_phones.add(lead_data.phone)

                db.commit()
                source_summary["status"] = "success"
            except Exception as e:
                db.rollback()
                source_summary["status"] = "failure"
                source_summary["failed"] = len(normalized_leads) if 'normalized_leads' in locals() else 'unknown'
                logger.error(f"Failed to ingest from {source_name}: {e}", exc_info=True)
            finally:
                db.close()
            
            overall_summary["sources"][source_name] = source_summary
        
        # Store the summary for the health service
        self.last_summary = overall_summary
        
        return overall_summary

registry = IngestionRegistry()
