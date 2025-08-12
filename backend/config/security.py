"""Configurações de segurança para o GLPI Dashboard."""

import os
from typing import Dict, Optional


class SecurityConfig:
    """Configurações centralizadas de segurança."""

    @staticmethod
    def get_cors_origins() -> list[str]:
        """Retorna as origens permitidas para CORS."""
        origins_str = os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:8050"
        )
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    @staticmethod
    def is_security_headers_enabled() -> bool:
        """Verifica se os headers de segurança estão habilitados."""
        return os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"

    @staticmethod
    def get_csp_config() -> Dict[str, str]:
        """Retorna a configuração do Content Security Policy."""
        return {
            "default_src": os.getenv("CSP_DEFAULT_SRC", "'self'"),
            "script_src": os.getenv("CSP_SCRIPT_SRC", "'self' 'unsafe-inline'"),
            "style_src": os.getenv("CSP_STYLE_SRC", "'self' 'unsafe-inline'"),
            "img_src": os.getenv("CSP_IMG_SRC", "'self' data: https:"),
            "connect_src": os.getenv("CSP_CONNECT_SRC", "'self'"),
        }

    @staticmethod
    def get_secret_key() -> str:
        """Retorna a chave secreta para JWT."""
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise ValueError(
                "SECRET_KEY não configurada. "
                "Configure a variável de ambiente SECRET_KEY com uma chave forte."
            )
        return secret_key

    @staticmethod
    def get_encryption_key() -> Optional[str]:
        """Retorna a chave de criptografia se configurada."""
        return os.getenv("ENCRYPTION_KEY")

    @staticmethod
    def is_development() -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"

    @staticmethod
    def get_allowed_hosts() -> list[str]:
        """Retorna os hosts permitidos."""
        hosts_str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        return [host.strip() for host in hosts_str.split(",") if host.strip()]
