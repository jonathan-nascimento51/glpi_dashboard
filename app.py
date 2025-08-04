from flask import Flask
from flask_cors import CORS
import logging
from backend.config.settings import active_config
from backend.api.routes import api_bp

def create_app(config=None):
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Carrega configurações
    if config is None:
        app.config.from_object(active_config)
    else:
        app.config.from_object(config)
    
    # Configura CORS
    CORS(app)
    
    # Configura logging
    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', logging.INFO),
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger = logging.getLogger('app')
    
    # Registra blueprints
    app.register_blueprint(api_bp)
    
    logger.info(f"Aplicação configurada com ambiente: {app.config.get('ENV', 'development')}")
    return app

# Cria a aplicação
app = create_app()

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    host = app.config.get('HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', False)
    
    logger = logging.getLogger('app')
    logger.info(f"Iniciando servidor Flask em {host}:{port} (Debug: {debug})")
    
    app.run(host=host, port=port, debug=debug)
