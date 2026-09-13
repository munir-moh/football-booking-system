import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
PRICE_PER_HOUR = 10000
MIN_HOURS = 1

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")