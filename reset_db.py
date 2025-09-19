#!/usr/bin/env python3
"""
Database reset script for NatureCards
Run this if you encounter database errors
"""

import os
from app import app, db

# Remove any existing database files
db_paths = ['flashcards.db', 'instance/flashcards.db']
for path in db_paths:
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Removed old database: {path}")

with app.app_context():
    print("🗄️ Dropping all tables...")
    db.drop_all()

    print("🌱 Creating new tables...")
    db.create_all()

    print("✅ Database reset complete!")
    print("🔐 You can now create user accounts and decks.")
    print("📝 The login will redirect to your notes page after successful authentication.")