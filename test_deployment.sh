#!/bin/bash

# 🐘 Elephas AI Pre-Deployment Test Script
# Run this before deploying to Render to catch any issues

echo "🐘 Testing Elephas AI before deployment..."

# Check Python version
echo "📍 Python version:"
python3 --version

# Check if all required files exist
echo "📍 Checking required files..."
required_files=(
    "main.py"
    "api/enhanced_routes.py"
    "requirements.txt"
    "render.yaml"
    "Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Test Python syntax
echo "📍 Testing Python syntax..."
python3 -m py_compile main.py
if [ $? -eq 0 ]; then
    echo "✅ main.py syntax OK"
else
    echo "❌ main.py syntax error"
    exit 1
fi

python3 -m py_compile api/enhanced_routes.py
if [ $? -eq 0 ]; then
    echo "✅ enhanced_routes.py syntax OK"
else
    echo "❌ enhanced_routes.py syntax error"
    exit 1
fi

# Check requirements.txt
echo "📍 Checking requirements.txt..."
if [ -s requirements.txt ]; then
    echo "✅ requirements.txt has content"
    echo "📋 Dependencies:"
    head -10 requirements.txt
else
    echo "❌ requirements.txt is empty"
    exit 1
fi

# Test imports (basic check)
echo "📍 Testing basic imports..."
python3 -c "
try:
    from fastapi import FastAPI
    print('✅ FastAPI import OK')
except ImportError as e:
    print(f'❌ FastAPI import failed: {e}')
    exit(1)
"

# Check render.yaml format
echo "📍 Checking render.yaml format..."
if command -v python3 &> /dev/null; then
    python3 -c "
import yaml
try:
    with open('render.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('✅ render.yaml format OK')
    print(f'📋 Service name: {config.get(\"services\", [{}])[0].get(\"name\", \"N/A\")}')
except Exception as e:
    print(f'❌ render.yaml format error: {e}')
    exit(1)
"
fi

# Check for any remaining ScamShield references
echo "📍 Checking for old ScamShield references..."
scamshield_refs=$(grep -r "ScamShield\|scamshield" --include="*.py" . | grep -v ".git" | wc -l)
if [ "$scamshield_refs" -gt 0 ]; then
    echo "⚠️  Found $scamshield_refs ScamShield references that may need updating:"
    grep -r "ScamShield\|scamshield" --include="*.py" . | grep -v ".git" | head -5
else
    echo "✅ No ScamShield references found"
fi

# Test dashboard files
echo "📍 Checking dashboard files..."
dashboard_path="../elephas-ai-sdk/dashboard"
if [ -f "$dashboard_path/index.html" ]; then
    echo "✅ Dashboard found at $dashboard_path"
else
    echo "⚠️  Dashboard not found at expected path"
fi

echo ""
echo "🎉 Pre-deployment test complete!"
echo ""
echo "🚀 Ready for Render deployment:"
echo "1. Commit all changes: git add . && git commit -m 'Ready for deployment'"
echo "2. Push to GitHub: git push origin main"
echo "3. Deploy on Render with settings from DEPLOYMENT_GUIDE.md"
echo ""
echo "🔗 Remember to set these environment variables in Render:"
echo "   - PYTHONPATH=/opt/render/project/src"
echo "   - PORT=8000"
echo ""
echo "📊 Test the deployment with:"
echo "   curl https://your-app.onrender.com/health"
