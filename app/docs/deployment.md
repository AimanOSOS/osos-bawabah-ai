# Deployment Guide

This guide covers deployment strategies and configuration for the Bawabah AI ML models API server.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Environment Setup](#environment-setup)
- [Configuration Management](#configuration-management)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Deployment Options

### 1. Local Development

**Requirements:**
- Python 3.13+
- Poetry
- 4GB+ RAM (for model loading)
- 2GB+ disk space (for model cache)

**Quick Start:**
```bash
# Clone repository
git clone <repository-url>
cd mlops-pipeline

# Install dependencies
poetry install

# Set up environment
cp env.example .env
# Edit .env with your settings

# Run development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Docker Deployment

**Single Container:**
```bash
# Build image
docker build -t bawabah-ai .

# Run container
docker run -p 8000:8000 --env-file .env bawabah-ai
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TTS_MODEL_NAME=openbmb/VoxCPM-0.5B
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/app/models
    restart: unless-stopped
```

### 3. Cloud Deployment

**AWS ECS/Fargate:**
- Container-based deployment
- Auto-scaling capabilities
- Load balancer integration

**Google Cloud Run:**
- Serverless container deployment
- Automatic scaling
- Pay-per-request pricing

**Azure Container Instances:**
- Simple container deployment
- Integration with Azure services

## Environment Setup

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- OS: Linux/macOS/Windows

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- GPU: Optional (for faster inference)

### Python Environment

**Using Poetry (Recommended):**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

**Using pip:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Model Download

Models are downloaded automatically on first use. For production, pre-download models:

```bash
# Pre-download TTS model
python -c "from app.services.model_loader import get_tts_model; get_tts_model()"
```

## Configuration Management

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Copy example file
cp env.example .env

# Edit configuration
nano .env
```

**Key Configuration Options:**

```bash
# Model Configuration
TTS_MODEL_NAME=openbmb/VoxCPM-0.5B
MODEL_CACHE_DIR=/app/models

# Performance Settings
DEFAULT_INFERENCE_TIMESTEPS=10
DEFAULT_CFG_VALUE=2.0
DEFAULT_RETRY_MAX_TIMS=3

# Audio Settings
SAMPLE_RATE=16000
AUDIO_FORMAT=WAV

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
MAX_TEXT_LENGTH=1000
```

### Production Configuration

**Security Settings:**
```bash
# Disable debug mode
DEBUG=false

# Set appropriate log level
LOG_LEVEL=WARNING

# Limit text length
MAX_TEXT_LENGTH=500
```

**Performance Settings:**
```bash
# Optimize for production
DEFAULT_INFERENCE_TIMESTEPS=8
DEFAULT_CFG_VALUE=1.5
DEFAULT_RETRY_MAX_TIMS=2
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Copy application code
COPY app/ ./app/

# Create models directory
RUN mkdir -p /app/models

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_CACHE_DIR=/app/models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TTS_MODEL_NAME=openbmb/VoxCPM-0.5B
      - MODEL_CACHE_DIR=/app/models
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - model_cache:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  model_cache:
```

### Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API proxy
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # File upload size limit
        client_max_body_size 50M;
    }
}
```

## Production Deployment

### 1. Server Setup

**Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/bawabah-ai
sudo chown $USER:$USER /opt/bawabah-ai
```

### 2. Application Deployment

```bash
# Clone repository
cd /opt/bawabah-ai
git clone <repository-url> .

# Set up environment
cp env.example .env
nano .env  # Configure for production

# Build and start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f api
```

### 3. SSL Certificate Setup

**Using Let's Encrypt:**
```bash
# Install Certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem
sudo chown $USER:$USER ./ssl/*.pem
```

### 4. System Service

Create systemd service for auto-start:

```ini
# /etc/systemd/system/bawabah-ai.service
[Unit]
Description=Bawabah AI API Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/bawabah-ai
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable bawabah-ai
sudo systemctl start bawabah-ai
```

## Monitoring and Logging

### Application Logging

**Log Configuration:**
```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

**Log Rotation:**
```bash
# Install logrotate
sudo apt install logrotate

# Create logrotate config
sudo nano /etc/logrotate.d/bawabah-ai
```

```bash
# /etc/logrotate.d/bawabah-ai
/opt/bawabah-ai/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart api
    endscript
}
```

### Health Monitoring

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        # Check model availability
        model = get_tts_model()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "models": {
                "tts": "available"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unhealthy")
```

**Monitoring Script:**
```bash
#!/bin/bash
# health-check.sh

API_URL="http://localhost:8000/health"
LOG_FILE="/opt/bawabah-ai/logs/health.log"

response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $response -eq 200 ]; then
    echo "$(date): Health check passed" >> $LOG_FILE
else
    echo "$(date): Health check failed (HTTP $response)" >> $LOG_FILE
    # Restart service
    docker-compose restart api
fi
```

**Cron Job:**
```bash
# Add to crontab
crontab -e

# Check every 5 minutes
*/5 * * * * /opt/bawabah-ai/health-check.sh
```

### Performance Monitoring

**Resource Monitoring:**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor Docker containers
docker stats

# Monitor disk usage
df -h
du -sh /opt/bawabah-ai/models
```

## Security Considerations

### Network Security

**Firewall Configuration:**
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct API access
```

**Docker Security:**
```yaml
# docker-compose.yml security settings
services:
  api:
    # ... other settings
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
```

### Application Security

**Environment Variables:**
```bash
# Secure environment file
chmod 600 .env
chown root:root .env
```

**Input Validation:**
- All inputs validated with Pydantic
- File type restrictions
- Size limits on uploads

**Error Handling:**
- No sensitive information in error messages
- Proper HTTP status codes
- Comprehensive logging

## Troubleshooting

### Common Issues

**1. Model Loading Failures**
```bash
# Check model cache directory
ls -la /app/models

# Check disk space
df -h

# Check logs
docker-compose logs api
```

**2. Memory Issues**
```bash
# Check memory usage
free -h
docker stats

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**3. Port Conflicts**
```bash
# Check port usage
sudo netstat -tlnp | grep :8000

# Kill process if needed
sudo kill -9 <PID>
```

**4. SSL Certificate Issues**
```bash
# Test SSL configuration
openssl s_client -connect your-domain.com:443

# Check certificate validity
sudo certbot certificates
```

### Debug Mode

**Enable Debug Mode:**
```bash
# Set in .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart service
docker-compose restart api
```

**View Debug Logs:**
```bash
docker-compose logs -f api
```

### Performance Issues

**Model Loading Optimization:**
```bash
# Pre-warm models
curl -X GET "http://localhost:8000/api/v1/text-to-speech/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "test"}'
```

**Resource Monitoring:**
```bash
# Monitor CPU and memory
htop

# Monitor disk I/O
iotop

# Monitor network
nethogs
```

### Backup and Recovery

**Model Backup:**
```bash
# Backup model cache
tar -czf models-backup-$(date +%Y%m%d).tar.gz /opt/bawabah-ai/models

# Backup configuration
cp .env .env.backup
```

**Recovery:**
```bash
# Restore models
tar -xzf models-backup-20240101.tar.gz -C /

# Restore configuration
cp .env.backup .env
```

## Scaling Considerations

### Horizontal Scaling

**Load Balancer Configuration:**
```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}
```

**Docker Swarm:**
```yaml
version: '3.8'
services:
  api:
    image: bawabah-ai
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### Vertical Scaling

**Resource Limits:**
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 8G
        reservations:
          cpus: '1.0'
          memory: 4G
```

This deployment guide provides comprehensive instructions for deploying the Bawabah AI API server in various environments, from development to production.
