#!/bin/bash

# 🐘 Elephas AI - Deployment Script
# This script prepares and deploys the Elephas AI API to Render

echo "🐘 Elephas AI - Deployment Preparation"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "render.yaml" ]; then
    echo "❌ Error: Please run this script from the elephas-ai directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run basic tests
echo "🧪 Running basic tests..."
python3 -c "
try:
    from api.enhanced_routes import app
    print('✅ FastAPI app imports successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Check render.yaml configuration
echo "⚙️ Verifying Render configuration..."
if grep -q "elephas-ai-api" render.yaml; then
    echo "✅ Render configuration verified"
else
    echo "❌ Render configuration needs updating"
    exit 1
fi

echo ""
echo "🚀 Ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Commit all changes to your git repository"
echo "2. Push to your main branch"
echo "3. Deploy to Render using the render.yaml configuration"
echo ""
echo "Deployment commands:"
echo "  git add ."
echo "  git commit -m 'Deploy Elephas AI v2.0'"
echo "  git push origin main"
echo ""
echo "Your API will be available at: https://elephas-ai-api.onrender.com"
echo "Dashboard will be accessible at: https://elephas-ai-api.onrender.com/"
