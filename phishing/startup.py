"""
Production startup script for PhishGuard AI
Handles initialization, migrations, and server startup
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Verify production environment is configured"""
    logger.info("Checking environment configuration...")
    
    required_env_vars = [
        # Add required env vars here
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            logger.warning(f"Missing environment variable: {var}")
    
    logger.info("✓ Environment check complete")

def initialize_ml_model():
    """Initialize machine learning model"""
    logger.info("Loading ML model...")
    try:
        from ml_model.detector import PhishingDetector
        detector = PhishingDetector()
        if detector.model is not None:
            logger.info("✓ ML model loaded successfully")
            return True
        else:
            logger.error("✗ Failed to load ML model")
            return False
    except Exception as e:
        logger.error(f"✗ Error loading ML model: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    logger.info("Starting PhishGuard AI server...")
    
    try:
        import uvicorn
        from backend.app import app
        
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        workers = int(os.getenv("API_WORKERS", "4"))
        
        logger.info(f"Server starting on {host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"✗ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_environment()
    if initialize_ml_model():
        start_server()
    else:
        sys.exit(1)
