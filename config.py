import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"

# Ensure necessary directories exist
for directory in [LOGS_DIR, SNAPSHOTS_DIR, REPORTS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Crawler Settings
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT", "5"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))
RETRIES = int(os.getenv("RETRIES", "3"))

# Playwright options
PLAYWRIGHT_TIMEOUT = TIMEOUT_SECONDS * 1000  # milliseconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

# ML Settings
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
VERIFICATION_MODEL_PATH = MODELS_DIR / "verification_model.pkl"

# LLM / AI Engine Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openrouter_or_openai_api_key_here")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gemma4:31b-cloud")
