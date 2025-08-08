from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
import logging
import redis
from backend.config.settings import active_config
from backend.api.routes import api_bp
from backend.routes.maintenance_routes import register_maintenance_routes

# Instância global do cache
cache = Cache()

def create_app(config=None):
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Carrega configurações
    if config is None:
        app.config.from_object(active_config)
    else:
        app.config.from_object(config)
    
    # Configura cache com Redis e fallback
    try:
        # Tenta conectar ao Redis
        redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379/0'))
        redis_client.ping()  # Testa conexão
        
        cache_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'CACHE_KEY_PREFIX': app.config.get('CACHE_KEY_PREFIX', 'glpi_dashboard:')
        }
        print("✓ Redis cache configurado com sucesso")
        
    except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
        # Fallback para SimpleCache se Redis não estiver disponível
        print(f"⚠ Redis não disponível ({e}), usando SimpleCache como fallback")
        cache_config = {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        }
    
    app.config.update(cache_config)
    cache.init_app(app)
    
    # Configura CORS
    CORS(app)
    
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
        print(f"\n=== REQUISIÇÃO RECEBIDA ===", flush=True)
        print(f"Método: {request.method}", flush=True)
        print(f"Path: {request.path}", flush=True)
        print(f"URL completa: {request.url}", flush=True)
        print(f"Headers: {dict(request.headers)}", flush=True)
        print(f"================================\n", flush=True)
        sys.stdout.flush()
        logger.info(f"REQUISIÇÃO RECEBIDA: {request.method} {request.path}")
        
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
    
    # Registra blueprints
    app.register_blueprint(api_bp)
    
    # Registra rotas de manutenção
    register_maintenance_routes(app)
    
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
