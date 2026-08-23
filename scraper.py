# trustpilot_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
from playwright.sync_api import sync_playwright

def get_browser_data(base_url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(base_url)
        print("Title:", page.title())
        print("URL:", page.url)

        score_element = page.locator("p.styles_trustScore__MVJJI")
        score_element.wait_for(state="visible", timeout=120_000)

        user_agent = page.evaluate("navigator.userAgent")
        cookies = {
            cookie["name"]: cookie["value"]
            for cookie in context.cookies()
        }
        browser.close()
        return (cookies, user_agent)

def get_reviews_from_page(url, user_agent, cookies):
    try:
        req = requests.get(url, headers={"User-Agent": user_agent}, cookies=cookies)
        req.raise_for_status()  # Raise an error for bad status codes
        time.sleep(2)  # Add a delay to avoid overwhelming the server
        soup = BeautifulSoup(req.text, 'html.parser')
        reviews_raw = soup.find("script", id="__NEXT_DATA__").string
        reviews_raw = json.loads(reviews_raw)
        return reviews_raw["props"]["pageProps"].get("reviews", [])
    except (requests.RequestException, json.JSONDecodeError, AttributeError) as e:
        return []

def scrape_trustpilot_reviews(base_url: str):
    cookies, ua = get_browser_data(base_url)
    reviews_data = []

    page_number = 1
    while True:
        url = f"{base_url}?page={page_number}"
        reviews = get_reviews_from_page(url, ua, cookies)

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