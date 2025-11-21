#!/bin/bash

# TradingAgents Deployment Helper Script
# This script helps prepare your project for deployment

set -e

echo "🚀 TradingAgents Deployment Helper"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys."
    echo ""
fi

# Function to check if API key is set
check_api_key() {
    local key_name=$1
    local key_value=$(grep "^${key_name}=" .env | cut -d '=' -f2)
    
    if [ -z "$key_value" ] || [ "$key_value" = "${key_name,,}_placeholder" ]; then
        echo "❌ $key_name is not set"
        return 1
    else
        echo "✅ $key_name is set"
        return 0
    fi
}

echo "Checking required API keys..."
echo ""

# Check required keys
OPENAI_OK=false
ALPHA_OK=false

if check_api_key "OPENAI_API_KEY"; then
    OPENAI_OK=true
fi

if check_api_key "ALPHA_VANTAGE_API_KEY"; then
    ALPHA_OK=true
fi

echo ""

if [ "$OPENAI_OK" = false ] || [ "$ALPHA_OK" = false ]; then
    echo "⚠️  API keys are missing in .env file."
    echo "   You can proceed if you intend to use BYOK (Bring Your Own Key) mode,"
    echo "   where users must enter their keys in the frontend."
    echo ""
    read -p "Do you want to proceed with BYOK mode? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please set the required API keys in .env file before deploying."
        exit 1
    fi
fi

echo "✅ All required API keys are configured!"
echo ""

# Display deployment options
echo "📦 Deployment Options:"
echo ""
echo "1. Vercel (Frontend) + Render (Backend) - FREE"
echo "   - Best for: Personal projects, testing"
echo "   - See DEPLOY.md for detailed instructions"
echo ""
echo "2. Railway - FREE tier available"
echo "   - Best for: All-in-one deployment"
echo "   - See DEPLOY.md for detailed instructions"
echo ""
echo "3. Docker Compose - Self-hosted"
echo "   - Best for: VPS deployment"
echo "   - Run: docker-compose up -d"
echo ""

# Ask user which deployment method
echo "Which deployment method would you like to use?"
echo "1) Vercel + Render (Recommended for free)"
echo "2) Railway"
echo "3) Docker Compose"
echo "4) Just show me the guide"
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📖 Vercel + Render Deployment"
        echo "=============================="
        echo ""
        echo "Step 1: Deploy Backend to Render"
        echo "  1. Go to https://render.com and sign in with GitHub"
        echo "  2. Click 'New +' → 'Web Service'"
        echo "  3. Connect your repository"
        echo "  4. Configure:"
        echo "     - Root Directory: backend"
        echo "     - Build Command: pip install -r requirements.txt"
        echo "     - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo "  5. Add environment variables from your .env file"
        echo "  6. Deploy!"
        echo ""
        echo "Step 2: Deploy Frontend to Vercel"
        echo "  1. Go to https://vercel.com and sign in with GitHub"
        echo "  2. Click 'Add New...' → 'Project'"
        echo "  3. Select your repository"
        echo "  4. Configure:"
        echo "     - Root Directory: frontend"
        echo "     - Framework: Next.js"
        echo "  5. Add environment variable:"
        echo "     NEXT_PUBLIC_API_URL=<your-render-backend-url>"
        echo "  6. Deploy!"
        echo ""
        echo "📚 For detailed instructions, see DEPLOY.md"
        ;;
    2)
        echo ""
        echo "📖 Railway Deployment"
        echo "===================="
        echo ""
        echo "1. Go to https://railway.app and sign in with GitHub"
        echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "3. Select your repository"
        echo "4. Add two services (Backend and Frontend)"
        echo "5. Configure environment variables"
        echo ""
        echo "📚 For detailed instructions, see DEPLOY.md"
        ;;
    3)
        echo ""
        echo "📖 Docker Compose Deployment"
        echo "============================"
        echo ""
        echo "Running Docker Compose..."
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d
            echo ""
            echo "✅ Services started!"
            echo "   - Frontend: http://localhost:3000"
            echo "   - Backend: http://localhost:8000"
            echo ""
            echo "To view logs: docker-compose logs -f"
            echo "To stop: docker-compose down"
        else
            echo "❌ docker-compose not found. Please install Docker first."
            echo "   Visit: https://docs.docker.com/get-docker/"
        fi
        ;;
    4)
        echo ""
        echo "📚 Opening deployment guide..."
        if [ -f "DEPLOY.md" ]; then
            if command -v open &> /dev/null; then
                open DEPLOY.md
            elif command -v xdg-open &> /dev/null; then
                xdg-open DEPLOY.md
            else
                cat DEPLOY.md
            fi
        else
            echo "❌ DEPLOY.md not found"
        fi
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Good luck with your deployment!"
