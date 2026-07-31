import os
import tempfile
import fitz
import re
from celery import shared_task
import requests

from app.core.database import SessionLocal
from app.models.base import Job, Record, ValidationStatus
from app.core.storage import storage
from app.core.celery_app import celery_app


@shared_task(name="app.workers.ingestion.tasks.process_pdf")
def process_pdf(job_id: int, s3_path: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        db.close()
        return "Job not found"

    job.status = "PROCESSING"
    db.commit()

    # Generate a presigned URL to download the PDF securely
    presigned_url = storage.get_presigned_url(s3_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        resp = requests.get(presigned_url)
        tmp.write(resp.content)
        tmp_path = tmp.name

    extracted_records = []

    try:
        # Simplified PDF parsing logic (using PyMuPDF)
        doc = fitz.open(tmp_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            # This is a very rudimentary extraction block for demonstration.
            # In production, we migrate the advanced vision_pdf_parser.py logic here.
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if "http" in line or "www" in line:
                    # Extract URL
                    url_match = re.search(r"(https?://[^\s]+)", line)
                    if url_match:
                        extracted_records.append(
                            {
                                "url": url_match.group(1),
                                "course_name": (
                                    lines[i - 1] if i > 0 else "Unknown Course"
                                ),
                                "institute": "Unknown Institute",
                                "fees": "Unknown Fees",
                            }
                        )
        doc.close()
    finally:
        os.remove(tmp_path)

    # Save to database and trigger scraper tasks
    for data in extracted_records:
        record = Record(
            job_id=job.id,
            original_course_name=data.get("course_name"),
            original_institute=data.get("institute"),
            original_fees=data.get("fees"),
            original_url=data.get("url"),
            status=ValidationStatus.PENDING,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Dispatch Scraping task for this specific record
        celery_app.send_task(
            "app.workers.scraper.tasks.scrape_url",
            args=[record.id, record.original_url],
            queue="scraper_queue",
        )

    job.total_records = len(extracted_records)
    job.status = (
        "COMPLETED"  # Technically ingestion is completed, verification is processing
    )
    db.commit()
    db.close()

    return f"Processed {len(extracted_records)} records"
