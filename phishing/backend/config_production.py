"""
Production settings for PhishGuard AI
"""

DEBUG = False
TESTING = False
ENVIRONMENT = "production"

# API Settings
API_TITLE = "PhishGuard AI"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Intelligent Phishing Website Detection Platform"

# Security
SECRET_KEY = "${SECRET_KEY}"  # Set in environment
ALLOWED_HOSTS = ["phishguard.ai", "www.phishguard.ai"]

# CORS
CORS_ORIGINS = [
    "https://phishguard.ai",
    "https://www.phishguard.ai",
]

# Database (optional)
DATABASE_URL = "${DATABASE_URL}"  # Set in environment

# ML Model
MODEL_PATH = "ml_model/phishing_model.pkl"
SCALER_PATH = "ml_model/scaler.pkl"
FEATURES_PATH = "ml_model/features.json"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/production.log"

# Rate Limiting
RATE_LIMIT_ENABLED = True
REQUESTS_PER_HOUR = 1000
REQUESTS_PER_MINUTE = 60

# Cache
CACHE_ENABLED = True
CACHE_TTL = 3600

# Features
ENABLE_BATCH_ANALYSIS = True
ENABLE_API_DOCS = True
MAX_BATCH_SIZE = 100

# Timeouts
REQUEST_TIMEOUT = 30
MODEL_INFERENCE_TIMEOUT = 5

# Security Headers
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
