#!/bin/bash
echo "========================================="
echo "Launching Voice Session Recorder..."
echo "========================================="

# Check if the virtual environment exists
if [ ! -d "voice_recorder" ]; then
    echo "[First-time Setup Detected]"
    echo "Installing required system packages (may ask for sudo password)..."
    
    sudo apt-get update -y
    sudo apt-get install -y python3-venv python3-tk portaudio19-dev python3-dev build-essential
    
    echo "Creating isolated virtual environment..."
    python3 -m venv voice_recorder
    
    echo "Installing python dependencies..."
    source voice_recorder/bin/activate
    pip install -r requirements.txt -q
else
    # If venv exists, just activate it and skip all the installation steps
    source voice_recorder/bin/activate
fi

# Run the application
echo "Starting Application..."
python3 app.py