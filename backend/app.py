#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Dashboard Backend Application
Main Flask application entry point
"""

import os
import sys
import logging
import redis
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import configurations and routes
from config.settings import active_config
from api.routes import api_bp
from routes.maintenance_routes import maintenance_bp
from utils.response_formatter import ResponseFormatter

# Configure logging
logging.basicConfig(
    level=getattr(logging, active_config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global cache instance
cache = Cache()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name:
        app.config.from_object(config_name)
    else:
        # Load from environment or default
        app.config['DEBUG'] = active_config.DEBUG
        app.config['SECRET_KEY'] = active_config.SECRET_KEY or 'dev-secret-key'
        app.config['REDIS_URL'] = getattr(active_config, 'REDIS_URL', 'redis://localhost:6379/0')
        app.config['CACHE_DEFAULT_TIMEOUT'] = getattr(active_config, 'CACHE_DEFAULT_TIMEOUT', 300)
    
    # Configure cache with Redis and fallback
    try:
        # Try to connect to Redis
        redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379/0'))
        redis_client.ping()  # Test connection
        
        cache_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'CACHE_KEY_PREFIX': 'glpi_dashboard:'
        }
        logger.info("✓ Redis cache configured successfully")
        
    except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
        # Fallback to SimpleCache if Redis is not available
        logger.warning(f"⚠ Redis not available ({e}), using SimpleCache as fallback")
        cache_config = {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        }
    
    app.config.update(cache_config)
    cache.init_app(app)
    
    # Enable CORS with proper headers
    CORS(app, 
         origins=[
             "http://localhost:3000",
             "http://127.0.0.1:3000",
             "http://localhost:3001",
             "http://127.0.0.1:3001",
             "http://localhost:5173",
             "http://127.0.0.1:5173"
         ],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True
    )
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        logger.info(f"REQUEST: {request.method} {request.path} from {request.remote_addr}")
        
    # Adicionar cabeçalhos CORS manualmente para garantir compatibilidade com testes
    @app.after_request
    def after_request(response):
        # Log response
        logger.info(f"RESPONSE: {response.status_code} for {request.method} {request.path}")
        
        # Só adicionar headers se não estiverem presentes (evitar duplicação)
        if not response.headers.get('Access-Control-Allow-Origin'):
            response.headers.add('Access-Control-Allow-Origin', '*')
        if not response.headers.get('Access-Control-Allow-Headers'):
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        if not response.headers.get('Access-Control-Allow-Methods'):
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        if not response.headers.get('Access-Control-Allow-Credentials'):
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(maintenance_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return ResponseFormatter.success({
            'status': 'healthy',
            'service': 'GLPI Dashboard Backend',
            'version': '1.0.0'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return ResponseFormatter.error('Endpoint not found', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return ResponseFormatter.error('Internal server error', 500)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        return ResponseFormatter.error('An unexpected error occurred', 500)
    
    logger.info(f"Flask app created with config: {active_config.__class__.__name__}")
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = active_config.DEBUG
    
    logger.info(f"Starting GLPI Dashboard Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Config: {active_config.__class__.__name__}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )