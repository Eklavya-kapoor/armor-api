# 🐘 Elephas AI - Render Deployment Guide

## Overview
Complete guide for deploying Elephas AI (formerly ScamShield) to Render.com with the new branding.

## Pre-deployment Checklist

### ✅ Completed Rebranding
- [x] Main orchestrator class renamed to `ElephasAIOrchestrator`
- [x] FastAPI app title updated to "Elephas AI - Enterprise Security API"
- [x] Log files renamed from `scamshield.log` to `elephas-ai.log`
- [x] All model versions updated to "Elephas-AI-v2.0"
- [x] API documentation and descriptions updated
- [x] Test files updated with new branding
- [x] Configuration files updated

### 📁 Key Files for Deployment
- `main.py` - Main application entry point
- `api/enhanced_routes.py` - FastAPI routes and API logic
- `render.yaml` - Render deployment configuration
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `deploy.sh` - Deployment script

## Render Configuration

### Service Settings
```yaml
Service Name: elephas-ai-api
Environment: Python 3.11+
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### Environment Variables
Set these in your Render dashboard:

#### Required
```
PYTHONPATH=/opt/render/project/src
PORT=8000
```

#### Optional (for enhanced features)
```
DB_HOST=your-database-host
DB_USER=elephas_ai_user
DB_PASSWORD=your-secure-password
DB_NAME=elephas_ai
API_KEY=your-secure-api-key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Domain Configuration
- **Custom Domain**: `elephas-ai-api.onrender.com`
- **Health Check**: `GET /`
- **Auto-Deploy**: Enable from main branch

## Deployment Steps

### 1. Repository Setup
```bash
# Ensure all files are committed
git add .
git commit -m "Complete Elephas AI rebranding"
git push origin main
```

### 2. Render Service Creation
1. Connect your GitHub repository to Render
2. Create new Web Service
3. Select repository: `scamshield-ai` (or rename repo to `elephas-ai`)
4. Configure build and start commands as above
5. Set environment variables
6. Deploy

### 3. Post-Deployment Verification
```bash
# Test API endpoints
curl https://elephas-ai-api.onrender.com/
curl https://elephas-ai-api.onrender.com/health
curl -X POST https://elephas-ai-api.onrender.com/scan \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, this is a test message"}'
```

## API Endpoints

### Core Endpoints
- `GET /` - Dashboard interface
- `GET /health` - Health check
- `POST /scan` - Scam detection
- `GET /dashboard-stats` - Statistics
- `GET /activities` - Recent activities
- `GET /threat-data` - Threat analytics

### Dashboard Access
- URL: `https://elephas-ai-api.onrender.com/`
- Username: `admin`
- Password: `secure123`

## Monitoring & Maintenance

### Logs
- Application logs available in Render dashboard
- Log file: `elephas-ai.log` (if persistent storage configured)

### Performance
- Expected cold start: 30-60 seconds
- Response time: < 2 seconds for scam detection
- Memory usage: ~512MB typical

### Scaling
- Auto-scaling configured in `render.yaml`
- Horizontal scaling available for enterprise plans

## Troubleshooting

### Common Issues

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'core'
```
**Solution**: Ensure `PYTHONPATH=/opt/render/project/src` is set

#### 2. Model Loading Issues
```
Error loading BERT model
```
**Solution**: Check if model files are included or download on first run

#### 3. Database Connection
```
Database connection failed
```
**Solution**: Verify database environment variables

### Support Commands
```bash
# Check service status
curl https://elephas-ai-api.onrender.com/health

# View recent logs (via Render dashboard)
# Check environment variables (via Render dashboard)
```

## Security Considerations

### API Security
- CORS configured for dashboard access
- Rate limiting recommended for production
- API key authentication for sensitive endpoints

### Data Privacy
- No user data stored by default
- Scan results not persisted unless configured
- Logs contain no sensitive information

## Next Steps

1. **Custom Domain**: Configure your own domain
2. **SSL Certificate**: Automatic with Render
3. **Database**: Add PostgreSQL for persistent data
4. **Monitoring**: Integrate with monitoring services
5. **CDN**: Consider CloudFlare for global performance

## Support

For deployment issues:
- Check Render logs
- Review this guide
- Test locally first with `python main.py`

---

**Elephas AI** - Intelligent Threat Detection Platform
