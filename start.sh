#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PORT=8080
export HOST=0.0.0.0
export AUTH_CODE=59bd0119d5fec5ffa3622e196ab5fd10

# Start the server
python3 passenger_wsgi.py 