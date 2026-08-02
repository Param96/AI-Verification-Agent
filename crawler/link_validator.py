import aiohttp
import asyncio
import time
from typing import Tuple
from config import TIMEOUT_SECONDS, USER_AGENT
from utils.logger import logger


async def validate_link(
    url: str, session: aiohttp.ClientSession
) -> Tuple[bool, int, str, int]:
    """
    Validates a URL using an async HTTP request.
    Returns: (is_valid, status_code, final_url, response_time_ms)
    """
    if not url or not url.startswith("http"):
        return False, 0, url, 0

    start_time = time.time()
    try:
        # We use a GET request instead of HEAD because some servers block HEAD or don't return full redirect chains for HEAD
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
            headers=headers,
            allow_redirects=True,
            ssl=False,  # Ignore SSL errors for broken educational sites, but we log it
        ) as response:
            response_time_ms = int((time.time() - start_time) * 1000)
            final_url = str(response.url)
            status = response.status

            # Allow 401, 403, and 503 as they are often bot-protection/WAF that Playwright can bypass
            is_valid = (200 <= status < 400) or status in (401, 403, 503)

            if not is_valid:
                logger.warning(f"Link invalid: {url} (Status: {status})")

            return is_valid, status, final_url, response_time_ms

    except asyncio.TimeoutError:
        logger.warning(f"Link timeout: {url}")
        return False, 408, url, int((time.time() - start_time) * 1000)
    except aiohttp.ClientError as e:
        logger.warning(f"Link error: {url} - {str(e)}")
        return False, 0, url, int((time.time() - start_time) * 1000)
    except Exception as e:
        logger.error(f"Unexpected error validating {url}: {e}")
        return False, 0, url, int((time.time() - start_time) * 1000)
