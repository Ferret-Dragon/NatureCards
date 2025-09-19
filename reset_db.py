#!/usr/bin/env python3
"""
Database reset script for NatureCards
Run this if you encounter database errors
"""

from app import app, db

with app.app_context():
    print("🗄️ Dropping all tables...")
    db.drop_all()

    print("🌱 Creating new tables...")
    db.create_all()

    print("✅ Database reset complete!")
    print("🔐 You can now create user accounts and decks.")