#!/bin/bash

echo "🎙️  Voice Verification Web Server"
echo "=================================="

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing requirements..."
    pip3 install -r requirements.txt
fi

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🚀 Starting Voice Verification Web Server..."
echo ""
echo "📍 Local Access:"
echo "   http://localhost:5000"
echo "   http://127.0.0.1:5000"
echo ""
echo "🌐 Network Access (other devices on your network):"
echo "   http://${LOCAL_IP}:5000"
echo ""
echo "📱 Use the network URL on phones/tablets connected to the same WiFi"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python3 app.py