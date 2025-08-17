#!/usr/bin/env python3
"""
Arquivo de aplicação Flask para testes
"""

import sys
import os

# Adiciona o diretório raiz do projeto ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importa a função create_app do arquivo app.py na raiz
from app import create_app
from backend.config.settings import active_config

# Cria a aplicação
app = create_app(active_config)

if __name__ == '__main__':
    app.run(debug=True)