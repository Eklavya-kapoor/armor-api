# 🚀 Elephas AI Render Deployment Steps

## ✅ Pre-Deployment Complete
- [x] Code pushed to Hugging Face repository: `hf.co:elephasai/elephas`
- [x] Private model configured: `elephasai/elephas`
- [x] Render.yaml ready with all environment variables
- [x] Git repository synced

## 🔧 Render Deployment Steps

### 1. Create New Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Choose "Connect a repository"

### 2. Connect Repository
- **Repository**: Connect to `elephasai/elephas` on Hugging Face
- **Alternative**: If connecting HF directly doesn't work, use GitHub:
  1. Mirror your HF repo to GitHub
  2. Connect the GitHub repository

### 3. Configure Service Settings
```
Name: elephas-ai-api
Runtime: Python 3
Region: Choose closest to your users
Branch: main
```

### 4. Build & Deploy Settings
```
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### 5. Environment Variables
**CRITICAL**: Set these in Render dashboard:

#### Required Variables:
```
PORT=8000
PYTHONPATH=/opt/render/project/src
ENVIRONMENT=production
MODEL_PATH=elephasai/elephas
LOG_LEVEL=INFO
```

#### **MOST IMPORTANT - Private Model Access:**
```
HF_TOKEN=hf_your_actual_token_here
```
**How to get HF_TOKEN:**
1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token with "Read" permissions
3. Copy the token (starts with `hf_`)
4. Paste it in Render environment variables

#### Optional Variables:
```
API_TITLE=Elephas AI Security API
API_VERSION=v2.0
API_DESCRIPTION=Advanced AI-powered threat detection and security analysis
```

### 6. Auto-Deploy
- ✅ Enable "Auto-Deploy"
- Branch: `main`

### 7. Deploy!
Click "Create Web Service" - Render will start building and deploying.

## 🔍 Deployment Verification

### Expected Build Process:
1. **Installing dependencies** (2-3 minutes)
2. **Downloading private model** (5-10 minutes)
3. **Starting application** (1-2 minutes)

### Health Check:
Once deployed, test these endpoints:
```bash
# Health check
curl https://elephas-ai-api.onrender.com/health

# API test
curl -X POST https://elephas-ai-api.onrender.com/scan \
  -H "Content-Type: application/json" \
  -d '{"text":"Congratulations! You won $1000"}'

# Dashboard
open https://elephas-ai-api.onrender.com/
```

## 🚨 Troubleshooting

### Common Issues:

#### 1. Model Download Fails
**Error**: `Repository not found or access denied`
**Solution**: Check HF_TOKEN is set correctly in Render environment variables

#### 2. Import Errors
**Error**: `ModuleNotFoundError: No module named 'core'`
**Solution**: Ensure `PYTHONPATH=/opt/render/project/src` is set

#### 3. Timeout During Build
**Error**: Build times out
**Solution**: This is normal for first deploy - model download takes time

#### 4. Port Issues
**Error**: Application doesn't start
**Solution**: Ensure `PORT=8000` environment variable is set

## 📊 Expected Performance
- **Cold Start**: 30-60 seconds (model loading)
- **Warm Response**: <2 seconds
- **Memory Usage**: ~1GB (free tier limit: 512MB - might need paid plan)

## 💡 Pro Tips
1. **Free Tier Limitation**: Your private model might be too large for free tier
2. **Upgrade to Starter Plan**: $7/month for 1GB RAM
3. **Monitor Logs**: Check Render logs for any issues
4. **Domain**: Your API will be at `https://elephas-ai-api.onrender.com`

## 🎯 Final Checklist
- [ ] Repository connected to Render
- [ ] Environment variables set (especially HF_TOKEN)
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `python main.py`
- [ ] Auto-deploy enabled
- [ ] Health check configured: `/health`

## 📞 Support
If you encounter issues:
1. Check Render build logs
2. Verify HF_TOKEN permissions
3. Test model access locally first
4. Consider upgrading to paid plan for larger models

---
**Ready to deploy! 🚀**
