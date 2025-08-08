#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper CLI para iniciar o backend do GLPI Dashboard
Usa o application factory pattern do app.py
"""

import os
import sys
import logging

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Configura logging básico (sem excessos)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Desabilita logs excessivos
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

def create_simple_app():
    """Wrapper para criar aplicação usando o factory pattern"""
    # Configuração simplificada para desenvolvimento
    config = {
        'DEBUG': False,
        'CACHE_TYPE': 'SimpleCache',  # Força SimpleCache para evitar problemas
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    
    return create_app(config)

if __name__ == '__main__':
    print("Iniciando backend GLPI Dashboard (modo simplificado)...")
    
    app = create_simple_app()
    
    # Configurações do servidor
    host = '127.0.0.1'  # Localhost apenas
    port = 5000
    
    print(f"Servidor iniciando em http://{host}:{port}")
    print("Pressione Ctrl+C para parar")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=False,  # Sem debug
            use_reloader=False,  # Sem reloader automático
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)