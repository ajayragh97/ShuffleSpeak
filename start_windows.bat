@echo off
echo =========================================
echo Launching Voice Session Recorder...
echo =========================================

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python.
    pause
    exit /b
)

:: If venv doesn't exist, do first-time setup
IF NOT EXIST "venv" (
    echo [First-time Setup Detected]
    echo Creating isolated virtual environment...
    python -m venv venv
    
    call venv\Scripts\activate.bat
    echo Installing python dependencies...
    pip install -r requirements.txt --quiet
) ELSE (
    :: Just activate if already installed
    call venv\Scripts\activate.bat
)

:: Run the application
echo Starting Application...
python app.py