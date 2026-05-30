"""
Example script demonstrating the refactored Vision PDF Parser.
Shows how to extract courses from scrambled PDFs and export results.
"""

from pathlib import Path
from parser.vision_pdf_parser import parse_pdf_vision
from utils.csv_exporter import export_records_to_csv
from utils.logger import logger
from config import BASE_DIR

def extract_and_export_pdf(pdf_path: str, output_csv: str = None) -> bool:
    """
    Extract courses from a PDF file and export to CSV.
    
    Args:
        pdf_path: Path to the PDF file to parse
        output_csv: Output CSV file path (defaults to generated name)
        
    Returns:
        True if successful, False otherwise
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return False
    
    # Set default output path if not provided
    if output_csv is None:
        output_csv = BASE_DIR / "reports" / f"{pdf_file.stem}_courses.csv"
    else:
        output_csv = Path(output_csv)
    
    logger.info(f"Starting PDF extraction from: {pdf_path}")
    
    # Parse the PDF
    records = parse_pdf_vision(pdf_file)
    
    if not records:
        logger.warning("No records extracted from PDF")
        return False
    
    # Export to CSV
    success = export_records_to_csv(records, output_csv)
    
    if success:
        logger.info(f"📊 Successfully extracted {len(records)} courses")
        print(f"\n✅ Extraction Complete!")
        print(f"   Courses extracted: {len(records)}")
        print(f"   Output file: {output_csv}")
        
        # Print sample records
        print(f"\n📋 Sample records (first 3):")
        for i, record in enumerate(records[:3], 1):
            print(f"\n   [{i}] {record.course_name}")
            print(f"       Institute: {record.institute_name}")
            print(f"       Mode: {record.mode}, Duration: {record.duration}")
            print(f"       Fees: {record.fees}")
            print(f"       URL: {record.link}")
    
    return success

if __name__ == "__main__":
    # Example usage
    pdf_path = "test.pdf"  # Replace with your PDF path
    
    # Extract and export
    extract_and_export_pdf(pdf_path)
