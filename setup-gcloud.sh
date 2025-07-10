# Google Cloud Run Setup Script
# Run this once to set up your project

echo "🌟 Setting up Google Cloud Run for Elephas AI..."

# 1. Install Google Cloud CLI (if not installed)
echo "📦 Installing Google Cloud CLI..."
# On macOS:
brew install google-cloud-sdk

# 2. Initialize and login
echo "🔐 Login to Google Cloud..."
gcloud init
gcloud auth login

# 3. Enable required APIs
echo "⚡ Enabling Cloud Run API..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 4. Set default region
gcloud config set run/region us-central1

echo "✅ Setup complete! Ready to deploy."
