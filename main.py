#!/usr/bin/env python3
"""
Multi-source scraper with pluggable URL extraction.
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

from extractors import get_extractor


def load_sources():
    """Load sources from sources.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sources_file = os.path.join(script_dir, 'sources.json')

    with open(sources_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_output_dirs(source_name):
    """Create output directory structure for a source"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, 'data', source_name)
    original_dir = os.path.join(base_dir, 'original')
    additional_dir = os.path.join(base_dir, 'additional')

    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(additional_dir, exist_ok=True)

    return original_dir, additional_dir


def scrape_url(url):
    """Scrape a URL and return structured data"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'lxml')

    # Find article titles and links
    # First try to find articles within archive container (excludes carousels/sidebars)
    archive_container = soup.find('div', class_='malaymail-news-archive')
    if archive_container:
        articles = archive_container.find_all('div', class_='article-item')
    else:
        articles = soup.find_all('article')

        if not articles:
            # Try alternative selectors
            articles = soup.find_all('div', class_='article-item')

        if not articles:
            # Fallback to other common patterns
            articles = soup.find_all('div', class_=['article', 'news-item', 'post'])

    scraped_articles = []
    for article in articles:
        # Try to find title - prefer article-title class first
        title_elem = article.find(class_='article-title')
        if title_elem:
            link_elem = title_elem.find('a', href=True)
            title = link_elem.get_text(strip=True) if link_elem else title_elem.get_text(strip=True)
            link = link_elem['href'] if link_elem else "No link"
        else:
            # Fallback to generic title search
            title_elem = article.find(['h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else "No title found"
            link_elem = article.find('a', href=True)
            link = link_elem['href'] if link_elem else "No link"

        scraped_articles.append({"title": title, "url": link})

    return {
        "scraped_at": datetime.now().isoformat(),
        "source_url": url,
        "articles": scraped_articles
    }


def scrape_additional_url(url, source_name):
    """Scrape an individual article page and return raw HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return {
        "scraped_at": datetime.now().isoformat(),
        "source_url": url,
        "html": response.text
    }


def url_to_slug(url):
    """Convert a URL to a filesystem-safe slug"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    # Replace slashes and special chars with underscores
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', path)
    # Truncate if too long
    return slug[:100] if slug else 'article'


def main():
    """Main entry point"""
    print(f"Multi-source scraper started")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    try:
        sources = load_sources()
        print(f"Loaded {len(sources)} source(s)")
        print()

        for source in sources:
            source_name = source['name']
            source_url = source['url']

            print(f"Processing source: {source_name}")
            print(f"URL: {source_url}")
            print("-" * 80)

            # Create output directories
            original_dir, additional_dir = create_output_dirs(source_name)

            # Scrape the main page
            print(f"Scraping main page...")
            scraped_data = scrape_url(source_url)
            print(f"Found {len(scraped_data['articles'])} articles")

            # Save original scrape
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            original_file = os.path.join(original_dir, f'scrape_{timestamp}.json')
            with open(original_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=2, ensure_ascii=False)
            print(f"Saved to {original_file}")

            # Extract additional URLs using source-specific extractor
            extractor = get_extractor(source_name)
            additional_urls = extractor(scraped_data)
            print(f"Extracted {len(additional_urls)} additional URLs to scrape")

            # Scrape each additional URL
            for idx, url in enumerate(additional_urls, 1):
                if url == "No link":
                    continue

                print(f"  Scraping additional URL {idx}/{len(additional_urls)}: {url[:60]}...")
                try:
                    article_data = scrape_additional_url(url, source_name)

                    # Save to additional directory
                    slug = url_to_slug(url)
                    article_file = os.path.join(additional_dir, f'{slug}.json')
                    with open(article_file, 'w', encoding='utf-8') as f:
                        json.dump(article_data, f, indent=2, ensure_ascii=False)

                except requests.exceptions.RequestException as e:
                    print(f"    Error scraping {url}: {e}")
                except Exception as e:
                    print(f"    Error processing {url}: {e}")

            print(f"Completed source: {source_name}")
            print()

        print("=" * 80)
        print("All sources scraped successfully")
        return 0

    except FileNotFoundError:
        print("Error: sources.json not found")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing sources.json: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
