from setuptools import setup, find_packages

setup(
    name='trustpilot_scraper',
    version='0.10',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas'
        # Add any other dependencies here
    ],
    description='A Python library for scraping Trustpilot reviews.',
    long_description='''
trustpilot-scraper
===================

trustpilot-scraper is a Python package designed for scraping Trustpilot reviews. It provides functions to retrieve Trustpilot reviews from a given Trustpilot page URL.

Installation
------------

You can install trustpilot-scraper via pip:

.. code-block:: bash

    pip install trustpilot-scraper

Usage
-----

To use trustpilot-scraper, import the `scrape_trustpilot_reviews` function from the `trustpilot_scraper.scraper` module. Then, provide the base URL of the Trustpilot page from which you want to scrape reviews.

.. code-block:: python

    from trustpilot_scraper.scraper import scrape_trustpilot_reviews

    base_url = 'https://www.trustpilot.com/review/example.com'

    reviews = scrape_trustpilot_reviews(base_url)

    for review in reviews:
        print(review)

Output
------

The `scrape_trustpilot_reviews` function returns a list of dictionaries, where each dictionary represents a single Trustpilot review. Each review dictionary contains the following keys: 'Date', 'Author', 'Body', 'Heading', 'Rating', and 'Location'.

Features
--------

- Scrapes Trustpilot reviews from the provided base URL.
- Retrieves review data including date, author, body, heading, rating, and location.
- Handles pagination automatically to scrape all available reviews.

Dependencies
------------

- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML content.
- `pandas`: For data manipulation.

For more information and documentation, please visit the GitHub repository: https://github.com/irfanalidv/trustpilot_scraper.

    ''',
    author='Md Irfan Ali',
    author_email='irfanali29@hotmail.com',
    url='https://github.com/irfanalidv/trustpilot_scraper',
    license='MIT',  # Add your license here
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
