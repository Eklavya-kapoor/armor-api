# 🆓 Deploy Your Private Model on Render Free Tier

## Strategy: Memory Optimization for 512MB Limit

Your private model `elephasai/elephas` can work on Render's free tier! Here's how to optimize it:

### Option 1: Memory-Optimized BERT Classifier
   
   # Fix the repository sync
   git pull origin main --allow-unrelated-histories
   git push origin main
   ```

2. **Create Render Service:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:

#### Option B: Manual Deployment
If GitHub sync fails, you can deploy manually:

1. **Create New Repository:**
   ```bash
   # Create a new repo on GitHub
   # Then push to it
   git remote set-url origin https://github.com/yourusername/elephas-ai.git
   git push -u origin main
   ```

### Step 3: Render Configuration

**Build Settings:**
```yaml
Name: elephas-ai-api
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

**Environment Variables:**
```bash
# CRITICAL: Set these in Render dashboard
HF_TOKEN=hf_your_token_here_from_step_1
MODEL_PATH=elephasai/elephas
ENVIRONMENT=production
LOG_LEVEL=INFO
PYTHONPATH=/opt/render/project/src
PORT=8000
```

### Step 4: Security Setup

**Important:** Never commit your HF_TOKEN to git. Set it only in Render's environment variables:

1. In Render dashboard → Your service → Environment
2. Add environment variable:
   - Key: `HF_TOKEN`
   - Value: `hf_your_actual_token`
   - Keep "Secret" checked

### Step 5: Deployment Process

1. **Commit and Push:**
   ```bash
   git add .
   git commit -m "Deploy Elephas AI with private model"
   git push origin main
   ```

2. **Deploy on Render:**
   - Service will auto-deploy from GitHub
   - Watch logs for any issues
   - First deployment takes 5-10 minutes

### Step 6: Test Deployment

```bash
# Health check
curl https://elephas-ai-api.onrender.com/health

# Test API
curl -X POST https://elephas-ai-api.onrender.com/scan \
  -H "Content-Type: application/json" \
  -d '{"text":"Congratulations! You won $1000. Click here to claim."}'
```

## 🔧 Troubleshooting

### Model Loading Issues
If you see: `❌ Failed to load BERT model`

**Solution:**
1. Check HF_TOKEN is set correctly
2. Verify model path: `elephasai/elephas`
3. Ensure model is accessible with your token

### Build Failures
If build fails with dependencies:

**Solution:**
1. Check `requirements.txt` includes all dependencies
2. Try upgrading pip: add `pip install --upgrade pip` to build command

### Git Sync Issues
If still having git problems:

**Quick Fix:**
```bash
# Create fresh repo
cd /Users/eklavya/Desktop/
cp -r scamshield-ai elephas-ai-fresh
cd elephas-ai-fresh
rm -rf .git
git init
git add .
git commit -m "Initial Elephas AI deployment"
# Push to new GitHub repo
```

## 📊 Expected Performance

- **Cold Start:** 60-120 seconds (model download)
- **Warm Response:** < 2 seconds
- **Memory Usage:** ~1GB (for BERT model)
- **Model Size:** ~500MB

## 🎯 Final Checklist

- [ ] HF_TOKEN set in Render (not in code)
- [ ] MODEL_PATH set to `elephasai/elephas`
- [ ] Git repository synced
- [ ] All environment variables configured
- [ ] Service deployed and running
- [ ] Health check passing
- [ ] API endpoints working

---

**Ready to deploy your private Elephas AI model! 🚀**
