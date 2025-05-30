import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import logging
from urllib.parse import urljoin

# Setup
os.makedirs("scraped_results", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraped_results/politifact_scraper.log"),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://www.politifact.com"
LIST_URL = f"{BASE_URL}/factchecks/list/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
def get_article_urls(page_limit=3):
    """Scrape all article URLs from paginated list"""
    urls = []
    for page in range(1, page_limit + 1):
        url = f"{LIST_URL}?page={page}"
        logging.info(f"Fetching list page: {url}")
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_='m-statement__quote')
            for item in items:
                anchor = item.find('a', href=True)
                if anchor:
                    full_url = urljoin(BASE_URL, anchor['href'])
                    urls.append(full_url)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            logging.error(f"Failed to fetch list page {url}: {e}")
            continue
    logging.info(f"Found {len(urls)} article URLs")
    return urls

def scrape_article(url):
    """Scrape individual article for required fields"""
    logging.info(f"Scraping article: {url}")
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        title_tag = soup.find('h1', class_='c-title c-title--subline')
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        author_block = soup.find('div', class_='m-author__content')
        author = author_block.find('a').get_text(strip=True) if author_block and author_block.find('a') else "No author"
        date_tag = author_block.find('span', class_='m-author__date') if author_block else None
        date = date_tag.get_text(strip=True) if date_tag else "No date found"

        description = ""
        article_block = soup.find('article', class_='m-textblock')
        if article_block:
            paragraphs = article_block.find_all('p')
            description = "\n".join([p.get_text(strip=True) for p in paragraphs])

        return {
            'Title': title,
            'Author': author,
            'Date Published': date,
            'Description': description,
            'URL': url
        }

    except Exception as e:
        logging.error(f"Error scraping article {url}: {e}")
        return None

# Start scraping
if __name__ == "__main__":
    article_urls = get_article_urls(page_limit=5)
    print("Articles")
    for i in article_urls:
        print(i)
    scraped_articles = []

    for article_url in article_urls:
        data = scrape_article(article_url)
        if data:
            scraped_articles.append(data)
        time.sleep(random.uniform(1, 2))

    # Save to CSV
    df = pd.DataFrame(scraped_articles)
    csv_path = os.path.join("scraped_results", "politifact_articles.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(scraped_articles)} articles to {csv_path}")
