"""Configurações centralizadas do projeto"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configuração base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # GLPI API
    GLPI_URL = os.environ.get('GLPI_URL', 'http://10.73.0.79/glpi/apirest.php')
    GLPI_USER_TOKEN = os.environ.get('GLPI_USER_TOKEN')
    GLPI_APP_TOKEN = os.environ.get('GLPI_APP_TOKEN')
    
    # Backend API
    BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')
    API_KEY = os.environ.get('API_KEY', '')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # CORS
    CORS_ORIGINS = ['*']
    
    # Redis Cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))  # 5 minutos
    CACHE_KEY_PREFIX = os.environ.get('CACHE_KEY_PREFIX', 'glpi_dashboard:')
    
    # Performance Settings
    PERFORMANCE_TARGET_P95 = int(os.environ.get('PERFORMANCE_TARGET_P95', '300'))  # 300ms target
    
    @classmethod
    def configure_logging(cls):
        """Configura o sistema de logging"""
        numeric_level = getattr(logging, cls.LOG_LEVEL.upper(), None)
        if not isinstance(numeric_level, int):
            numeric_level = logging.INFO
        
        logging.basicConfig(
            level=numeric_level,
            format=cls.LOG_FORMAT
        )
        
        return logging.getLogger('api')

# Configuração de desenvolvimento
class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True

# Configuração de produção
class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False
    CORS_ORIGINS = ['https://dashboard.example.com']

# Configuração de teste
class TestingConfig(Config):
    """Configuração para ambiente de teste"""
    DEBUG = True
    TESTING = True

# Dicionário de configurações
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}

# Configuração ativa
active_config = config_by_name[os.environ.get('FLASK_ENV', 'dev')]
