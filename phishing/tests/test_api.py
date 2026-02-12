"""
PhishGuard AI - Comprehensive Test Suite
Tests for phishing detection model and API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestPhishingDetection:
    """Test phishing detection API"""
    
    def test_analyze_legitimate_url(self):
        """Test analysis of legitimate URL"""
        response = client.post("/api/analyze", json={"url": "https://google.com"})
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "is_phishing" in data
        assert "confidence" in data
        assert "threat_level" in data
        assert "explanation" in data
        assert "recommendations" in data
    
    def test_analyze_suspicious_url(self):
        """Test analysis of suspicious URL"""
        response = client.post("/api/analyze", json={"url": "http://192.168.1.1"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["is_phishing"], bool)
        assert 0 <= data["confidence"] <= 100
    
    def test_invalid_url(self):
        """Test error handling for invalid URL"""
        response = client.post("/api/analyze", json={"url": "not a url"})
        assert response.status_code == 400
    
    def test_empty_url(self):
        """Test error handling for empty URL"""
        response = client.post("/api/analyze", json={"url": ""})
        assert response.status_code == 400
    
    def test_url_with_http(self):
        """Test URL auto-correction"""
        response = client.post("/api/analyze", json={"url": "google.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["url"].startswith("https://")
    
    def test_response_schema(self):
        """Test response follows expected schema"""
        response = client.post("/api/analyze", json={"url": "https://github.com"})
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields
        required_fields = [
            "url", "is_phishing", "confidence", "threat_level",
            "threat_description", "risk_score", "explanation",
            "timestamp", "flags", "recommendations"
        ]
        
# sourcery skip: no-loop-in-tests
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Check explanation structure
        assert "risk_factors" in data["explanation"]
        assert "safe_factors" in data["explanation"]
        assert isinstance(data["recommendations"], list)


class TestThreatDetection:
    """Test threat level classification"""
    
    @pytest.mark.parametrize("threat_level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    def test_valid_threat_levels(self, threat_level):
        """Test all valid threat levels"""
        # This would require URLs that trigger specific threat levels
        # In a real scenario, you'd use test URLs
        pass


class TestSEO:
    """Test SEO features"""
    
    def test_sitemap(self):
        """Test sitemap.xml availability"""
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]
    
    def test_robots(self):
        """Test robots.txt availability"""
        response = client.get("/robots.txt")
        assert response.status_code == 200


class TestBatchAnalysis:
    """Test batch URL analysis"""
    
    def test_batch_analyze(self):
        """Test analyzing multiple URLs at once"""
        urls = [
            "https://google.com",
            "https://github.com",
            "https://example.com"
        ]
        response = client.post("/api/batch-analyze", json=urls)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == len(urls)


class TestErrorHandling:
    """Test error handling"""
    
    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/analyze",
            content="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_url_field(self):
        """Test handling of missing URL field"""
        response = client.post("/api/analyze", json={})
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
