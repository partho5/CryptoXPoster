#!/bin/bash

echo "🚀 Deploying Crypto News Scraper with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy env.example to .env and fill in your API keys:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Build and start the containers
echo "🐳 Building and starting Docker containers..."
docker-compose up -d --build

# Wait for the container to be healthy
echo "⏳ Waiting for container to be healthy..."
sleep 10

# Check if the container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Container is running!"
    echo "🌐 Server is available at: http://localhost:8080"
    echo "📊 Check logs with: docker-compose logs -f"
    echo "🛑 Stop with: docker-compose down"
else
    echo "❌ Container failed to start!"
    echo "📋 Check logs: docker-compose logs"
    exit 1
fi

echo "🎉 Deployment complete!" 