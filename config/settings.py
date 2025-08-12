import os
from typing import Dict, Any

class Config:
    """Configuração base da aplicação."""
    
    # Configurações do Flask/Dash
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '8050'))
    
    # Configurações da API GLPI
    GLPI_URL = os.getenv('GLPI_URL', 'http://localhost/glpi')
    GLPI_USER_TOKEN = os.getenv('GLPI_USER_TOKEN', '')
    GLPI_APP_TOKEN = os.getenv('GLPI_APP_TOKEN', '')
    
    # Configurações do Backend API
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
    BACKEND_API_KEY = os.getenv('BACKEND_API_KEY', '')
    BACKEND_TIMEOUT = int(os.getenv('BACKEND_TIMEOUT', '30'))
    
    # Configurações de Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Retorna todas as configurações como dicionário."""
        return {
            'debug': cls.DEBUG,
            'secret_key': cls.SECRET_KEY,
            'host': cls.HOST,
            'port': cls.PORT,
            'glpi_url': cls.GLPI_URL,
            'glpi_user_token': cls.GLPI_USER_TOKEN,
            'glpi_app_token': cls.GLPI_APP_TOKEN,
            'backend_url': cls.BACKEND_URL,
            'backend_api_key': cls.BACKEND_API_KEY,
            'backend_timeout': cls.BACKEND_TIMEOUT,
            'log_level': cls.LOG_LEVEL,
        }

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True

class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False

class TestingConfig(Config):
    """Configuração para testes."""
    DEBUG = True
    TESTING = True

# Configuração ativa baseada no ambiente
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

env = os.getenv('FLASK_ENV', 'development')
active_config = config_map.get(env, config_map['default'])
