@echo off
REM NatureCards Installation Script for Windows
REM This script sets up the virtual environment and installs all dependencies

echo 🌿 Setting up NatureCards Flashcard Application
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python first.
    pause
    exit /b 1
)

echo 📍 Using Python:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🌱 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🌱 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo 🌱 Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo 🌱 Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo 🌱 Initializing database...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 To run the application:
echo    1. Activate virtual environment: venv\Scripts\activate
echo    2. Run the app: python app.py
echo    3. Open http://127.0.0.1:5000 in your browser
echo.
echo 🌿 Happy studying!
pause