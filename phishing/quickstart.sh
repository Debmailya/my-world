#!/bin/bash

# PhishGuard AI - Quick Start Guide

set -e

clear

echo "╔════════════════════════════════════════╗"
echo "║   Welcome to PhishGuard AI Setup      ║"
echo "║   Intelligent Phishing Detection      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"
    
    echo ""
    echo "Starting PhishGuard AI with Docker..."
    echo ""
    
    docker-compose up --build
    
else
    echo "⚠️  Docker not found. Installing dependencies for local development..."
    echo ""
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required. Please install Python 3.11+"
        exit 1
    fi
    
    echo "✓ Python $(python3 --version) found"
    echo ""
    
    # Create virtual environment
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    # Start server
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║    Starting PhishGuard AI Server      ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "🚀 Server starting on http://localhost:8000"
    echo "🌐 Open http://localhost:8000 in your browser"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    python backend/app.py
fi
