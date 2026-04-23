import os

MAIN_API_URL = os.getenv("MAIN_API_URL", "http://localhost:5000/api")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "swimapi-api-key")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

DEFAULT_DAYS_AHEAD = 7

REQUEST_TIMEOUT = 5
