from typing import List, Dict
from utils.schema import CourseRecord
from utils.logger import logger


def detect_duplicates(records: List[CourseRecord]) -> Dict[int, str]:
    """
    Detects duplicate courses in the dataset based on Institute Name and Course Name.
    Returns a dictionary mapping row_number -> duplicate_warning_message.
    """
    logger.info("Running duplicate detection...")

    seen = {}
    duplicates = {}

    for record in records:
        # Create a basic hash of institute and course
        key = (
            str(record.institute_name).lower().strip(),
            str(record.course_name).lower().strip(),
        )

        if key in seen:
            original_row = seen[key]
            duplicates[record.row_number] = f"Potential duplicate of row {original_row}"
        else:
            seen[key] = record.row_number

    logger.info(f"Found {len(duplicates)} potential duplicates.")
    return duplicates
