#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Dashboard - Main Application Entry Point
This file serves as the main entry point and imports the backend application.
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the main application from backend
from backend.app import create_app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
