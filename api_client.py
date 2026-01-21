import cloudscraper
import time
import random
from typing import Optional, Any
from config import HEADERS, REQUEST_TIMEOUT
from logger import logger

class ApiClient:
    def __init__(self):
        self.scraper: Optional[cloudscraper.CloudScraper] = None
        self.proxy = "http://smart-reyqgdg7xyh6_area-UA_state-kyivcity_life-120_session-q2puPT4fKdI:rqxTnbhoAEoThFYZ@eu.smartproxy.net:3120"
        logger.info(f"Проксі: {self.proxy.split('@')[1]}")
    
    def __enter__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=10
        )
        logger.info("Сесія відкрита")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.scraper:
            self.scraper.close()
            logger.info("Сесія закрита")
    
    def get(self, url: str, as_json: bool = False, max_retries: int = 5) -> Any:
        for attempt in range(max_retries):
            try:
                delay = random.uniform(0.3, 0.8)
                time.sleep(delay)
                
                headers = HEADERS.copy()
                
                if 'rozetka.com.ua/ua/' in url and not url.startswith(('https://common-api', 'https://product-api')):
                    headers['Referer'] = 'https://rozetka.com.ua/ua/'
                
                from urllib.parse import urlparse
                parsed = urlparse(url)
                short_url = f"{parsed.netloc}{parsed.path[:50]}"
                
                logger.info(f"➤ [{attempt + 1}] {short_url}")
                
                response = self.scraper.get(
                    url,
                    headers=headers,
                    proxies={'http': self.proxy, 'https': self.proxy},
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    logger.info(f"✓ {response.status_code} | {short_url}")
                else:
                    logger.warning(f"⚠ {response.status_code} | {short_url}")
                
                if response.status_code == 403:
                    logger.warning(f"403 Forbidden [{attempt + 1}/{max_retries}]")
                    if attempt < max_retries - 1:
                        wait_time = min((3 ** attempt) + random.uniform(2, 5), 60)
                        logger.info(f"Очікування {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                
                if response.status_code == 429:
                    logger.warning(f"429 Rate Limited [{attempt + 1}/{max_retries}]")
                    if attempt < max_retries - 1:
                        wait_time = min((4 ** attempt) + random.uniform(5, 10), 120)
                        logger.info(f"Очікування {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                
                response.raise_for_status()
                
                time.sleep(random.uniform(0.1, 0.3))
                
                if as_json:
                    return response.json()
                return response.text
                    
            except cloudscraper.exceptions.CloudflareChallengeError as e:
                logger.warning(f"Cloudflare Challenge [{attempt + 1}/{max_retries}]")
                if attempt < max_retries - 1:
                    wait_time = random.uniform(5, 10)
                    logger.info(f"Очікування {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                raise
                
            except Exception as e:
                logger.error(f"Помилка: {str(e)[:50]} | {short_url}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))
                    continue
                raise
        
        raise Exception(f"Провалено після {max_retries} спроб")