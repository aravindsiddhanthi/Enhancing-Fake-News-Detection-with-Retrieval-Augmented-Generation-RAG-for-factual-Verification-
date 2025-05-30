import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin
import logging
import os

os.makedirs("scraped_results", exist_ok=True)  # Ensure folder exists

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraped_results/factcheck_scraper.log"),
        logging.StreamHandler()
    ]
)

class FactCheckScraper:
    def __init__(self, base_url="https://www.factcheck.org"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.articles = []

    def scrape_page(self, url):
        """Scrape a single page for articles"""
        logging.info(f"Scraping: {url}")
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise exception for HTTP errors

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article', class_='post')

            for article in articles:
                try:
                    # Extract title and URL
                    title_element = article.find('h3', class_='entry-title').find('a')
                    title = title_element.text.strip()
                    article_url = title_element['href']

                    # Extract date
                    date_element = article.find('div', class_='entry-meta')
                    date = date_element.text.strip() if date_element else "No date found"

                    # Extract description
                    description_element = article.find('div', class_='entry-content').find('p')
                    description = description_element.text.strip() if description_element else "No description found"

                    # Add to articles list
                    self.articles.append({
                        'Title': title,
                        'Description': description,
                        'Date': date,
                        'URL': article_url
                    })

                    logging.info(f"Found article: {title}")
                except Exception as e:
                    logging.error(f"Error parsing article: {e}")
                    continue

            return len(articles)
        except Exception as e:
            logging.error(f"Error scraping page {url}: {e}")
            return 0

    def scrape_multiple_pages(self, num_pages=5):
        """Scrape multiple pages using numbered URLs"""
        pages_scraped = 0

        while pages_scraped < num_pages:
            if pages_scraped == 0:
                current_url = self.base_url
            else:
                current_url = f"{self.base_url}/page/{pages_scraped + 1}/"

            articles_count = self.scrape_page(current_url)
            pages_scraped += 1

            if articles_count == 0:
                logging.warning(f"No articles found on page {pages_scraped}, stopping.")
                break

            # Add a delay to be respectful
            delay = random.uniform(1.5, 3.0)
            logging.info(f"Sleeping for {delay:.2f} seconds")
            time.sleep(delay)

        logging.info(f"Scraped {pages_scraped} pages, found {len(self.articles)} articles")
        return self.articles


    def save_to_csv(self, filename="factcheck_articles.csv"):
        """Save scraped articles to CSV in scraped_results folder"""
        if not self.articles:
            logging.warning("No articles to save")
            return False
        filepath = os.path.join("scraped_results", filename)

        df = pd.DataFrame(self.articles)
        df.to_csv(filepath, index=False)
        logging.info(f"Saved {len(self.articles)} articles to {filepath}")
        return True

# Example usage
if __name__ == "__main__":
    scraper = FactCheckScraper()

    # Scrape number of pages starting from the main page
    scraper.scrape_multiple_pages(num_pages=5)

    # Save results to both CSV and Excel
    scraper.save_to_csv()
