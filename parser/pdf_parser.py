import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List
from utils.logger import logger
from utils.schema import CourseRecord
from parser.dataset_parser import parse_spreadsheet


def parse_pdf(file_path: Path) -> List[CourseRecord]:
    """Parse tables from PDF and convert them into CourseRecords."""
    logger.info(f"Parsing PDF: {file_path}")

    all_rows = []
    headers = None

    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                table = page.extract_table()
                if table:
                    # If headers not set, try to use first row of first table
                    if headers is None:
                        headers = table[0]
                        data_rows = table[1:]
                    else:
                        data_rows = table

                    # Clean data rows (replace None with empty string for pandas)
                    cleaned_rows = []
                    for row in data_rows:
                        # Ensure row length matches headers
                        row = [str(cell) if cell else "" for cell in row]
                        if len(row) < len(headers):
                            row.extend([""] * (len(headers) - len(row)))
                        elif len(row) > len(headers):
                            row = row[: len(headers)]
                        cleaned_rows.append(row)

                    all_rows.extend(cleaned_rows)

        if not headers or not all_rows:
            logger.warning(f"No valid tables found in {file_path}")
            return []

        # Convert to DataFrame to re-use spreadsheet parser logic
        df = pd.DataFrame(all_rows, columns=headers)

        # Save to temporary CSV and parse using dataset_parser
        temp_csv = file_path.with_suffix(".temp.csv")
        df.to_csv(temp_csv, index=False)

        records = parse_spreadsheet(temp_csv)

        # Cleanup
        if temp_csv.exists():
            temp_csv.unlink()

        return records

    except Exception as e:
        logger.error(f"Failed to parse PDF {file_path}: {e}")
        return []
