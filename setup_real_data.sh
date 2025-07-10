#!/bin/bash
# Setup script for Elephas AI real data integration

echo "🚀 Setting up Elephas AI with real data integration..."

# Create database directory
mkdir -p /Users/eklavya/Desktop/scamshield-ai/database

# Install required Python packages
echo "📦 Installing required packages..."
cd /Users/eklavya/Desktop/scamshield-ai

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

echo "✅ Python packages installed"

# Check for PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL:"
    echo "   brew install postgresql"
    echo "   Or visit: https://www.postgresql.org/download/"
    exit 1
fi

# Check for Redis
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis not found. Installing Redis..."
    if command -v brew &> /dev/null; then
        brew install redis
    else
        echo "Please install Redis manually: https://redis.io/download"
        exit 1
    fi
fi

# Start Redis if not running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "🔥 Starting Redis..."
    redis-server --daemonize yes
fi

# Setup environment variables
if [ ! -f ".env" ]; then
    echo "📝 Creating environment configuration..."
    cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=elephas_ai
DB_USER=postgres
DB_PASSWORD=password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# External API Keys (Optional - for threat intelligence)
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here
PHISHTANK_API_KEY=your_phishtank_api_key_here

# Hugging Face Model
HF_MODEL_NAME=elephasai/elephas

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
EOF
    echo "✅ Environment file created (.env)"
    echo "📝 Please update the API keys in .env file for full functionality"
fi

# Setup PostgreSQL database
echo "🗄️  Setting up PostgreSQL database..."

# Create database and user
createdb elephas_ai 2>/dev/null || echo "Database elephas_ai already exists"

# Run database setup
psql -d elephas_ai -f database/setup.sql

echo "✅ Database setup completed"

# Create systemd service for automatic startup (Linux)
if command -v systemctl &> /dev/null; then
    echo "🔧 Creating systemd service..."
    sudo tee /etc/systemd/system/elephas-ai.service > /dev/null << EOF
[Unit]
Description=Elephas AI Enterprise Security API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn api.enhanced_routes:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable elephas-ai.service
    echo "✅ Systemd service created and enabled"
fi

# Create startup script for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Creating macOS startup script..."
    cat > start_elephas.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

# Start Redis if not running
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes
fi

# Start PostgreSQL if not running (for Homebrew installation)
if command -v brew &> /dev/null; then
    brew services start postgresql@14 2>/dev/null || brew services start postgresql 2>/dev/null
fi

# Start the API server
echo "🚀 Starting Elephas AI API server..."
uvicorn api.enhanced_routes:app --host 0.0.0.0 --port 8000 --reload
EOF

    chmod +x start_elephas.sh
    echo "✅ macOS startup script created (start_elephas.sh)"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update API keys in .env file for external threat intelligence"
echo "2. Start the server:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   ./start_elephas.sh"
else
    echo "   sudo systemctl start elephas-ai"
fi
echo "3. Open dashboard: http://localhost:8000"
echo ""
echo "🔗 Useful commands:"
echo "   View logs: tail -f scamshield.log"
echo "   Test API: curl http://localhost:8000/health"
echo "   Stop Redis: redis-cli shutdown"
echo "   Database shell: psql -d elephas_ai"
echo ""
echo "📊 Dashboard features:"
echo "   ✅ Real-time threat detection"
echo "   ✅ Database-backed analytics"
echo "   ✅ External threat intelligence"
echo "   ✅ Activity monitoring"
echo "   ✅ Performance metrics"
echo ""
