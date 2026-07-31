import asyncio
from celery import shared_task
from playwright.async_api import async_playwright

from app.core.database import SessionLocal
from app.models.base import Record, Evidence, ValidationStatus
from app.core.celery_app import celery_app

# In production, we would use storage to save the screenshot
# from app.core.storage import storage


async def run_playwright_scraper(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # Set high timeout for slow enterprise sites
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            # Wait for content to render
            await page.wait_for_timeout(2000)

            extracted_text = await page.evaluate("document.body.innerText")
            # In a full implementation, we'd take a screenshot and grab HTML
            # screenshot_bytes = await page.screenshot(full_page=True)
            # html_content = await page.content()

            return {
                "text": extracted_text,
                "screenshot_path": "uploads/screenshots/mock_screenshot.png",  # storage.upload_file(...)
                "html_path": "uploads/html/mock_page.html",  # storage.upload_file(...)
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()


@shared_task(name="app.workers.scraper.tasks.scrape_url")
def scrape_url(record_id: int, url: str):
    db = SessionLocal()
    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        db.close()
        return "Record not found"

    if not url or url == "Unknown":
        record.status = ValidationStatus.BROKEN_LINK
        db.commit()
        db.close()
        return "No URL provided"

    # Run the async Playwright scraper
    result = asyncio.run(run_playwright_scraper(url))

    if "error" in result:
        record.status = ValidationStatus.BROKEN_LINK
        record.ai_summary = f"Scraping failed: {result['error']}"
        db.commit()
        db.close()
        return "Scraping failed"

    # Create Evidence Record
    evidence = Evidence(
        record_id=record.id,
        extracted_web_text=result.get("text", "")[
            :10000
        ],  # Store first 10k chars for DB size safety
        screenshot_s3_path=result.get("screenshot_path"),
        html_s3_path=result.get("html_path"),
    )
    db.add(evidence)

    record.status = ValidationStatus.PROCESSING
    db.commit()

    # Dispatch AI Validation task
    celery_app.send_task(
        "app.workers.ai_engine.tasks.validate_record",
        args=[record.id],
        queue="ai_queue",
    )

    db.close()
    return f"Scraped and queued AI validation for Record {record_id}"
