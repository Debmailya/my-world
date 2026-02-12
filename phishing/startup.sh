#!/bin/bash

# PhishGuard AI - Production Startup Script
# Handles initialization and server startup

set -e

echo "========================================="
echo "PhishGuard AI - Production Startup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check required environment variables
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ -z "$ENVIRONMENT" ]; then
    export ENVIRONMENT="development"
    echo -e "${YELLOW}⚠️  ENVIRONMENT not set. Using: development${NC}"
else
    echo "Environment: $ENVIRONMENT"
fi

if [ -z "$API_WORKERS" ]; then
    export API_WORKERS=4
    echo "API Workers: 4 (default)"
else
    echo "API Workers: $API_WORKERS"
fi

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p backend logs ml_model

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
else
    source venv/bin/activate
fi

# Initialize ML model
echo -e "${YELLOW}Loading ML model...${NC}"
python -c "from ml_model.detector import PhishingDetector; detector = PhishingDetector(); print('✓ Model loaded successfully')" || {
    echo -e "${RED}✗ Failed to load ML model${NC}"
    exit 1
}

# Run health checks
echo -e "${YELLOW}Running health checks...${NC}"
python -c "import sklearn; import fastapi; print('✓ All dependencies available')" || {
    echo -e "${RED}✗ Missing required dependencies${NC}"
    exit 1
}

# Start server
echo -e "${GREEN}Starting PhishGuard AI server...${NC}"
echo "API available at http://localhost:8000"

if [ "$ENVIRONMENT" = "production" ]; then
    # Production: use gunicorn
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers "$API_WORKERS" \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 60 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info \
        backend.app:app
else
    # Development: use uvicorn with reload
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload --log-level info
fi
