#!/bin/bash

# Navigate to project directory
cd /var/www/xPosting

# Activate virtual environment
source venv/bin/activate

# Install PM2 if not already installed
if ! command -v pm2 &> /dev/null; then
    echo "Installing PM2..."
    npm install -g pm2
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup

echo "Crypto News Scraper started with PM2!"
echo "Check status with: pm2 status"
echo "View logs with: pm2 logs crypto-news-scraper" 