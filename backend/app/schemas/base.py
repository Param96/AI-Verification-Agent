from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.base import ValidationStatus

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    organization_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class JobBase(BaseModel):
    filename: str
    s3_path: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    status: str
    total_records: int
    processed_records: int
    organization_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class EvidenceResponse(BaseModel):
    id: int
    screenshot_s3_path: Optional[str]
    html_s3_path: Optional[str]
    extracted_web_text: Optional[str]
    reasoning_log: Optional[Dict[str, Any]]
    class Config:
        from_attributes = True

class RecordResponse(BaseModel):
    id: int
    job_id: int
    original_course_name: Optional[str]
    original_institute: Optional[str]
    original_fees: Optional[str]
    original_url: Optional[str]
    status: ValidationStatus
    confidence_score: int
    ai_summary: Optional[str]
    evidence: Optional[EvidenceResponse]
    class Config:
        from_attributes = True
