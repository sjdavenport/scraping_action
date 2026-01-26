#!/usr/bin/env python3
"""
Scraper for malaymail.com Malaysia news section
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

def scrape(url, code = None, proxies = None):
    if proxies:
        response = requests.get(url, proxies=proxies)
    else:
        response = requests.get(url)
        
    if code == "utf-8":
        response.encoding = "utf-8"

    if response.status_code == 403:
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/119.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    }

        response = requests.get(url, headers=headers)
        out = response.text
    elif response.status_code == 200:
        out = response.text
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

    return out

def load_sources():
    """Load sources from sources.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sources_file = os.path.join(script_dir, 'sources.json')

    with open(sources_file, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def create_output_dirs(source_name):
    """Create output directory structure for a source"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir2use = os.path.join(script_dir, 'data', source_name)
    os.makedirs(dir2use, exist_ok=True)

    return dir2use

def main_scraper():
    sources = load_sources()
    yesterday = date.today() - timedelta(days=1)
    yesterdays_date = yesterday.strftime("%d-%m-%Y")
    ending = yesterdays_date + '.html'
    for i in range(len(sources)):
        name = sources[i]['name']
        url = sources[i]['url']
        html = scrape(url)
        dir2use = create_output_dirs(name)
        savename = os.path.join(dir2use, ending)
        with open(savename, "w", encoding="utf-8") as f:
            f.write(html)

if __name__ == "__main__":
    exit(main_scraper())
