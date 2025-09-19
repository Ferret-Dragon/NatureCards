#!/usr/bin/env python3
"""
Simple test to check what's causing the internal server error
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def test():
    return "🌿 NatureCards Test - If you see this, Flask is working!"

@app.route('/test-db')
def test_db():
    try:
        # Test database connection
        result = db.engine.execute('SELECT 1').scalar()
        return f"Database working! Result: {result}"
    except Exception as e:
        return f"Database error: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🧪 Running test app on http://localhost:5000")
    print("🧪 Visit /test-db to check database connection")
    app.run(debug=True, port=5000)