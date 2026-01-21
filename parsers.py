import re
import time
import random
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from api_client import ApiClient
from config import API_BASE, PRODUCT_API_BASE, BATCH_SIZE, COMMENTS_PER_PAGE
from logger import logger

def parse_category_pages(client: ApiClient, base_url: str) -> int:
    html = client.get(base_url)
    match = re.search(r'Знайдено\s*(\d+)', html)
    if match:
        total = int(match.group(1))
        pages = (total + 39) // 40
        logger.info(f"Found {total} products, {pages} pages")
        return pages
    logger.warning("Could not determine page count")
    return 1

def extract_product_ids(client: ApiClient, base_url: str, pages: int) -> List[str]:
    urls = [
        base_url + (f"page={p}/" if p > 1 else "")
        for p in range(1, pages + 1)
    ]
    
    logger.info(f"Fetching product IDs from {pages} pages...")
    htmls = []
    for url in urls:
        htmls.append(client.get(url))
    
    ids = sorted({
        pid for html in htmls
        for pid in re.findall(r'/p(\d+)/', html)
    })
    
    logger.info(f"Extracted {len(ids)} unique product IDs")
    return ids

def fetch_product_details(client: ApiClient, ids: List[str]) -> Dict[str, Dict]:
    batches = [ids[i:i+BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)]
    logger.info(f"Fetching product details in {len(batches)} batches...")
    
    results = []
    for batch in batches:
        result = client.get(
            f"{API_BASE}/product/details?country=UA&lang=ua&ids={','.join(batch)}",
            as_json=True
        )
        results.append(result)
    
    details = {
        str(p['id']): p
        for result in results
        for p in result.get('data', [])
    }
    
    logger.info(f"Fetched details for {len(details)} products")
    return details

def fetch_product_main(client: ApiClient, product_id: str) -> Dict:
    url = f"{API_BASE}/pages/product/main?country=UA&lang=ua&id={product_id}&isGroup=false"
    result = client.get(url, as_json=True)
    return result.get('data', {}).get('productData', {})

def fetch_all_product_mains(client: ApiClient, ids: List[str]) -> List[Dict]:
    logger.info(f"Fetching main product data for {len(ids)} products...")
    return [fetch_product_main(client, pid) for pid in ids]

def fetch_comments_page(client: ApiClient, product_id: str, page: int, seller_id: int = 5) -> Dict:
    url = (f"{PRODUCT_API_BASE}/comments/get?country=UA&lang=ua&goods={product_id}"
           f"&limit={COMMENTS_PER_PAGE}&page={page}&sort=from_buyer&topSellerId={seller_id}&type=comment")
    result = client.get(url, as_json=True)
    return result

def fetch_all_comments(client: ApiClient, product_id: str) -> Dict:
    first_page = fetch_comments_page(client, product_id, 1)
    
    pages_count = first_page.get('data', {}).get('pages', {}).get('count', 1)
    
    if pages_count <= 1:
        return first_page
    
    logger.info(f"Product {product_id}: fetching {pages_count} comment pages")
    
    remaining_pages = []
    for page in range(2, pages_count + 1):
        remaining_pages.append(fetch_comments_page(client, product_id, page))
    
    all_comments = first_page.get('data', {}).get('comments', [])
    for page_data in remaining_pages:
        all_comments.extend(page_data.get('data', {}).get('comments', []))
    
    first_page['data']['comments'] = all_comments
    return first_page

def extract_images(main_data: Dict) -> List[str]:
    images = []
    
    product_images = (main_data.get('product') or {}).get('images', [])
    for img in product_images:
        if 'original' in img and 'url' in img['original']:
            images.append(img['original']['url'])
    
    var_params = (main_data.get('varParams') or {}).get('options', [])
    for option in var_params:
        for value in option.get('values', []):
            if 'bgImageUrl' in value and value['bgImageUrl']:
                images.append(value['bgImageUrl'])
            if 'product' in value and 'image' in value['product']:
                images.append(value['product']['image'])
    
    return list(dict.fromkeys(images))

def extract_characteristics(main_data: Dict) -> List[Dict[str, str]]:
    chars = []
    characteristics = main_data.get('characteristics') or []
    
    for group in characteristics:
        for option in (group.get('options') or []):
            title = option.get('title', '')
            values = option.get('values') or []
            for value in values:
                chars.append({
                    'назва': title,
                    'значення': value.get('title', '')
                })
    
    return chars

def clean_description(html_text: str) -> str:
    if not html_text:
        return 'Опис відсутній'
    soup = BeautifulSoup(html_text, 'lxml')
    return soup.get_text(' ', strip=True) or 'Опис відсутній'