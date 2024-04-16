# trustpilot_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

def get_reviews_from_page(url):
    try:
        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        req.raise_for_status()  # Raise an error for bad status codes
        time.sleep(2)  # Add a delay to avoid overwhelming the server
        soup = BeautifulSoup(req.text, 'html.parser')
        reviews_raw = soup.find("script", id="__NEXT_DATA__").string
        reviews_raw = json.loads(reviews_raw)
        return reviews_raw["props"]["pageProps"]["reviews"]
    except (requests.RequestException, json.JSONDecodeError, AttributeError) as e:
        return []

def scrape_trustpilot_reviews(base_url: str):
    reviews_data = []

    page_number = 1
    while True:
        url = f"{base_url}?page={page_number}"
        reviews = get_reviews_from_page(url)

        if not reviews:
            break

        for review in reviews:
            data = {
                'Date': pd.to_datetime(review["dates"]["publishedDate"]).strftime("%Y-%m-%d"),
                'Author': review["consumer"]["displayName"],
                'Body': review["text"],
                'Heading': review["title"],
                'Rating': review["rating"],
                'Location': review["consumer"]["countryCode"]
            }
            reviews_data.append(data)
        
        page_number += 1

    # Remove duplicates based on the 'Body' field
    reviews_data = [dict(t) for t in {tuple(d.items()) for d in reviews_data}]
    
    return reviews_data