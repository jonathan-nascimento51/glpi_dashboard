#!/usr/bin/env python3
"""
Ponto de entrada principal do backend GLPI Dashboard
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from backend.app.core.config import active_config

def main():
    """Funçáo principal para inicializar a aplicaçáo"""
    app = create_app()
    
    # Configurações do servidor
    host = active_config.HOST
    port = active_config.PORT
    debug = active_config.DEBUG
    
    print(f"Iniciando servidor em {host}:{port} (debug={debug})")
    
    # Inicia o servidor Flask
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
