HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://rozetka.com.ua/',
    'Origin': 'https://rozetka.com.ua',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

API_BASE = "https://common-api.rozetka.com.ua/v1/api"
PRODUCT_API_BASE = "https://product-api.rozetka.com.ua/v4"

CONNECTOR_LIMIT = 300
CONNECTOR_LIMIT_PER_HOST = 100
REQUEST_TIMEOUT = 60

BATCH_SIZE = 60
COMMENTS_PER_PAGE = 36

IMAGES_FILE = 'images.csv'
LOG_FILE = 'parser.log'
LINKS_FILE = 'links.txt'