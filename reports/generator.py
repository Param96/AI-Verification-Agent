import pandas as pd
import json
from datetime import datetime
from typing import List
from config import REPORTS_DIR
from utils.logger import logger
from utils.schema import FinalReportRecord

def generate_reports(records: List[FinalReportRecord], base_filename: str = "audit_report"):
    """
    Generates CSV, Excel, and JSON reports from the final verified records.
    """
    if not records:
        logger.warning("No records provided to generate reports.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{base_filename}_{timestamp}"
    
    # Convert Pydantic models to dicts
    data = [r.model_dump() for r in records]
    df = pd.DataFrame(data)

    # File paths
    csv_path = REPORTS_DIR / f"{prefix}.csv"
    excel_path = REPORTS_DIR / f"{prefix}.xlsx"
    json_path = REPORTS_DIR / f"{prefix}.json"

    logger.info("Generating reports...")

    try:
        # Save CSV
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved CSV report: {csv_path}")

        # Save Excel with column width auto-adjustment
        # openpyxl must be installed
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Audit_Report')
            worksheet = writer.sheets['Audit_Report']
            from openpyxl.utils import get_column_letter
            for idx, col in enumerate(df.columns):
                # Attempt to find max width, default to length of column name
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                col_letter = get_column_letter(idx + 1)
                worksheet.column_dimensions[col_letter].width = min(max_len, 60)
        logger.info(f"Saved Excel report: {excel_path}")

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved JSON report: {json_path}")

    except Exception as e:
        logger.error(f"Failed to generate reports: {e}")
