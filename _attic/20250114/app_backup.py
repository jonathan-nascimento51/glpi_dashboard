from flask import Flask, jsonify
from flask_cors import CORS
import logging
import time
from backend.app.core.config import active_config
from backend.app.core.cache_config import configure_cache
from backend.app.api.routes import api_bp

def create_app(config=None):
    """Cria e configura a aplicaçáo Flask com cache inteligente"""
    app = Flask(__name__)
    
    # Carrega configurações
    if config is None:
        app.config.from_object(active_config)
    else:
        app.config.from_object(config)
    
    # Configura cache inteligente com fallback automático
    cache_manager = configure_cache(app)
    
    # Configura CORS
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Configura logging
    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', logging.INFO),
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger = logging.getLogger('app')
    
    # Middleware para logar todas as requisições
    @app.before_request
    def log_request_info():
        from flask import request
        import sys
        print(f"\n=== REQUISIÇáO RECEBIDA ===", flush=True)
        print(f"Método: {request.method}", flush=True)
        print(f"Path: {request.path}", flush=True)
        print(f"URL completa: {request.url}", flush=True)
        print(f"Headers: {dict(request.headers)}", flush=True)
        print(f"================================\n", flush=True)
        sys.stdout.flush()
        logger.info(f"REQUISIÇáO RECEBIDA: {request.method} {request.path}")
        
    @app.after_request
    def log_response_info(response):
        from flask import request
        import sys
        print(f"\n=== RESPOSTA ENVIADA ===", flush=True)
        print(f"Status: {response.status_code}", flush=True)
        print(f"Para: {request.method} {request.path}", flush=True)
        print(f"============================\n", flush=True)
        sys.stdout.flush()
        return response
    
    # Rota raiz
    @app.route('/')
    def index():
        return jsonify({
            'message': 'GLPI Dashboard API',
            'version': '1.0.0',
            'status': 'running',
            'cache_type': cache_manager.cache_type,
            'redis_available': cache_manager.redis_available,
            'endpoints': {
                'metrics': '/api/metrics',
                'health': '/health',
                'cache_info': '/cache/info'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Endpoint de health check com informações detalhadas"""
        try:
            cache_info = cache_manager.get_cache_info()
            
            health_status = {
                'status': 'healthy',
                'timestamp': time.time(),
                'cache': {
                    'type': cache_info['type'],
                    'available': cache_info.get('redis_available', True),
                    'hit_rate': cache_info['metrics']['hit_rate_percent']
                },
                'environment': {
                    'flask_env': app.config.get('FLASK_ENV', 'unknown'),
                    'debug': app.config.get('DEBUG', False)
                }
            }
            
            return jsonify(health_status), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }), 500
    
    # Cache info endpoint
    @app.route('/cache/info')
    def cache_info():
        """Endpoint com informações detalhadas do cache"""
        try:
            info = cache_manager.get_cache_info()
            return jsonify(info), 200
        except Exception as e:
            logger.error(f"Cache info failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Registra blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    logger.info(f"Aplicaçáo configurada com ambiente: {app.config.get('ENV', 'development')}")
    return app

# Cria a aplicaçáo
app = create_app()

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    host = app.config.get('HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', False)
    
    logger = logging.getLogger('app')
    logger.info(f"Iniciando servidor Flask em {host}:{port} (Debug: {debug})")
    
    app.run(host=host, port=port, debug=debug)

