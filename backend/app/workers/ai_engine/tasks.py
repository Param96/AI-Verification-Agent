import json
from celery import shared_task
from openai import OpenAI

from app.core.database import SessionLocal
from app.models.base import Record, Evidence, ValidationStatus
from app.core.config import settings

# In production, we'd preload SentenceTransformers and XGBoost globally here for the worker
# from sentence_transformers import SentenceTransformer
# encoder = SentenceTransformer('all-MiniLM-L6-v2')

def ml_fast_check(course_name: str, web_text: str) -> dict:
    # MOCK implementation of the ML fast-check layer
    # In production, this generates embeddings and runs XGBoost
    if course_name and course_name.lower() in web_text.lower():
        return {"confidence": 95, "status": ValidationStatus.VALID}
    return {"confidence": 40, "status": ValidationStatus.INVALID}

def llm_deep_reasoning(record: Record, web_text: str) -> dict:
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
    prompt = f"""
    Compare this PDF record with the website text.
    PDF Course: {record.original_course_name}
    PDF Fees: {record.original_fees}
    Website Text: {web_text[:2000]}
    
    Respond in JSON format: {{"status": "VALID"|"INVALID"|"PARTIAL_MATCH", "summary": "brief explanation"}}
    """
    try:
        response = client.chat.completions.create(
            model=settings.DEFAULT_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"status": ValidationStatus.PENDING_REVIEW, "summary": f"LLM Error: {str(e)}"}

@shared_task(name="app.workers.ai_engine.tasks.validate_record")
def validate_record(record_id: int):
    db = SessionLocal()
    record = db.query(Record).filter(Record.id == record_id).first()
    evidence = db.query(Evidence).filter(Evidence.record_id == record_id).first()
    
    if not record or not evidence:
        db.close()
        return "Missing record or evidence"

    web_text = evidence.extracted_web_text or ""
    
    # Layer 1 & 2: ML Fast-Check
    ml_result = ml_fast_check(record.original_course_name, web_text)
    
    reasoning_log = {
        "ml_confidence": ml_result["confidence"],
        "ml_status": ml_result["status"].value
    }

    # Layer 3: LLM Fallback (if ML is uncertain)
    if ml_result["confidence"] < 80:
        llm_result = llm_deep_reasoning(record, web_text)
        record.status = llm_result.get("status", ValidationStatus.PENDING_REVIEW)
        record.ai_summary = llm_result.get("summary", "")
        record.confidence_score = 90 # LLM high confidence
        reasoning_log["llm_status"] = record.status
        reasoning_log["llm_summary"] = record.ai_summary
    else:
        record.status = ml_result["status"]
        record.confidence_score = ml_result["confidence"]
        record.ai_summary = "Verified by ML Fast-Checker"

    evidence.reasoning_log = reasoning_log
    db.commit()
    db.close()
    
    return f"Validated Record {record_id} -> {record.status}"
