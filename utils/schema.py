from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CourseRecord(BaseModel):
    """Schema representing a row from the input dataset."""
    row_number: int
    institute_name: str
    course_name: str
    mode: Optional[str] = None
    duration: Optional[str] = None
    fees: Optional[str] = None
    course_type: Optional[str] = None
    field_domain: Optional[str] = None
    certificate: Optional[str] = None
    link: Optional[str] = None
    qs_world_rank: Optional[str] = None
    qs_continental_rank: Optional[str] = None
    nirf_rank: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    scholarship: Optional[str] = None
    country: Optional[str] = None

class CrawlResult(BaseModel):
    """Schema for the result of the web crawler."""
    final_url: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    extracted_text: Optional[str] = None
    snapshot_path: Optional[str] = None
    screenshot_path: Optional[str] = None

class FinalReportRecord(BaseModel):
    """Schema for the final generated ML audit report row."""
    row_number: int
    institute_name: str
    course_name: str
    link_status: str
    verification_status: str
    confidence_score: float
    
    # Taxonomy fields
    original_domain: str
    predicted_domain: str
    domain_match_status: str
    original_course_type: str
    
    # Extra ML fields
    similarity_scores: Dict[str, float]
    broken_link_status: bool
    ai_summary: str
    timestamp: str
