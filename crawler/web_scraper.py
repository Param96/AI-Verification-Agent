import asyncio
from typing import Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext
from utils.logger import logger
from utils.schema import CrawlResult
from config import PLAYWRIGHT_TIMEOUT, SNAPSHOTS_DIR, RETRIES

async def extract_page_content(page: Page) -> str:
    """Extracts readable text from the page."""
    # We remove script and style tags to reduce noise
    try:
        content = await page.evaluate('''() => {
            // Aggressively remove Cookie/GDPR banners and modals
            const blockSelectors = [
                '[id*="cookie"]', '[class*="cookie"]',
                '[id*="gdpr"]', '[class*="gdpr"]',
                '[id*="consent"]', '[class*="consent"]',
                '[id*="banner"]', '[class*="banner"]',
                'div[role="dialog"]', '.modal', '.overlay'
            ];
            blockSelectors.forEach(selector => {
                try {
                    document.querySelectorAll(selector).forEach(e => e.remove());
                } catch(e) {}
            });

            // Remove non-text noise
            const scripts = document.querySelectorAll('script, style, noscript, iframe, svg, header, footer');
            scripts.forEach(s => s.remove());
            
            return document.body.innerText;
        }''')
        return content.strip() if content else ""
    except Exception as e:
        logger.warning(f"Failed to extract text cleanly: {e}")
        return ""

async def scrape_url(url: str, context: BrowserContext, row_id: int) -> CrawlResult:
    """
    Scrapes a URL using Playwright.
    Takes screenshot and HTML snapshot if it fails.
    Returns CrawlResult.
    """
    if not url or not url.startswith('http'):
        return CrawlResult(error_message="Invalid URL")

    page = await context.new_page()
    
    for attempt in range(RETRIES):
        try:
            logger.debug(f"Row {row_id}: Scraping {url} (Attempt {attempt + 1})")
            response = await page.goto(url, wait_until='networkidle', timeout=PLAYWRIGHT_TIMEOUT)
            
            # Dismiss common cookie banners if possible (basic heuristic)
            try:
                await page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button, a'));
                    const acceptBtn = buttons.find(b => b.innerText.toLowerCase().includes('accept') || b.innerText.toLowerCase().includes('agree'));
                    if(acceptBtn) acceptBtn.click();
                }''')
                await asyncio.sleep(1) # wait for modal to close
            except:
                pass

            status = response.status if response else 0
            final_url = page.url
            
            text_content = await extract_page_content(page)
            
            await page.close()
            return CrawlResult(
                final_url=final_url,
                status_code=status,
                extracted_text=text_content
            )

        except Exception as e:
            logger.warning(f"Row {row_id}: Scraping failed on attempt {attempt + 1}: {str(e)}")
            if attempt == RETRIES - 1:
                # Last attempt failed, take snapshot and screenshot
                safe_url = str(row_id)
                snapshot_path = SNAPSHOTS_DIR / f"{safe_url}_failed.html"
                screenshot_path = SNAPSHOTS_DIR / f"{safe_url}_failed.png"
                
                try:
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    html_content = await page.content()
                    with open(snapshot_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                except Exception as snap_err:
                    logger.error(f"Failed to save snapshots for {row_id}: {snap_err}")

                await page.close()
                return CrawlResult(
                    final_url=url,
                    error_message=str(e),
                    snapshot_path=str(snapshot_path),
                    screenshot_path=str(screenshot_path)
                )
            await asyncio.sleep(2 ** attempt) # Exponential backoff

    await page.close()
    return CrawlResult(error_message="Exhausted retries")
