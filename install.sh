#!/bin/bash

# NatureCards Installation Script for Unix/macOS
# This script sets up the virtual environment and installs all dependencies

echo "🌿 Setting up NatureCards Flashcard Application"
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "📍 Using Python: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🌱 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🌱 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🌱 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "🌱 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🌱 Initializing database..."
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 To run the application:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run the app: python app.py"
echo "   3. Open http://127.0.0.1:5000 in your browser"
echo ""
echo "🌿 Happy studying!"