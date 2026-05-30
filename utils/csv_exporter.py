import csv
from pathlib import Path
from typing import List
from utils.logger import logger
from utils.schema import CourseRecord

def export_records_to_csv(records: List[CourseRecord], output_path: Path) -> bool:
    """
    Export a list of CourseRecords to a CSV file.
    
    Args:
        records: List of CourseRecord objects to export
        output_path: Path to the output CSV file
        
    Returns:
        True if export successful, False otherwise
    """
    try:
        if not records:
            logger.warning("No records to export")
            return False
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # CSV headers matching CourseRecord fields
        headers = [
            'ID', 'Institute Name', 'Course Name', 'Mode', 'Duration', 
            'Fees', 'Course Type', 'Field/Domain', 'Certificate', 'URL',
            'QS World Rank', 'QS Continental Rank', 'NIRF Rank', 
            'Description', 'Language', 'Scholarship', 'Country'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for record in records:
                writer.writerow([
                    record.row_number,
                    record.institute_name,
                    record.course_name,
                    record.mode or '',
                    record.duration or '',
                    record.fees or '',
                    record.course_type or '',
                    record.field_domain or '',
                    record.certificate or '',
                    record.link or '',
                    record.qs_world_rank or '',
                    record.qs_continental_rank or '',
                    record.nirf_rank or '',
                    record.description or '',
                    record.language or '',
                    record.scholarship or '',
                    record.country or ''
                ])
        
        logger.info(f"✅ Exported {len(records)} records to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export records to CSV: {e}")
        return False
