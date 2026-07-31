from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.storage import storage
from app.core.celery_app import celery_app
from app.models.base import Job
from app.schemas.base import JobResponse

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_verification_job(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported currently"
        )

    # 1. Upload to S3/MinIO
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    s3_path = storage.upload_file(file.file, unique_filename)

    # 2. Create Job in DB
    # Note: Hardcoding organization_id=1 for now until Auth is implemented
    new_job = Job(
        filename=file.filename, s3_path=s3_path, organization_id=1, status="PENDING"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 3. Dispatch Celery Task to Ingestion Queue
    celery_app.send_task(
        "app.workers.ingestion.tasks.process_pdf",
        args=[new_job.id, s3_path],
        queue="ingestion_queue",
    )

    return new_job


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
