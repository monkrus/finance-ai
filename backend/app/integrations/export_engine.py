import json
import csv
import io
import uuid
import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration import ExportJob

logger = logging.getLogger(__name__)

class ExportEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_csv(self, data: List[Dict[str, Any]]) -> str:
        """Stream data to CSV."""
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    async def generate_json(self, data: List[Dict[str, Any]]) -> str:
        """Stream data to JSON."""
        return json.dumps(data, indent=2)

    async def process_export(self, job_id: int, filters: Dict[str, Any]):
        """Background worker generating the file and setting the URL."""
        job = await self.db.get(ExportJob, job_id)
        if not job:
            return
            
        job.status = "running"
        await self.db.commit()

        try:
            # Mock generating data based on type
            mock_data = [
                {"id": 1, "value": "test1"},
                {"id": 2, "value": "test2"}
            ]
            
            content = ""
            if job.format == "csv":
                content = await self.generate_csv(mock_data)
            elif job.format == "json":
                content = await self.generate_json(mock_data)
            else:
                raise ValueError(f"Unsupported export format: {job.format}")

            # Simulate uploading to S3 or returning a presigned URL
            file_name = f"export_{uuid.uuid4().hex}.{job.format}"
            
            job.file_url = f"https://mock-s3-bucket.s3.amazonaws.com/{file_name}"
            job.status = "completed"

        except Exception as e:
            logger.error(f"Export {job_id} failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            
        await self.db.commit()
