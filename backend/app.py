from flask import Flask
from flask_cors import CORS
from api.routes import api_bp
from api.demo_routes import demo_bp
from api.server_metrics import metrics_bp, track_request_metrics
from cache_test_routes import cache_test_bp
from config.settings import Config
from utils.structured_logger import create_glpi_logger
from utils.observability_middleware import ObservabilityMiddleware

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, origins="*")
    
    # Setup structured logging
    logger = create_glpi_logger()
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(demo_bp)  # Demo routes for benchmarking
    app.register_blueprint(metrics_bp)  # Server metrics for performance monitoring
    app.register_blueprint(cache_test_bp)  # Cache testing endpoints
    
    # Setup observability middleware
    ObservabilityMiddleware(app)
    
    # Add server metrics tracking
    track_request_metrics(app)
    
    return app

# Create app instance for imports
app = create_app()

if __name__ == '__main__':
    config = Config()
    host = getattr(config, 'HOST', '127.0.0.1')
    port = getattr(config, 'PORT', 8000)
    debug = getattr(config, 'FLASK_DEBUG', False)
    
    print(f"Starting Flask app on {host}:{port}")
    app.run(host=host, port=port, debug=debug)