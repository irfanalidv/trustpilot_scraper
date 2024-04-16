# Trustpilot Scraper

The `trustpilot_scraper` library is a Python package designed for scraping Trustpilot reviews. It provides functions to retrieve Trustpilot reviews from a given Trustpilot page URL.

## Installation

You can install `trustpilot_scraper` via pip:

```bash
pip install trustpilot_scraper
```

## Usage

```python
from trustpilot_scraper import scrape_trustpilot_reviews

base_url = 'https://www.trustpilot.com/review/example.com'

reviews = scrape_trustpilot_reviews(base_url)

for review in reviews:
    print(review)
```

## Features

- Scrapes Trustpilot reviews from the provided base URL.
- Retrieves review data including date, author, body, heading, rating, and location.
- Handles pagination automatically to scrape all available reviews.

## Dependencies

- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML content.
- Any other dependencies are automatically installed via pip during package installation.

## Contributing

If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on [GitHub](https://github.com/irfanalidv/trustpilot-scraper).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.