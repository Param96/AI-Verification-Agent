import asyncio
from typing import Optional
from openai import AsyncOpenAI
from pydantic import ValidationError
from config import DEFAULT_LLM_MODEL
from utils.logger import logger
from utils.schema import CourseRecord, CrawlResult, AIVerificationResult

# We instantiate the client lazily inside the function to avoid event loop conflicts.


async def verify_course_data(
    course: CourseRecord, web_data: CrawlResult
) -> AIVerificationResult:
    """
    Uses OpenAI to compare the dataset course record against the extracted text from the official link.
    Returns structured JSON according to AIVerificationResult schema.
    """
    # Use Local Ollama API via OpenAI compatibility layer
    client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required by SDK but ignored by Ollama
        timeout=120.0,
        max_retries=3,
    )

    if not web_data.extracted_text or len(web_data.extracted_text.strip()) < 50:
        logger.warning(
            f"Row {course.row_number}: Not enough text extracted to perform AI verification."
        )
        return AIVerificationResult(
            status="mismatch",
            confidence=1.0,
            verified_fields={
                k: False
                for k in course.model_dump().keys()
                if k not in ["row_number", "link"]
            },
            differences=[
                "Failed to extract sufficient text from the webpage or page is blank."
            ],
        )

    # Build the prompt
    dataset_info = course.model_dump(exclude={"row_number", "link"})
    dataset_str = "\n".join(
        [f"- {k}: {v}" for k, v in dataset_info.items() if v is not None]
    )

    # Truncate text to avoid token limits (keep first ~20,000 chars depending on model)
    # Using roughly 15,000 chars for safety.
    safe_text = web_data.extracted_text[:15000]

    system_prompt = (
        "You are an expert auditor for educational courses. Your job is to compare a structured dataset "
        "record with the raw text extracted from the course's official webpage. "
        "Detect exact matches, semantic matches, missing values, outdated info, and incorrect values. "
        "Pay SPECIAL ATTENTION to the 'institute_name', 'mode' (online/offline), 'country', 'skills', 'fees' and 'has_uni_logo'. "
        "You must explicitly verify if the webpage content confirms the institute name, course mode, country, skills, fees, and if the university logo or brand is present on the page (check for alt texts or headers). "
        "Strictly adhere to the following JSON schema for your output:\n"
        "{\n"
        '  "status": "match | partial | mismatch",\n'
        '  "confidence": 0.0 to 1.0,\n'
        '  "verified_fields": {"field_name": true/false},\n'
        '  "differences": ["list of strings detailing discrepancies"],\n'
        '  "suggested_corrections": [{"field_name": "Course Type", "original": "Free", "suggested": "Paid"}],\n'
        '  "verified_institute_name": "Match | Mismatch | Missing",\n'
        '  "verified_mode": "Match | Mismatch | Missing",\n'
        '  "verified_country": "Match | Mismatch | Missing",\n'
        '  "verified_skills": "Match | Mismatch | Missing",\n'
        '  "verified_fees": "Match | Mismatch | Missing",\n'
        '  "verified_logo": "Match | Mismatch | Missing"\n'
        "}\n"
        "Do NOT use objects in the differences list. Provide a simple string describing each difference. Format your differences like this: 'Field Domain: The course does not belong to the domain XYZ' or 'Duration: The duration is 6 weeks instead of 4 weeks'.\n"
        "CRITICAL INSTRUCTION: For 'verified_institute_name', 'verified_mode', 'verified_country', 'verified_skills', 'verified_fees', and 'verified_logo', you MUST output a STRING value of 'Match', 'Mismatch', or 'Missing'. NEVER output boolean true/false for these fields."
    )

    user_prompt = f"""
Dataset Record:
{dataset_str}

Extracted Webpage Text (Truncated if too long):
{safe_text}

Analyze the above information. Compare the dataset fields against what is mentioned in the webpage text.
For 'verified_fields', provide a boolean mapping for each field present in the Dataset Record. True if the webpage confirms it (or strongly implies it semantically), False if it contradicts or is completely missing.
Provide a list of 'differences' if any field contradicts. If everything matches, the list should be empty.
Set 'status' to 'match' (all fields match), 'partial' (some match, some are missing/different), or 'mismatch' (major contradictions).
Make sure you LOOK CAREFULLY at the course name and institute name. Also, carefully verify if the course domain matches the original domain provided in the Dataset Record.
"""

    try:
        completion = await client.chat.completions.create(
            model=DEFAULT_LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        import json

        raw_content = completion.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        result_dict = json.loads(raw_content.strip())
        result = AIVerificationResult(**result_dict)
        return result

    except ValidationError as e:
        logger.error(f"Row {course.row_number}: Schema validation error from AI: {e}")
        return AIVerificationResult(
            status="mismatch",
            confidence=0.0,
            verified_fields={},
            differences=[f"AI output validation error: {str(e)}"],
        )
    except Exception as e:
        logger.error(f"Row {course.row_number}: AI verification failed: {e}")
        return AIVerificationResult(
            status="mismatch",
            confidence=0.0,
            verified_fields={},
            differences=[f"AI connection error: {str(e)}"],
        )
