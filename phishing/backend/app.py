"""
PhishGuard AI - Production-Ready Phishing Detection API
A professional cybersecurity SaaS platform powered by machine learning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl, validator
import ssl
import socket
from urllib.parse import urlparse
import requests
from datetime import datetime
import json
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path to import ml_model
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_model.detector import PhishingDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PhishGuard AI",
    description="Intelligent Phishing Detection Platform",
    version="1.0.0"
)

# CORS Configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML detector
detector = PhishingDetector()

# ============================================================================
# Request/Response Models
# ============================================================================

class URLRequest(BaseModel):
    """Validate URL input"""
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        """Ensure URL is properly formatted"""
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        try:
            result = urlparse(v)
            if not result.scheme or not result.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
        return v


class URLAnalysisResponse(BaseModel):
    """Comprehensive analysis response"""
    url: str
    is_phishing: bool
    confidence: float
    threat_level: str
    threat_description: str
    risk_score: float
    explanation: dict
    timestamp: str
    flags: list
    recommendations: list


# ============================================================================
# URL Feature Extraction
# ============================================================================

class URLAnalyzer:
    """Extract features from URLs for analysis"""
    
    @staticmethod
    def get_ssl_info(url: str) -> dict:
        """Check SSL certificate validity"""
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        "has_ssl": True,
                        "cert_valid": True,
                        "issuer": cert.get('issuer', 'Unknown')
                    }
        except Exception as e:
            return {
                "has_ssl": False,
                "cert_valid": False,
                "issuer": None,
                "error": str(e)
            }
    
    @staticmethod
    def check_redirects(url: str, max_redirects: int = 5) -> dict:
        """Check for suspicious redirects"""
        try:
            response = requests.head(url, timeout=5, allow_redirects=False)
            redirect_count = 0
            redirect_chain = [url]
            
            while response.status_code in [301, 302, 303, 307, 308] and redirect_count < max_redirects:
                redirect_url = response.headers.get('location')
                redirect_chain.append(redirect_url)
                response = requests.head(redirect_url, timeout=5, allow_redirects=False)
                redirect_count += 1
            
            return {
                "has_redirects": redirect_count > 0,
                "redirect_count": redirect_count,
                "redirect_chain": redirect_chain,
                "final_url": redirect_chain[-1]
            }
        except Exception as e:
            return {
                "has_redirects": False,
                "redirect_count": 0,
                "error": str(e)
            }
    
    @staticmethod
    def extract_domain_features(url: str) -> dict:
        """Extract domain-based features"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        features = {
            "domain": domain,
            "subdomain_count": domain.count('.') - 1,
            "has_hyphen": '-' in domain,
            "has_numbers": any(c.isdigit() for c in domain),
            "domain_length": len(domain),
            "is_ip": bool(__import__('re').match(r'^\d+\.\d+\.\d+\.\d+', domain)),
            "path_length": len(parsed.path),
            "has_query": bool(parsed.query),
            "special_chars_in_path": len([c for c in parsed.path if c in '@!$&\'()*+,;=:'])
        }
        
        return features
    
    @staticmethod
    def check_domain_age(domain: str) -> dict:
        """Check approximate domain age using WHOIS (simplified)"""
        # In production, use a proper WHOIS library
        return {"domain_age_suspicious": False}


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard"""
    return {"status": "PhishGuard AI is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": detector.model is not None
    }


@app.post("/api/analyze", response_model=URLAnalysisResponse)
async def analyze_url(request: URLRequest):
    """
    Analyze a URL for phishing indicators
    
    Returns:
    - Phishing prediction (True/False)
    - Confidence score (0-100)
    - Threat level (Low/Medium/High/Critical)
    - Detailed explanation of findings
    - Risk score and flags
    """
    try:
        url = request.url
        logger.info(f"Analyzing URL: {url}")
        
        # Extract features
        analyzer = URLAnalyzer()
        domain_features = analyzer.extract_domain_features(url)
        ssl_info = analyzer.get_ssl_info(url)
        redirects_info = analyzer.check_redirects(url)
        domain_age_info = analyzer.check_domain_age(domain_features['domain'])
        
        # Prepare feature dict for model
        features = {
            **domain_features,
            **ssl_info,
            **redirects_info,
            **domain_age_info
        }
        
        # Get prediction from ML model
        is_phishing, confidence, risk_score = detector.predict(url, features)
        
        # Determine threat level based on confidence
        if is_phishing:
            if confidence >= 0.95:
                threat_level = "CRITICAL"
            elif confidence >= 0.80:
                threat_level = "HIGH"
            elif confidence >= 0.60:
                threat_level = "MEDIUM"
            else:
                threat_level = "LOW"
        else:
            threat_level = "LOW"
        
        # Generate explanation
        explanation = _generate_explanation(is_phishing, features, confidence)
        
        # Generate flags
        flags = _extract_flags(features, is_phishing)
        
        # Generate recommendations
        recommendations = _generate_recommendations(is_phishing, flags)
        
        response = URLAnalysisResponse(
            url=url,
            is_phishing=is_phishing,
            confidence=round(confidence * 100, 2),
            threat_level=threat_level,
            threat_description=_get_threat_description(threat_level),
            risk_score=round(risk_score, 2),
            explanation=explanation,
            timestamp=datetime.now().isoformat(),
            flags=flags,
            recommendations=recommendations
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing URL. Please try again.")


@app.post("/api/batch-analyze")
async def batch_analyze(urls: list[str]):
    """Analyze multiple URLs at once"""
    results = []
    for url in urls:
        try:
            result = await analyze_url(URLRequest(url=url))
            results.append(result)
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return {"results": results, "total": len(urls)}


@app.get("/sitemap.xml")
async def sitemap():
    """Sitemap for SEO"""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://phishguard.ai/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://phishguard.ai/about</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://phishguard.ai/docs</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>"""
    return FileResponse(media_type="application/xml", content=xml)


