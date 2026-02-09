"""
Vercel Serverless Entry Point
Routes all /api/* requests to the Flask app.
"""
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from api.app import app

# Vercel expects a WSGI-compatible app
app.debug = False
