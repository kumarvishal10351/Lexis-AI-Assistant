# Lexis AI Assistant - Deployment Guide

## Table of Contents
1. [Local Deployment](#local-deployment)
2. [Streamlit Cloud](#streamlit-cloud-recommended)
3. [Docker Deployment](#docker-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [Production Checklist](#production-checklist)

---

## Local Deployment

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment tool (venv or conda)

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/lexis-ai-assistant.git
cd lexis-ai-assistant
```

#### 2. Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Mistral API key
nano .env
# or
code .env
```

#### 5. Create Data Directory
```bash
mkdir -p data
```

#### 6. Run Application
```bash
streamlit run lexis_improved.py
```

Application will be available at: `http://localhost:8501`

### Local Deployment Troubleshooting

**Issue: ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

**Issue: Port 8501 already in use**
```bash
# Use different port
streamlit run lexis_improved.py --server.port 8502
```

**Issue: MISTRAL_API_KEY not recognized**
```bash
# Verify .env file exists and format is correct
cat .env

# Ensure no quotes around key
MISTRAL_API_KEY=actual_key_without_quotes
```

---

## Streamlit Cloud (Recommended)

### Why Streamlit Cloud?
- ✅ Free tier available
- ✅ Automatic deployment from GitHub
- ✅ Built-in secrets management
- ✅ Easy version updates
- ✅ Custom domain support

### Deployment Steps

#### 1. Prepare GitHub Repository
```bash
# Initialize if not already done
git init
git add .
git commit -m "Initial commit: Lexis AI Assistant"

# Push to GitHub (ensure private if using API keys)
git push origin main
```

#### 2. Create Streamlit Account
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in with GitHub"
3. Authorize Streamlit

#### 3. Deploy Application
1. Click "New app" button
2. Select your repository
3. Select branch (main)
4. Set main file path to `lexis_improved.py`
5. Click "Deploy"

#### 4. Configure Secrets
1. Go to App Settings (gear icon)
2. Click "Secrets" tab
3. Add secret:
```
MISTRAL_API_KEY = your_api_key_here
```
4. Save and app will automatically reload

#### 5. Verify Deployment
- Check deployment logs
- Test with sample PDF
- Verify all features work

### Advanced Streamlit Cloud Configuration

#### Custom Domain
1. Go to App Settings > Custom Domain
2. Enter your domain
3. Follow DNS instructions
4. Verify

#### Environment Variables
Add to `~/.streamlit/secrets.toml`:
```toml
# Secrets
MISTRAL_API_KEY = "your_key"

# Optional configuration
streamlit_logger_level = "info"
client_maxuploadsize = 200
```

#### Requirements for Cloud
Ensure `requirements.txt` has pinned versions:
```
streamlit==1.28.1
langchain==0.1.9
langchain-mistralai==0.1.0
# etc...
```

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Hub account (optional)

### Create Dockerfile

Create `Dockerfile` in project root:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY lexis_improved.py .
COPY .streamlit /app/.streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "lexis_improved.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create .streamlit/config.toml

```toml
[client]
showErrorDetails = true
maxUploadSize = 200

[server]
port = 8501
headless = true
enableXsrfProtection = true

[logger]
level = "info"
```

### Build and Run

#### Local Docker Build
```bash
# Build image
docker build -t lexis-app .

# Run container
docker run -p 8501:8501 \
  -e MISTRAL_API_KEY="your_api_key" \
  -v lexis_data:/app/data \
  -v lexis_chroma:/app/chroma_db \
  lexis-app
```

#### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  lexis:
    build: .
    ports:
      - "8501:8501"
    environment:
      MISTRAL_API_KEY: ${MISTRAL_API_KEY}
      STREAMLIT_SERVER_HEADLESS: "true"
    volumes:
      - lexis_data:/app/data
      - lexis_chroma:/app/chroma_db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  lexis_data:
  lexis_chroma:
```

Deploy:
```bash
# Copy environment
cp .env.example .env
# Edit .env with your API key

# Run
docker-compose up -d

# View logs
docker-compose logs -f lexis

# Stop
docker-compose down
```

---

## AWS Deployment

### Using AWS App Runner

#### Step 1: Prepare Repository
```bash
# Ensure .dockerignore exists
# Ensure Dockerfile is in root
git push origin main
```

#### Step 2: AWS Setup
1. Go to AWS App Runner console
2. Click "Create service"
3. Select "Source code repository"
4. Connect GitHub
5. Select repository and branch
6. Configure:
   - Port: 8501
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run lexis_improved.py --server.port=8501 --server.address=0.0.0.0`

#### Step 3: Environment Variables
In App Runner settings:
1. Go to "Environment variables"
2. Add:
   - Key: `MISTRAL_API_KEY`
   - Value: Your API key (from Secrets Manager)

#### Step 4: Deploy
1. Click "Create and deploy"
2. Wait for build (5-10 minutes)
3. Access via provided URL

### Using EC2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-instance.com

# Update system
sudo yum update -y

# Install Python
sudo yum install python3.11 python3.11-venv -y

# Clone repository
git clone https://github.com/yourusername/lexis.git
cd lexis

# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/lexis.service
```

Add to systemd service:
```ini
[Unit]
Description=Lexis AI Assistant
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/lexis
Environment="MISTRAL_API_KEY=your_key"
ExecStart=/home/ec2-user/lexis/venv/bin/streamlit run lexis_improved.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable lexis
sudo systemctl start lexis
sudo systemctl status lexis
```

---

## Heroku Deployment

### Create Procfile

```
web: streamlit run lexis_improved.py --server.port=$PORT --server.address=0.0.0.0
```

### Create runtime.txt

```
python-3.11.5
```

### Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create lexis-ai-app

# Set environment variable
heroku config:set MISTRAL_API_KEY=your_key

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Scale
heroku ps:scale web=1
```

---

## Production Checklist

### Pre-Deployment
- [ ] All dependencies in requirements.txt
- [ ] .env.example created
- [ ] No hardcoded secrets
- [ ] Tests passed
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Logging configured

### Security
- [ ] API keys in environment variables
- [ ] HTTPS enabled
- [ ] Input validation
- [ ] CORS configured if needed
- [ ] Rate limiting enabled
- [ ] File upload limits set
- [ ] No debug mode in production

### Performance
- [ ] Configuration optimized
- [ ] Caching enabled
- [ ] Database indexes
- [ ] Response times measured
- [ ] Load testing completed
- [ ] Auto-scaling configured (if cloud)

### Monitoring
- [ ] Logging setup
- [ ] Error tracking
- [ ] Performance monitoring
- [ ] Health checks
- [ ] Uptime monitoring
- [ ] Analytics enabled

### Documentation
- [ ] Deployment steps documented
- [ ] Configuration documented
- [ ] Troubleshooting guide
- [ ] API documentation
- [ ] Runbooks created
- [ ] Architecture documented

### Backup & Recovery
- [ ] Data backup strategy
- [ ] Vector store backups
- [ ] Chat history backups
- [ ] Recovery procedures tested
- [ ] Disaster recovery plan

### Maintenance
- [ ] Update schedule
- [ ] Dependency updates
- [ ] Security patches
- [ ] Performance tuning
- [ ] Cost monitoring (cloud)

---

## Monitoring & Logging

### Application Logs

View in different environments:

**Local:**
```bash
# Console output
streamlit run lexis_improved.py
```

**Docker:**
```bash
docker-compose logs -f lexis
```

**Streamlit Cloud:**
1. Go to App Settings
2. Click "View logs"

### Key Metrics to Monitor

```python
# Logged automatically in data/analytics.json:
- Query count per hour
- Average confidence score
- Response times
- Documents retrieved
- Error rate
- Popular queries
```

### Alerting Setup

Set up alerts for:
- Error rate > 5%
- Response time > 10s
- API failures
- Disk space < 1GB
- Memory usage > 80%

---

## Scaling Considerations

### Vertical Scaling
- Increase chunk_size for better context
- Increase retriever_k for more comprehensive results
- Increase machine specs if response times slow

### Horizontal Scaling
- Use load balancer (AWS ALB, Google Cloud LB)
- Shared vector database (Chroma Cloud)
- Shared chat history (Redis, PostgreSQL)
- Queue system for heavy tasks (Celery)

### Cost Optimization
- Use cheaper models for non-critical tasks
- Implement caching layer (Redis)
- Optimize vector store size
- Monitor API costs
- Use spot instances (AWS)

---

## Troubleshooting Deployments

### Streamlit Cloud Issues

**App won't load:**
```
1. Check App Settings > Logs
2. Verify requirements.txt compatibility
3. Clear browser cache
4. Restart app (Settings > Reboot app)
```

**Secrets not working:**
```
1. Verify exact key name in secrets
2. Reload page after updating secrets
3. Check app logs for KeyError
```

### Docker Issues

**Build fails:**
```bash
docker build --no-cache -t lexis-app .
```

**Container exits:**
```bash
docker logs container_id
```

### AWS Issues

**App Runner service fails:**
1. Check CloudWatch logs
2. Verify build succeeded
3. Check environment variables
4. Verify port configuration

---

## Post-Deployment

### Verify Functionality
1. Upload test PDF
2. Ask test question
3. Verify answer accuracy
4. Check response time
5. Review sources

### Performance Baseline
```
Record initial metrics:
- Response time: X seconds
- Confidence score: X%
- API costs: $X/month
- Resource usage: X%
```

### User Training
- Share deployment URL
- Provide usage guide
- Set expectations for limitations
- Create feedback channel

---

## Support & Updates

### Getting Help
- Check logs
- Review error messages
- Consult troubleshooting section
- Check Mistral API status

### Updating
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Redeploy
git push origin main  # For cloud deployments
docker-compose up -d --build  # For Docker
```

---

**Version**: 2.0.0  
**Last Updated**: 2026-03-27  
**Status**: Production Ready ✅
