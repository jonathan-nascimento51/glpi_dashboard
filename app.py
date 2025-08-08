from flask import Flask
from flask_cors import CORS
import logging
from backend.config.settings import active_config
from backend.config.cache import init_cache
from backend.api.routes import api_bp

def create_app(config=None):
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração
    if config:
        app.config.update(config)
    else:
        app.config.update(active_config.to_dict())
    
    # CORS
    CORS(app, origins=["http://localhost:3001", "http://127.0.0.1:3001"])
    
    # Inicializa cache usando o módulo separado
    init_cache(app)
    
    # Configura logging
    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', logging.INFO),
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger = logging.getLogger('app')
    
    # Middleware para logar requisições (simplificado)
    @app.before_request
    def log_request_info():
        from flask import request
        logger.info(f"REQUISIÇÃO: {request.method} {request.path}")
        
    @app.after_request
    def log_response_info(response):
        from flask import request
        logger.info(f"RESPOSTA: {response.status_code} para {request.method} {request.path}")
        return response
    
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
