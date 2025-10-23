import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONGODB_URL = os.getenv("MONGODB_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY", "capzone-dev-secret")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",") if origin.strip()]
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
