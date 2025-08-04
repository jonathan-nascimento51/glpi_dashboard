import os
import logging
from flask import Flask
from flask_cors import CORS

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Enable CORS for frontend-backend communication
CORS(app, origins=["http://localhost:5000"])

# Configure app settings
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Register routes
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
