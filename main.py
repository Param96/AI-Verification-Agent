import asyncio
import aiohttp
import argparse
from pathlib import Path
from tqdm.asyncio import tqdm
from datetime import datetime
from playwright.async_api import async_playwright

from config import CONCURRENCY_LIMIT, BASE_DIR
from utils.logger import logger
from utils.schema import CourseRecord, FinalReportRecord
from utils.checkpoint import CheckpointManager
from parser.dataset_parser import parse_spreadsheet
from parser.vision_pdf_parser import parse_pdf_vision
from crawler.link_validator import validate_link
from crawler.web_scraper import scrape_url
from verifier.integrity_checker import IntegrityChecker
from reports.generator import generate_reports

async def process_record(
    record: CourseRecord, 
    session: aiohttp.ClientSession, 
    context, 
    semaphore: asyncio.Semaphore,
    checkpoint: CheckpointManager,
    checker: IntegrityChecker
) -> FinalReportRecord:
    
    async with semaphore:
        # Check if already processed
        if checkpoint.is_processed(record.row_number):
            logger.debug(f"Row {record.row_number} already processed. Skipping.")
            return None 

        # 1. Validate Link
        is_valid, status_code, final_url, response_time = await validate_link(record.link, session)
        link_status_msg = f"HTTP {status_code}" if status_code else "Failed/Timeout"

        if not is_valid:
            final_record = FinalReportRecord(
                row_number=record.row_number,
                institute_name=record.institute_name,
                course_name=record.course_name,
                link_status=link_status_msg,
                verification_status="BROKEN_LINK",
                confidence_score=1.0,
                original_domain=record.field_domain or "Unknown",
                predicted_domain="Unknown",
                domain_match_status="Fail",
                original_course_type=record.course_type or "Unknown",
                similarity_scores={},
                broken_link_status=True,
                ai_summary="Could not verify because the webpage could not be loaded.",
                timestamp=datetime.now().isoformat()
            )
            checkpoint.save_processed(record.row_number, final_record.model_dump())
            checkpoint.save_incorrect(record.row_number, final_record.model_dump())
            return final_record

        # 2. Scrape Webpage
        crawl_result = await scrape_url(final_url, context, record.row_number)
        crawl_result.response_time_ms = response_time
        
        # 3. Integrity Verification (ML + Rules)
        verification_result = checker.check_integrity(record, crawl_result)

        # 4. Compile Final Record
        features = verification_result.get('features') or {}
        tax_suggestion = verification_result.get('suggested_correction') or {}
        
        predicted_domain = tax_suggestion.get('suggestion', "Unknown")
        domain_match = "Match" if features.get('domain_match') == 1 else "Mismatch"

        final_record = FinalReportRecord(
            row_number=record.row_number,
            institute_name=record.institute_name,
            course_name=record.course_name,
            link_status=f"HTTP {crawl_result.status_code}",
            verification_status=verification_result['status'],
            confidence_score=verification_result['confidence'],
            original_domain=record.field_domain or "Unknown",
            predicted_domain=predicted_domain,
            domain_match_status=domain_match,
            original_course_type=record.course_type or "Unknown",
            similarity_scores={
                "course_name": features.get('course_name_similarity', 0.0),
                "institute": features.get('institute_similarity', 0.0)
            },
            broken_link_status=False,
            ai_summary=tax_suggestion.get('reason', 'Verification complete.'),
            timestamp=datetime.now().isoformat()
        )

        checkpoint.save_processed(record.row_number, final_record.model_dump())
        
        # Save to anomalies table if not strictly VALID
        if final_record.verification_status != "VALID":
            checkpoint.save_incorrect(record.row_number, final_record.model_dump())
            
        return final_record

async def main(file_path: Path):
    logger.info(f"Starting ML-Driven Data Auditing System for {file_path}")

    # Parse data
    if file_path.suffix.lower() == '.pdf':
        records = parse_pdf_vision(file_path)
    else:
        records = parse_spreadsheet(file_path)

    if not records:
        logger.error("No valid records found to process. Exiting.")
        return

    # Setup Checkpoint DB
    db_path = BASE_DIR / "logs" / f"checkpoint_{file_path.stem}.sqlite"
    checkpoint = CheckpointManager(db_path)

    # Filter out already processed records
    unprocessed = [r for r in records if not checkpoint.is_processed(r.row_number)]
    logger.info(f"Total Records: {len(records)} | Unprocessed: {len(unprocessed)}")

    if unprocessed:
        checker = IntegrityChecker()
        checker.preload_dataset(records)
        
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        
        async with aiohttp.ClientSession() as session:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
                    ignore_https_errors=True
                )
                
                tasks = []
                for record in unprocessed:
                    tasks.append(process_record(record, session, context, semaphore, checkpoint, checker))
                
                await tqdm.gather(*tasks, desc="Verifying Courses")
                
                await context.close()
                await browser.close()

    # Load ALL processed records from checkpoint DB to generate final report
    all_data_dicts = checkpoint.get_all_processed()
    final_records = [FinalReportRecord(**data) for data in all_data_dicts]
    
    # Sort back to original order
    final_records.sort(key=lambda x: x.row_number)
    
    logger.info(f"Generating final reports for {len(final_records)} records...")
    generate_reports(final_records, base_filename=f"audit_{file_path.stem}")
    logger.info("Agent execution completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ML-Driven Data Auditing System")
    parser.add_argument("file_path", type=str, help="Path to the Excel, CSV, or PDF dataset.")
    args = parser.parse_args()

    input_path = Path(args.file_path).resolve()
    if not input_path.exists():
        print(f"Error: File '{input_path}' does not exist.")
        exit(1)

    asyncio.run(main(input_path))
