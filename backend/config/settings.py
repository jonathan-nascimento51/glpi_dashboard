"""Configurações centralizadas do projeto com validações robustas"""
import os
import logging
import warnings
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class ConfigValidationError(Exception):
    """Exceção para erros de validação de configuração"""
    pass

class Config:
    """Configuração base com validações robustas"""
    
    def __init__(self):
        """Inicializa e valida as configurações"""
        self._validate_required_configs()
        self._validate_config_values()
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    @property
    def PORT(self) -> int:
        """Porta do servidor com validação"""
        try:
            port = int(os.environ.get('PORT', 5000))
            if not (1 <= port <= 65535):
                raise ValueError(f"Porta inválida: {port}")
            return port
        except ValueError as e:
            raise ConfigValidationError(f"Erro na configuração PORT: {e}")
    
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # GLPI API
    GLPI_URL = os.environ.get('GLPI_URL', 'http://10.73.0.79/glpi/apirest.php')
    GLPI_USER_TOKEN = os.environ.get('GLPI_USER_TOKEN')
    GLPI_APP_TOKEN = os.environ.get('GLPI_APP_TOKEN')
    
    # Backend API
    BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')
    API_KEY = os.environ.get('API_KEY', '')
    
    @property
    def API_TIMEOUT(self) -> int:
        """Timeout da API com validação"""
        try:
            timeout = int(os.environ.get('API_TIMEOUT', '30'))
            if not (1 <= timeout <= 300):
                raise ValueError(f"Timeout deve estar entre 1 e 300 segundos: {timeout}")
            return timeout
        except ValueError as e:
            raise ConfigValidationError(f"Erro na configuração API_TIMEOUT: {e}")
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # CORS
    CORS_ORIGINS = ['*']
    
    # Redis Cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
    
    @property
    def CACHE_REDIS_URL(self) -> str:
        """URL do Redis com fallback"""
        return os.environ.get('CACHE_REDIS_URL', self.REDIS_URL)
    
    @property
    def CACHE_DEFAULT_TIMEOUT(self) -> int:
        """Timeout do cache com validação"""
        try:
            timeout = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
            if not (10 <= timeout <= 3600):
                raise ValueError(f"Cache timeout deve estar entre 10 e 3600 segundos: {timeout}")
            return timeout
        except ValueError as e:
            raise ConfigValidationError(f"Erro na configuração CACHE_DEFAULT_TIMEOUT: {e}")
    
    CACHE_KEY_PREFIX = os.environ.get('CACHE_KEY_PREFIX', 'glpi_dashboard:')
    
    # Performance Settings
    @property
    def PERFORMANCE_TARGET_P95(self) -> int:
        """Target de performance P95 com validação"""
        try:
            target = int(os.environ.get('PERFORMANCE_TARGET_P95', '300'))
            if not (50 <= target <= 10000):
                raise ValueError(f"Performance target deve estar entre 50 e 10000ms: {target}")
            return target
        except ValueError as e:
            raise ConfigValidationError(f"Erro na configuração PERFORMANCE_TARGET_P95: {e}")
    
    # Configurações de segurança
    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Tamanho máximo de conteúdo"""
        return int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    
    @property
    def RATE_LIMIT_PER_MINUTE(self) -> int:
        """Limite de requisições por minuto"""
        return int(os.environ.get('RATE_LIMIT_PER_MINUTE', '100'))
    
    def _validate_required_configs(self) -> None:
        """Valida configurações obrigatórias"""
        required_configs = {
            'GLPI_URL': self.GLPI_URL,
            'GLPI_USER_TOKEN': self.GLPI_USER_TOKEN,
            'GLPI_APP_TOKEN': self.GLPI_APP_TOKEN
        }
        
        missing_configs = [key for key, value in required_configs.items() if not value]
        
        if missing_configs:
            raise ConfigValidationError(
                f"Configurações obrigatórias ausentes: {', '.join(missing_configs)}"
            )
    
    def _validate_config_values(self) -> None:
        """Valida valores das configurações"""
        # Validar URL do GLPI
        if not self.GLPI_URL.startswith(('http://', 'https://')):
            raise ConfigValidationError(f"GLPI_URL deve começar com http:// ou https://: {self.GLPI_URL}")
        
        # Validar nível de log
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            warnings.warn(f"LOG_LEVEL inválido '{self.LOG_LEVEL}', usando 'INFO'")
            self.LOG_LEVEL = 'INFO'
        
        # Validar chave secreta em produção
        if not self.DEBUG and self.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ConfigValidationError(
                "SECRET_KEY deve ser alterada em ambiente de produção"
            )
    
    @classmethod
    def configure_logging(cls) -> logging.Logger:
        """Configura o sistema de logging de forma robusta"""
        try:
            config_instance = cls()
            numeric_level = getattr(logging, config_instance.LOG_LEVEL.upper(), None)
            if not isinstance(numeric_level, int):
                numeric_level = logging.INFO
            
            # Configurar logging básico
            logging.basicConfig(
                level=numeric_level,
                format=config_instance.LOG_FORMAT,
                force=True  # Força reconfiguração
            )
            
            # Configurar loggers específicos
            logger = logging.getLogger('api')
            logger.setLevel(numeric_level)
            
            # Reduzir verbosidade de bibliotecas externas
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('requests').setLevel(logging.WARNING)
            
            return logger
            
        except Exception as e:
            # Fallback para configuração básica
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            logger = logging.getLogger('api')
            logger.warning(f"Erro na configuração de logging: {e}")
            return logger
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Retorna um resumo das configurações (sem dados sensíveis)"""
        return {
            'debug': self.DEBUG,
            'port': self.PORT,
            'host': self.HOST,
            'glpi_url': self.GLPI_URL,
            'log_level': self.LOG_LEVEL,
            'cache_type': self.CACHE_TYPE,
            'cache_timeout': self.CACHE_DEFAULT_TIMEOUT,
            'performance_target': self.PERFORMANCE_TARGET_P95,
            'api_timeout': self.API_TIMEOUT
        }

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
