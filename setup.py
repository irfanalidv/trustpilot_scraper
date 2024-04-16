# setup.py

from setuptools import setup, find_packages

setup(
    name='trustpilot_scraper',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        # Add any other dependencies here
    ],
    description='A Python library for scraping Trustpilot reviews.',
    author='Md Irfan Ali',
    author_email='irfanali29@hotmail.com',
    url='https://github.com/irfanalidv/trustpilot-scraper',
)
