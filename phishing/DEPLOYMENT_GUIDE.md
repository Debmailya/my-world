DEPLOYMENT_GUIDE.md
===================

## PhishGuard AI - Complete Deployment Guide

This guide covers deploying PhishGuard AI to production on multiple platforms.

---

## 1. LOCAL DEVELOPMENT

### Prerequisites
- Python 3.11+
- pip or conda
- Git

### Setup

```bash
# Clone repository
git clone <repo-url>
cd phishing

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run development server
python backend/app.py
```

App will be available at http://localhost:8000

---

## 2. DOCKER DEPLOYMENT (Recommended)

### Prerequisites
- Docker installed (https://www.docker.com/products/docker-desktop)

### Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:80
```

### Production with Docker

```bash
# Build production image
docker build -t phishguard-ai:prod .

# Run with optimized settings
docker run -d \
  --name phishguard \
  -p 80:8000 \
  -e ENVIRONMENT=production \
  --restart unless-stopped \
  phishguard-ai:prod
```

---

## 3. HEROKU DEPLOYMENT

### Prerequisites
- Heroku account (https://www.heroku.com)
- Heroku CLI installed

### Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create phishguard-ai

# Set buildpacks
heroku buildpacks:add heroku/python -a phishguard-ai

# Deploy
git push heroku main

# Monitor logs
heroku logs --tail -a phishguard-ai

# Check status
heroku apps:info -a phishguard-ai
```

### Heroku Configuration

```bash
# Set environment variables
heroku config:set ENVIRONMENT=production -a phishguard-ai
heroku config:set API_WORKERS=4 -a phishguard-ai

# Scale dynos
heroku ps:scale web=2 -a phishguard-ai

# Enable SSL
heroku certs:auto:enable -a phishguard-ai
```

---

## 4. AWS EC2 DEPLOYMENT

### Prerequisites
- AWS account
- EC2 instance (Ubuntu 22.04, t3.medium or larger)

### Setup Steps

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <repo-url> /app
cd /app

# Start application
docker-compose up -d

# View logs
docker-compose logs -f
```

### Enable HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --standalone -d phishguard.ai -d www.phishguard.ai

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Configure Nginx with SSL

```bash
# Update nginx.conf with SSL paths
# /etc/ssl/certs/fullchain.pem
# /etc/ssl/private/privkey.pem

# Restart Nginx
docker-compose restart nginx
```

---

## 5. GOOGLE CLOUD RUN DEPLOYMENT

### Prerequisites
- Google Cloud account
- gcloud CLI installed

### Steps

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/phishguard-ai

# Deploy to Cloud Run
gcloud run deploy phishguard-ai \
  --image gcr.io/YOUR_PROJECT_ID/phishguard-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1

# Get service URL
gcloud run services describe phishguard-ai --region us-central1
```

---

## 6. AZURE APP SERVICE DEPLOYMENT

### Prerequisites
- Azure account
- Azure CLI installed

### Steps

```bash
# Login
az login

# Create resource group
az group create --name phishguard-rg --location "East US"

# Create App Service plan
az appservice plan create \
  --name phishguard-plan \
  --resource-group phishguard-rg \
  --sku B2 --is-linux

# Create web app
az webapp create \
  --resource-group phishguard-rg \
  --plan phishguard-plan \
  --name phishguard-ai \
  --deployment-container-image-name-user-provided phishguard-ai

# Configure Docker
az webapp config container set \
  --name phishguard-ai \
  --resource-group phishguard-rg \
  --docker-custom-image-name phishguard-ai \
  --docker-registry-server-url <registry-url>
```

---

## 7. DIGITAL OCEAN DEPLOYMENT

### Prerequisites
- DigitalOcean account
- DigitalOcean App Platform

### Steps

```bash
# Create app.yaml
cat > app.yaml << EOF
name: phishguard-ai
services:
- name: api
  github:
    branch: main
    repo: your-username/phishguard
  build_command: pip install -r backend/requirements.txt
  run_command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app:app
  http_port: 8000
  envs:
  - key: ENVIRONMENT
    value: production
EOF

# Deploy
doctl apps create --spec app.yaml
```

---

## 8. PRODUCTION CHECKLIST

Before deploying to production, ensure:

### Security
- [ ] HTTPS/TLS enabled
- [ ] Environment variables configured (.env)
- [ ] Secrets not in code
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation active

### Performance
- [ ] Database indexed (if applicable)
- [ ] Caching configured
- [ ] Compression enabled
- [ ] Load balancer configured
- [ ] Multiple instances running

### Monitoring
- [ ] Uptime monitoring enabled
- [ ] Error tracking configured
- [ ] Logs centralized
- [ ] Alerts configured
- [ ] Performance metrics tracked

### Operations
- [ ] Backup strategy in place
- [ ] Disaster recovery plan
- [ ] Documentation updated
- [ ] Support contact configured
- [ ] Runbooks created

---

## 9. SCALING GUIDELINES

### For 1,000s of requests/month
- Single instance sufficient
- 1GB RAM, 1 CPU

### For 100,000s of requests/month
- 2-3 instances
- Load balancer
- 2GB RAM per instance

### For 1,000,000+ requests/month
- 5+ instances
- Redis caching
- Database replication
- CDN for static files
- Advanced monitoring

---

## 10. TROUBLESHOOTING

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Docker containers not starting
```bash
# Check logs
docker-compose logs -f

# Rebuild images
docker-compose down --rmi all
docker-compose up --build
```

### ML model not loading
```bash
# Check model file exists
ls -la ml_model/phishing_model.pkl

# Verify permissions
chmod 644 ml_model/*.pkl
```

### High memory usage
```bash
# Reduce workers
export API_WORKERS=2

# Check for memory leaks
python -m tracemalloc backend/app.py
```

---

## 11. MONITORING & LOGGING

### Configure Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-client
pip install python-json-logger
```

### Key Metrics to Monitor
- Request latency (p50, p95, p99)
- Error rate
- Model inference time
- Memory usage
- CPU usage
- Request throughput

### Log Aggregation
- Send logs to CloudWatch, Stackdriver, or ELK
- Set alert thresholds
- Create dashboards

---

## 12. BACKUP & DISASTER RECOVERY

### Backup Strategy
- Code: Git repository
- Model: Automated backups every 24 hours
- Logs: Retained for 30+ days

### Recovery Steps
1. Redeploy from Docker image
2. Restore model from backup
3. Verify integrity
4. Run health checks

---

## 13. DOMAIN & DNS CONFIGURATION

### DNS Setup
```
A Record: phishguard.ai -> Load Balancer IP
CNAME:    www.phishguard.ai -> phishguard.ai
```

### SSL Certificate
- Use Let's Encrypt for free certificates
- Auto-renewal every 90 days
- Add to CDN (CloudFlare, Akamai, etc.)

---

## Support

For deployment issues, contact:
- Email: support@phishguard.ai
- Docs: https://phishguard.ai/docs

---

Generated: February 2026
Version: 1.0.0
