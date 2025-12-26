#!/bin/bash

# mkh_Manus - Quick Start Script
# هذا السكريبت يقوم بتشغيل المشروع بسرعة

set -e

echo "=================================="
echo "🚀 mkh_Manus - Starting Server"
echo "=================================="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "✓ Running in Docker container"
    exec python3 -m uvicorn run_server:app --host 0.0.0.0 --port 8000
    exit 0
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check if requirements are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 Installing Python requirements..."
    pip install -r requirements.txt
else
    echo "✓ Python requirements already installed"
fi

# Check if frontend is built
if [ ! -d "manus_pro/frontend/dist" ]; then
    echo "📦 Building frontend..."
    cd manus_pro/frontend
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed. Please install Node.js"
        exit 1
    fi
    
    npm install
    npm run build
    cd ../..
    echo "✓ Frontend built successfully"
else
    echo "✓ Frontend already built"
fi

echo ""
echo "=================================="
echo "🎉 Starting mkh_Manus Server..."
echo "=================================="
echo ""
echo "📍 Server will be available at:"
echo "   http://localhost:8000"
echo ""
echo "⚙️  To add API keys:"
echo "   1. Open http://localhost:8000"
echo "   2. Click on 'الإعدادات' (Settings)"
echo "   3. Add your Cerebras API keys"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 run_server.py
