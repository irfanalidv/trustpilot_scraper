"""Allow ``python -m trustpilot_scraper``."""

import sys

from .cli import main

sys.exit(main())
