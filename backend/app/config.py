import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONGODB_URL = os.getenv("MONGODB_URL", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "PROYECTOS")
MONGODB_PRODUCTS_COLLECTION = os.getenv("MONGODB_PRODUCTS_COLLECTION", "JOSE_DM_CAPS")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
SECRET_KEY = os.getenv("SECRET_KEY", "capzone-dev-secret")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",") if origin.strip()]
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONGODB_URL = os.getenv("MONGODB_URL", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "PROYECTOS")
MONGODB_PRODUCTS_COLLECTION = os.getenv("MONGODB_PRODUCTS_COLLECTION", "JOSE_DM_CAPS")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
SECRET_KEY = os.getenv("SECRET_KEY", "capzone-dev-secret")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",") if origin.strip()]
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
