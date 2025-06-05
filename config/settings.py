
from dotenv import load_dotenv
import os
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")
TG_TOKEN = os.getenv("TG_TOKEN")
if not TG_TOKEN:
    raise RuntimeError("Не найден TG_TOKEN в .env")



import os
import logging
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

#api
TG_TOKEN = os.getenv("TG_TOKEN")
if not TG_TOKEN:
    raise RuntimeError("⚠️ Не найден TG_TOKEN в .env")

# api link
AGENT_API_URL = "https://valorant-api.com/v1/agents"
DEFAULT_LANGUAGE = "ru-RU" 
# cash time
CACHE_TTL = 3600  

#log settings
LOG_FILE = BASE_DIR / "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("valbot")
