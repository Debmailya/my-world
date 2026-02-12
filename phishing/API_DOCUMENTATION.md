# PhishGuard AI - API Documentation

## Overview

PhishGuard AI provides a REST API for intelligent phishing URL detection using machine learning.

## Base URL

Production: `https://phishguard.ai/api`
Development: `http://localhost:8000/api`

## Authentication

Currently, the API is publicly available without authentication. Future versions may implement:
- API keys
- JWT tokens
- Rate limiting per key

## Endpoints

### 1. Analyze Single URL

**POST** `/api/analyze`

Analyzes a single URL for phishing indicators.

#### Request

```json
{
  "url": "https://example.com"
}
```

#### Response (200 OK)

```json
{
  "url": "https://example.com",
  "is_phishing": false,
  "confidence": 95.5,
  "threat_level": "LOW",
  "threat_description": "Minimal risk. URL appears safe.",
  "risk_score": 0.15,
  "explanation": {
    "risk_factors": [],
    "safe_factors": [
      "Valid SSL certificate detected",
      "Domain name length is normal"
    ],
    "confidence": 0.955,
    "summary": "This URL appears to be legitimate with 95.5% confidence."
  },
  "timestamp": "2026-02-12T10:30:00.000Z",
  "flags": [],
  "recommendations": [
    "This URL appears to be safe",
    "Always verify the sender of unexpected emails before clicking links"
  ]
}
```

#### Error Responses

**400 Bad Request** - Invalid URL format
```json
{
  "detail": "Invalid URL: [error details]"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Error analyzing URL. Please try again."
}
```

---

### 2. Batch Analyze URLs

**POST** `/api/batch-analyze`

Analyzes multiple URLs in a single request.

#### Request

```json
[
  "https://example.com",
  "https://google.com",
  "https://github.com"
]
```

#### Response (200 OK)

```json
{
  "results": [
    {
      "url": "https://example.com",
      "is_phishing": false,
      "confidence": 95.5,
      "threat_level": "LOW",
      ...
    },
    ...
  ],
  "total": 3
}
```

#### Limits

- Maximum 100 URLs per request
- Request timeout: 60 seconds
- Rate limit: 1000 requests/hour

---

### 3. Health Check

**GET** `/health`

Returns API health status.

#### Response (200 OK)

```json
{
  "status": "healthy",
  "timestamp": "2026-02-12T10:30:00.000Z",
  "model_loaded": true
}
```

---

## Response Schema

### URLAnalysisResponse

| Field | Type | Description |
|-------|------|-------------|
| url | string | The analyzed URL |
| is_phishing | boolean | True if URL is likely phishing |
| confidence | number | Confidence score (0-100) |
| threat_level | string | One of: LOW, MEDIUM, HIGH, CRITICAL |
| threat_description | string | Human-readable threat description |
| risk_score | number | Risk score (0-1) |
| explanation | object | Detailed analysis explanation |
| timestamp | string | ISO 8601 timestamp of analysis |
| flags | array | Security flags found (e.g., "IP-based URL") |
| recommendations | array | Security recommendations |

### Explanation Object

| Field | Type | Description |
|-------|------|-------------|
| risk_factors | array | List of detected risk factors |
| safe_factors | array | List of detected safe factors |
| confidence | number | Confidence (0-1) |
| summary | string | Summary of analysis |

---

## Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Invalid URL | URL format is invalid |
| 422 | Missing required field | `url` field not provided |
| 429 | Too many requests | Rate limit exceeded |
| 500 | Server error | Internal server error |
| 503 | Service unavailable | Server is down |

---

## Rate Limiting

- Free tier: 100 requests/hour
- Premium tier: 10,000 requests/hour (future)

Rate limit info is returned in headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 2026-02-12T11:30:00Z
```

---

## Code Examples

### Python

```python
import requests

url = 'https://example.com'
response = requests.post('https://phishguard.ai/api/analyze', json={'url': url})
result = response.json()

print(f"Is Phishing: {result['is_phishing']}")
print(f"Confidence: {result['confidence']}%")
print(f"Threat Level: {result['threat_level']}")
```

### JavaScript

```javascript
const url = 'https://example.com';

fetch('https://phishguard.ai/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url })
})
  .then(res => res.json())
  .then(data => {
    console.log('Is Phishing:', data.is_phishing);
    console.log('Confidence:', data.confidence);
    console.log('Threat Level:', data.threat_level);
  });
```

### cURL

```bash
curl -X POST https://phishguard.ai/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## Best Practices

1. **Always Use HTTPS** - Ensure your client uses HTTPS when connecting to the API
2. **Validate Input** - Ensure URLs are properly formatted before sending
3. **Handle Errors** - Implement proper error handling for network issues
4. **Cache Results** - Cache results for frequently checked URLs
5. **Batch Operations** - Use batch endpoint for multiple URLs
6. **Monitor Rate Limits** - Track rate limit headers

---

## Threat Levels

| Level | Confidence | Action |
|-------|-----------|--------|
| **LOW** | 0-60% phishing | Safe to use |
| **MEDIUM** | 60-80% phishing | Use caution |
| **HIGH** | 80-95% phishing | Likely phishing |
| **CRITICAL** | >95% phishing | **Do not interact** |

---

## FAQ

**Q: How accurate is the detection?**
A: Our model achieves ~99.2% accuracy on test data. Real-world accuracy may vary depending on emerging phishing techniques.

**Q: Are URLs stored?**
A: No. URLs are processed in memory and not stored in our database.

**Q: How long does analysis take?**
A: Typically < 500ms per URL.

**Q: Can I integrate this into my email client?**
A: Yes, through our API. Email filter integrations are on the roadmap.

**Q: Is there a webhook option?**
A: Not currently, but it's planned for future versions.

---

## Changelog

### v1.0.0 (Feb 2026)
- Initial release
- Single URL analysis
- Batch URL analysis
- Real-time detection

---

## Support

- **Email**: support@phishguard.ai
- **Documentation**: https://phishguard.ai/docs
- **Status Page**: https://status.phishguard.ai
- **GitHub Issues**: https://github.com/phishguard/ai/issues

---

Last Updated: February 2026
