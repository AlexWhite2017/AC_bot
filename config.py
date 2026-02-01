import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")
ADMIN_ID = os.getenv("ADMIN_ID", "ВАШ_TELEGRAM_ID")

# Пути к файлам данных
THEORY_DATA_PATH = "data/theory_guide.json"
MODELS_DATA_PATH = "data/ac_models.json"
NEWS_DATA_PATH = "data/news_posts.json"

# Константы для расчета
BTU_PER_M2 = 340  # BTU на квадратный метр
