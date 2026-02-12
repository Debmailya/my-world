"""
Development settings for PhishGuard AI
"""

DEBUG = True
TESTING = False
ENVIRONMENT = "development"

# API Settings
API_TITLE = "PhishGuard AI"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Intelligent Phishing Website Detection Platform"

# Security
SECRET_KEY = "dev-key-change-in-production"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# CORS
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Database (optional)
DATABASE_URL = "sqlite:///./phishguard.db"

# ML Model
MODEL_PATH = "ml_model/phishing_model.pkl"
SCALER_PATH = "ml_model/scaler.pkl"
FEATURES_PATH = "ml_model/features.json"

# Logging
LOG_LEVEL = "DEBUG"
LOG_FILE = "logs/development.log"

# Rate Limiting
RATE_LIMIT_ENABLED = False
REQUESTS_PER_HOUR = 1000

# Cache
CACHE_ENABLED = False
CACHE_TTL = 3600

# Features
ENABLE_BATCH_ANALYSIS = True
ENABLE_API_DOCS = True
MAX_BATCH_SIZE = 100

# Timeouts
REQUEST_TIMEOUT = 30
MODEL_INFERENCE_TIMEOUT = 5
