from flask import Flask, Response
from flask_cors import CORS
from api.routes import api_bp
from api.server_metrics import metrics_bp, track_request_metrics
from config.settings import get_config
from utils.structured_logger import create_glpi_logger
from utils.observability_middleware import ObservabilityMiddleware

def create_app():
    app = Flask(__name__)
    
    # Get configuration instance
    config = get_config()
    app.config.from_object(config)
    
    # Security: Use configured CORS origins instead of wildcard
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Add security headers for production
    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """Add security headers to all responses"""
        # Only add security headers in production/non-debug mode
        if not app.config.get('DEBUG', False) and hasattr(config, 'SECURITY_HEADERS'):
            security_headers = getattr(config, 'SECURITY_HEADERS', {})
            for header_key, header_value in security_headers.items():
                # Convert header key format (e.g., STRICT_TRANSPORT_SECURITY -> Strict-Transport-Security)
                header_name = header_key.replace('_', '-').title()
                response.headers[header_name] = header_value
        
        # Add cache control headers for static content security
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    
    # Setup structured logging
    logger = create_glpi_logger()
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(metrics_bp)  # Server metrics for performance monitoring
    
    
    # Setup observability middleware
    ObservabilityMiddleware(app)
    
    # Add server metrics tracking
    track_request_metrics(app)
    
    return app

# Create app instance for imports
app = create_app()

if __name__ == '__main__':
    config = get_config()
    host = getattr(config, 'HOST', '127.0.0.1')
    port = getattr(config, 'PORT', 8000)
    debug = getattr(config, 'DEBUG', False)
    
    # Security: Log configuration summary (without sensitive data)
    logger = create_glpi_logger()
    logger.info(f"Starting Flask app on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Configuration summary: {config.get_config_summary()}")
    
    # Security warning for debug mode in production
    if debug and host != '127.0.0.1':
        logger.warning("DEBUG mode is enabled with non-localhost binding - this is insecure for production!")
    
    app.run(host=host, port=port, debug=debug)