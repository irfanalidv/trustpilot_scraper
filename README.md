[![GitHub license](https://img.shields.io/github/license/irfanalidv/trustpilot_scraper)](https://github.com/irfanalidv/trustpilot_scraper/blob/main/LICENSE)
[![Python version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://pypi.org/project/trustpilot-scraper/)
[![PyPI](https://img.shields.io/pypi/v/trustpilot-scraper)](https://pypi.org/project/trustpilot-scraper/)
[![Downloads](https://static.pepy.tech/badge/trustpilot-scraper)](https://pepy.tech/project/trustpilot-scraper)

# Trustpilot Scraper

The `trustpilot-scraper` library is a Python package designed for scraping Trustpilot reviews. It provides functions to retrieve Trustpilot reviews from a given Trustpilot page URL.

This Python library enables businesses to scrape Trustpilot reviews for market analysis, sentiment analysis, and competitor benchmarking. It empowers businesses to gain insights into customer feedback, improve products/services, and enhance their online reputation.

## Installation

You can install `trustpilot-scraper` via pip:

```bash
pip install trustpilot-scraper
```

## Usage

```python
from trustpilot_scraper.scraper import scrape_trustpilot_reviews

base_url = 'https://www.trustpilot.com/review/example.com'

reviews = scrape_trustpilot_reviews(base_url)

for review in reviews:
    print(review)

```
## Output

```python
{'Date': '2022-02-16', 'Author': 'joyce francis', 'Body': 'I visited the Farnborough CR branch and was served by a young lady called Anna who was patient and friendly and also solved a huge problem for me...  great response... \nI would suggest when you visit ask for this young lady.. great customer service...\nOld Black Lady !', 'Heading': 'I visited the Farnborough CR branch and…', 'Rating': 5, 'Location': 'GB'}
{'Date': '2022-07-07', 'Author': 'Marlie Anderson', 'Body': 'Fast response times and excellent client service. I would be delighted to work with them again.', 'Heading': 'Fast response times and excellent…', 'Rating': 5, 'Location': 'US'}
{'Date': '2021-02-07', 'Author': 'JefryMW', 'Body': 'Good gooodljfj', 'Heading': 'Good gooodljfj', 'Rating': 5, 'Location': 'CZ'}
{'Date': '2021-04-27', 'Author': 'torti', 'Body': 'No Company contact exists. Self here fake trusts. No damage on parcels? They dont send parcels maybe system works but rest of this company that noone know who it is isnt serious.\nMake a imressum contact company name where the companys home adress etc.', 'Heading': 'No Company contact exists', 'Rating': 1, 'Location': 'DE'}
{'Date': '2021-01-21', 'Author': 'Aslak Borgenvik', 'Body': "Always punctual. Never any damage on parcels. Cheap, fast and trustworthy, I can't wait for a bigger expand on clienta.", 'Heading': 'Always punctual', 'Rating': 5, 'Location': 'NO'}
{'Date': '2022-01-05', 'Author': 'peter', 'Body': "i decided to buy a draw fridge 2/1/22 took it home installed it unit wouldn't cool faulty cooling system took it back next day, day 2 unit replaced and installed and tested while at the 4x4 centre all working got home filled fridge all good, day 3 fridge not cold error code E3 took it back and put it on test, day 4 got phone call cooling system faulty given refund now back to my old system. really wanted draw fridge as it fitted and looked good and took up less room", 'Heading': 'disappointed draw fridge', 'Rating': 2, 'Location': 'AU'}
{'Date': '2022-03-05', 'Author': 'Jx', 'Body': 'Spam, unsolicited e-mail without any option to unsubscribe.', 'Heading': 'Spam', 'Rating': 1, 'Location': 'PT'}
{'Date': '2021-10-29', 'Author': 'Bill Kelly', 'Body': 'Hooked  it up to my Companion 70 amp lithium power pack that I use to run my Engels 45 litre fridge. Does a great job. More power gong in than  coming out. Make sure you don’t use the regulator supplied because the companion power pack has its own regulator.', 'Heading': '200 watt solar blanket.', 'Rating': 5, 'Location': 'AU'}
{'Date': '2021-09-17', 'Author': 'Cristian Gabriel Mazzulla', 'Body': "Fulfills its function 100% \nit's just an example page xD", 'Heading': 'It is perfect!', 'Rating': 5, 'Location': 'AR'}
{'Date': '2022-06-19', 'Author': 'A TrustPilot User', 'Body': 'Great Site! This is the Example Domain.', 'Heading': 'Great Site', 'Rating': 5, 'Location': 'CA'}
{'Date': '2021-12-03', 'Author': 'ILikeTasks', 'Body': 'Website fulfils its job', 'Heading': 'example', 'Rating': 5, 'Location': 'US'}
{'Date': '2022-08-19', 'Author': 'Me', 'Body': '4WD Supa Center High-Def Dash Camera\nI bought this 2 years ago at first it was good it captured everything but after the first month I started Noticing Sun Glitches where the screen would just white out,\nIn the first summer in Victoria it just shut down over 30c it would heat up in the sun and just stop recording\nVery poor quality $45 I payed after 6 month I tossed it in the Bin 1*', 'Heading': '4WD Supa Center High-Def Dash Camera', 'Rating': 1, 'Location': 'AU'}
{'Date': '2022-10-04', 'Author': 'Kepler', 'Body': 'Fantastic keyboard for the price, for the 1st time using a 60% TKL keyboard and I am adapting quite well, also 1st time using mechanical keys and enjoying a lot these Outemu pro red switches.\nThis Keyboard is solid, well made and it is simple and easy to use. The only downside for me is the lack of control the intensity of the RGB lighting at hardware level.', 'Heading': 'Fantastic keyboard for the price', 'Rating': 4, 'Location': 'PT'}
{'Date': '2022-04-18', 'Author': 'Snowneeerd', 'Body': 'Picked up a Titan rear drawer. When I got home an opened it, the side was dented. No problems getting it swapped. Got the second one home, this was also dented. Going to ask them to check the third one before I take it. Obvious quality control issues.', 'Heading': 'Two dented Titan rear drawers 4WD Supa Centre', 'Rating': 2, 'Location': 'AU'}
{'Date': '2022-07-20', 'Author': 'Ankit Verma', 'Body': 'Does my review even count???', 'Heading': 'Does my review even count???', 'Rating': 4, 'Location': 'IN'}
```

## Features

- Scrapes Trustpilot reviews from the provided base URL.
- Retrieves review data including date, author, body, heading, rating, and location.
- Handles pagination automatically to scrape all available reviews.

## Dependencies

- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML content.
- `pandas`: For data manipulation.
- Any other dependencies are automatically installed via pip during package installation.
