#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação Flask GLPI Dashboard
"""

import sys
import os
import importlib.util

# Adiciona o diretório pai ao path para importar módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
# Adiciona também o diretório raiz do contêiner para importações
sys.path.insert(0, '/')

# Importa diretamente do arquivo app.py na raiz do projeto
import os
app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
print(f"Tentando carregar app de: {app_path}")
spec = importlib.util.spec_from_file_location("main_app", app_path)
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

from backend.config.settings import active_config

# Cria a aplicação
app = main_app.create_app(active_config)

if __name__ == '__main__':
    # Executa o servidor Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=active_config.DEBUG
    )