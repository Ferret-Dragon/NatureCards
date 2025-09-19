#!/usr/bin/env python3
"""
Setup script for NatureCards Flashcard Application
Automatically creates virtual environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🌱 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Output: {e.output}")
        sys.exit(1)

def main():
    print("🌿 Setting up NatureCards Flashcard Application")
    print("=" * 50)

    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Check if Python 3 is available
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"📍 Using Python: {result.stdout.strip()}")
    except:
        print("❌ Python not found")
        sys.exit(1)

    # Create virtual environment
    venv_name = "venv"
    if not os.path.exists(venv_name):
        run_command(f"{sys.executable} -m venv {venv_name}", "Creating virtual environment")
    else:
        print(f"✅ Virtual environment '{venv_name}' already exists")

    # Determine activation script path based on OS
    if os.name == 'nt':  # Windows
        activate_script = f"{venv_name}\\Scripts\\activate"
        pip_path = f"{venv_name}\\Scripts\\pip"
        python_path = f"{venv_name}\\Scripts\\python"
    else:  # Unix/macOS
        activate_script = f"{venv_name}/bin/activate"
        pip_path = f"{venv_name}/bin/pip"
        python_path = f"{venv_name}/bin/python"

    # Install dependencies
    run_command(f"{pip_path} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies")

    # Initialize database
    run_command(f"{python_path} -c \"from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')\"", "Initializing database")

    print("\n🎉 Setup completed successfully!")
    print("\n📋 To run the application:")
    print(f"   1. Activate virtual environment: source {activate_script}")
    print(f"   2. Run the app: python app.py")
    print("   3. Open http://127.0.0.1:5000 in your browser")
    print("\n🌿 Happy studying!")

if __name__ == "__main__":
    main()