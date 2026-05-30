import aiohttp
import asyncio
import time
from typing import Tuple, Optional
from config import TIMEOUT_SECONDS, USER_AGENT
from utils.logger import logger

async def validate_link(url: str, session: aiohttp.ClientSession) -> Tuple[bool, int, str, float]:
    """
    Validates a URL using an async HTTP request.
    Returns: (is_valid, status_code, final_url, response_time_ms)
    """
    if not url or not url.startswith('http'):
        return False, 0, url, 0.0

    start_time = time.time()
    try:
        # We use a GET request instead of HEAD because some servers block HEAD or don't return full redirect chains for HEAD
        async with session.get(
            url, 
            timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
            headers={'User-Agent': USER_AGENT},
            allow_redirects=True,
            ssl=False # Ignore SSL errors for broken educational sites, but we log it
        ) as response:
            response_time_ms = (time.time() - start_time) * 1000
            final_url = str(response.url)
            status = response.status
            
            is_valid = 200 <= status < 400
            
            if not is_valid:
                logger.warning(f"Link invalid: {url} (Status: {status})")
                
            return is_valid, status, final_url, response_time_ms
            
    except asyncio.TimeoutError:
        logger.warning(f"Link timeout: {url}")
        return False, 408, url, (time.time() - start_time) * 1000
    except aiohttp.ClientError as e:
        logger.warning(f"Link error: {url} - {str(e)}")
        return False, 0, url, (time.time() - start_time) * 1000
    except Exception as e:
        logger.error(f"Unexpected error validating {url}: {e}")
        return False, 0, url, (time.time() - start_time) * 1000
