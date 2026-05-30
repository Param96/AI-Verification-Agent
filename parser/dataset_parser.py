import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from utils.logger import logger
from utils.schema import CourseRecord

# Standard column mapping to match Dataset -> CourseRecord schema
COLUMN_MAP = {
    "Sr No.": "row_number",
    "Name of Institute": "institute_name",
    "Course name": "course_name",
    "Mode": "mode",
    "Duration": "duration",
    "Fees": "fees",
    "Course Type": "course_type",
    "Field/Domain": "field_domain",
    "Certificate": "certificate",
    "Link": "link",
    "QS World University Rank": "qs_world_rank",
    "QS Continental Rank": "qs_continental_rank",
    "NIRF Rank": "nirf_rank",
    "Description": "description",
    "Language": "language",
    "Scholarship/Financial Aid": "scholarship",
    "Country": "country"
}

def parse_spreadsheet(file_path: Path) -> List[CourseRecord]:
    """Parse Excel or CSV file into a list of CourseRecords."""
    logger.info(f"Parsing spreadsheet: {file_path}")
    
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Clean column names (strip whitespace)
    df.columns = [col.strip() for col in df.columns]

    records = []
    for idx, row in df.iterrows():
        try:
            # Map columns, handling NaN/NaT
            mapped_data = {}
            for original_col, schema_col in COLUMN_MAP.items():
                if original_col in df.columns:
                    val = row[original_col]
                    mapped_data[schema_col] = str(val) if pd.notna(val) else None
                else:
                    mapped_data[schema_col] = None

            # Enforce required fields
            if mapped_data.get('row_number') is None:
                mapped_data['row_number'] = idx + 1
            else:
                mapped_data['row_number'] = int(float(mapped_data['row_number']))

            if mapped_data.get('institute_name') is None:
                mapped_data['institute_name'] = "Unknown"
            if mapped_data.get('course_name') is None:
                mapped_data['course_name'] = "Unknown"

            record = CourseRecord(**mapped_data)
            records.append(record)
        except Exception as e:
            logger.error(f"Error parsing row {idx} in {file_path}: {e}")

    logger.info(f"Successfully parsed {len(records)} records from {file_path}")
    return records
