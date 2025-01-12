import os

from dotenv import load_dotenv

load_dotenv()

WEATHER_API_SECRET = os.getenv("WEATHER_API_SECRET")
TOKEN = os.getenv("BOT_TOKEN")
NUTRITION_API_ID = os.getenv("NUTRITION_API_ID")
NUTRITION_API_SECRET = os.getenv("NUTRITION_API_SECRET")

if not TOKEN or not NUTRITION_API_ID or not NUTRITION_API_SECRET:
	raise ValueError("Переменная окружения BOT_TOKEN не установлена")