@app.get("/robots.txt")
async def robots():
    """Robots.txt for SEO"""
    content = """User-agent: *
Allow: /
Disallow: /api/
Allow: /sitemap.xml

Sitemap: https://phishguard.ai/sitemap.xml"""
    return FileResponse(media_type="text/plain", content=content)


# ============================================================================
# Helper Functions
# ============================================================================

def _generate_explanation(is_phishing: bool, features: dict, confidence: float) -> dict:
    """Generate detailed explanation of the prediction"""
    explanation = {"risk_factors": [], "safe_factors": []}
    
    # Risk factors
    if features.get('is_ip'):
        explanation["risk_factors"].append("Domain is an IP address instead of a proper domain name")
    
    if features.get('has_hyphen'):
        explanation["risk_factors"].append("Domain contains hyphens (common in phishing)")
    
    if features.get('subdomain_count', 0) > 3:
        explanation["risk_factors"].append("Excessive subdomains detected")
    
    if not features.get('has_ssl'):
        explanation["risk_factors"].append("No valid SSL certificate found")
    
    if features.get('has_redirects'):
        explanation["risk_factors"].append(f"Multiple redirects detected ({features.get('redirect_count', 0)} redirects)")
    
    if features.get('domain_length', 0) > 40:
        explanation["risk_factors"].append("Unusually long domain name")
    
    # Safe factors
    if features.get('has_ssl'):
        explanation["safe_factors"].append("Valid SSL certificate detected")
    
    if features.get('domain_length', 0) < 20:
        explanation["safe_factors"].append("Domain name length is normal")
    
    if not features.get('has_redirects'):
        explanation["safe_factors"].append("No suspicious redirects detected")
    
    explanation["confidence"] = confidence
    explanation["summary"] = f"This URL appears to be {'phishing' if is_phishing else 'legitimate'} with {confidence*100:.1f}% confidence."
    
    return explanation


def _extract_flags(features: dict, is_phishing: bool) -> list:
    """Extract security flags from URL analysis"""
    flags = []
    
    if features.get('is_ip'):
        flags.append("IP-based URL")
    if features.get('has_hyphen'):
        flags.append("Hyphenated domain")
    if features.get('subdomain_count', 0) > 3:
        flags.append("Multiple subdomains")
    if not features.get('has_ssl'):
        flags.append("No SSL certificate")
    if features.get('has_redirects'):
        flags.append("Suspicious redirects")
    if features.get('special_chars_in_path'):
        flags.append("Special characters in URL path")
    
    return flags


def _generate_recommendations(is_phishing: bool, flags: list) -> list:
    """Generate security recommendations"""
    recommendations = []
    
    if is_phishing:
        recommendations.append("Do not enter any personal or financial information")
        recommendations.append("Report this URL to your email provider or IT security team")
        recommendations.append("Delete any emails containing this link")
        recommendations.append("Do not download or open any attachments from this source")
    else:
        recommendations.append("This URL appears to be safe")
        recommendations.append("Always verify the sender of unexpected emails before clicking links")
        recommendations.append("Keep your browser and security software up to date")
    
    if "No SSL certificate" in flags:
        recommendations.append("Avoid entering sensitive information on this website")
    
    if "Suspicious redirects" in flags:
        recommendations.append("Be cautious when clicking this link - it may redirect to malicious content")
    
    return recommendations


def _get_threat_description(threat_level: str) -> str:
    """Get description for threat level"""
    descriptions = {
        "LOW": "Minimal risk. URL appears safe.",
        "MEDIUM": "Moderate risk detected. Review URL carefully.",
        "HIGH": "Significant risk indicators. Likely phishing attempt.",
        "CRITICAL": "Extreme risk. Highly likely to be phishing. Do not interact."
    }
    return descriptions.get(threat_level, "Unknown threat level")


# ============================================================================
# Serve Frontend
# ============================================================================

# Serve static files from frontend build
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
