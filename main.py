#!/usr/bin/env python3
"""
Scraper for malaymail.com Malaysia news section
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def scrape_malaymail():
    """Scrape the malaymail.com Malaysia news page"""
    url = "https://www.malaymail.com/news/malaysia/2026/01"

    print(f"Scraping {url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("-" * 80)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Find article titles and links
        articles = soup.find_all('article')

        if not articles:
            # Try alternative selectors
            articles = soup.find_all('div', class_=['article', 'news-item', 'post'])

        print(f"Found {len(articles)} articles\n")

        scraped_articles = []
        for idx, article in enumerate(articles[:10], 1):  # Limit to first 10 articles
            # Try to find title
            title_elem = article.find(['h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else "No title found"

            # Try to find link
            link_elem = article.find('a', href=True)
            link = link_elem['href'] if link_elem else "No link"

            # Make sure link is absolute
            if link and not link.startswith('http'):
                link = f"https://www.malaymail.com{link}"

            scraped_articles.append({"title": title, "url": link})
            print(f"{idx}. {title}")
            print(f"   URL: {link}")
            print()

        # Save to JSON file in data folder
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)

        output_file = os.path.join(data_dir, f'scrape_{timestamp}.json')
        output_data = {
            "scraped_at": datetime.now().isoformat(),
            "source_url": url,
            "articles": scraped_articles
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(scraped_articles)} articles to {output_file}")
        print("-" * 80)
        print("Scraping completed successfully")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return 1
    except Exception as e:
        print(f"Error parsing page: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(scrape_malaymail())
