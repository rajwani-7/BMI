#!/bin/bash

echo "========================================"
echo "  HealthCompanion - Flask Application"
echo "  High-Tech Gym Theme"
echo "========================================"
echo ""

echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "Starting Flask server..."
echo ""
echo "Access the application at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
