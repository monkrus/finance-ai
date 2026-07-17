import csv
import json
import logging
from io import StringIO
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration import ImportJob

logger = logging.getLogger(__name__)

class ImportEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def parse_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse CSV and stream directly to JSON records."""
        records = []
        f = StringIO(content)
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
        return records

    async def parse_json(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON."""
        return json.loads(content)

    async def process_import(self, job_id: int, content: str):
        """Processes the import job in the background."""
        job = await self.db.get(ImportJob, job_id)
        if not job:
            return

        job.status = "running"
        await self.db.commit()

        try:
            records = []
            if job.file_type == "csv":
                records = await self.parse_csv(content)
            elif job.file_type == "json":
                records = await self.parse_json(content)
            else:
                raise ValueError(f"Unsupported file type: {job.file_type}")

            # For now, we mock validation and duplicate detection
            processed = 0
            failed = 0
            errors = []

            for i, record in enumerate(records):
                if not record:
                    failed += 1
                    errors.append({"row": i, "error": "Empty record"})
                    continue
                # In production, we'd map this to a target table (e.g. Transaction)
                processed += 1

            job.records_processed = processed
            job.records_failed = failed
            if errors:
                job.error_log = {"errors": errors[:100]} # Cap error log size
            
            job.status = "completed" if failed == 0 else "completed_with_errors"
            
        except Exception as e:
            logger.error(f"Import {job_id} failed: {str(e)}")
            job.status = "failed"
            job.error_log = {"fatal_error": str(e)}

        await self.db.commit()
