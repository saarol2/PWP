"""Configuration values for the auxiliary maintenance service."""

import os
from dotenv import load_dotenv

load_dotenv()

MAIN_API_URL = os.getenv("MAIN_API_URL", "https://pwp.fly.dev/api")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "swimapi-api-key")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

DEFAULT_DAYS_AHEAD = 7
CLEANUP_AGE_DAYS = 7

REQUEST_TIMEOUT = 5
