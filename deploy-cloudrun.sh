#!/bin/bash
# Deploy Elephas AI to Google Cloud Run

# Configuration
PROJECT_ID="your-gcp-project-id"  # Replace with your project ID
SERVICE_NAME="elephas-ai"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Elephas AI to Google Cloud Run..."

# Build and push image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.cloudrun -t $IMAGE_NAME .

echo "📤 Pushing to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🌟 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 900 \
  --concurrency 1000 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,MODEL_PATH=elephasai/elephas,LOG_LEVEL=INFO,PORT=8080" \
  --set-secrets="HF_TOKEN=HF_TOKEN:latest"

echo "✅ Deployment complete!"
echo "🌐 Your API is available at: https://$SERVICE_NAME-$REGION-$PROJECT_ID.run.app"
echo "🔍 Test with: curl https://$SERVICE_NAME-$REGION-$PROJECT_ID.run.app/health"
