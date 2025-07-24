#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.api.app_production import create_app

# Create the Flask app
app = create_app('production')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)