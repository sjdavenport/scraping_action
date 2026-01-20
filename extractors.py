"""
URL extraction functions for different sources.
Each extractor takes scraped data and returns a list of URLs to scrape.
"""


def extract_urls_malaymail(scraped_data):
    """Extract additional URLs from malaymail scraped data"""
    return [article["url"] for article in scraped_data.get("articles", [])]


def extract_urls_default(scraped_data):
    """Generic fallback extractor"""
    return [article["url"] for article in scraped_data.get("articles", [])]


# Registry mapping source names to their extractors
EXTRACTORS = {
    "malaymail": extract_urls_malaymail,
    # Add more sources here
}


def get_extractor(source_name):
    """Get the extractor function for a source, falling back to default"""
    return EXTRACTORS.get(source_name, extract_urls_default)
