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
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            # Beautiful Styles
            header_font = Font(bold=True, color="FFFFFF", size=12)
            header_fill = PatternFill("solid", fgColor="4F81BD") # Professional Blue
            wrap_alignment = Alignment(wrap_text=True, vertical="top")
            thin_border = Border(bottom=Side(style='thin', color='E0E0E0'))
            
            # Format Headers
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Freeze Top Row
            worksheet.freeze_panes = "A2"
            
            # Format Columns & Rows
            for idx, col in enumerate(df.columns):
                col_letter = get_column_letter(idx + 1)
                
                # Set Breathable Column Widths
                if col in ['description', 'course_name', 'ai_summary', 'institute_name']:
                    worksheet.column_dimensions[col_letter].width = 50
                elif col == 'link':
                    worksheet.column_dimensions[col_letter].width = 40
                else:
                    worksheet.column_dimensions[col_letter].width = 20
                
                # Apply wrapping and borders to all cells
                for cell in worksheet[col_letter]:
                    if cell.row != 1:
                        cell.alignment = wrap_alignment
                        cell.border = thin_border
        logger.info(f"Saved Excel report: {excel_path}")

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved JSON report: {json_path}")

    except Exception as e:
        logger.error(f"Failed to generate reports: {e}")
