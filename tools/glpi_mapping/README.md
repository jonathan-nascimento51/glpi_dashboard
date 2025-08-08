# GLPI Mapping Tool

Ferramenta para mapeamento e manutenção de catálogos GLPI. Este módulo permite extrair, mapear e manter atualizados os catálogos e lookups do sistema GLPI.

## 🎯 Funcionalidades

- **Extração de Catálogos**: Extrai dados de diferentes catálogos GLPI (tickets, usuários, grupos, categorias, etc.)
- **Múltiplos Formatos**: Salva dados em JSON e CSV para máxima compatibilidade
- **Detecção de Hierarquia**: Analisa e mapeia estruturas hierárquicas dos catálogos
- **CLI Amigável**: Interface de linha de comando intuitiva com rich output
- **Cache Inteligente**: Sistema de cache para otimizar performance
- **Retry Automático**: Recuperação automática de falhas de rede

## 📦 Instalação

### Como Pacote Pip (Recomendado)

```bash
# No diretório do projeto principal
cd tools/glpi_mapping
pip install -e .
```

### Desenvolvimento

```bash
# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"
```

## ⚙️ Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente:

```bash
# URL base do GLPI
export GLPI_BASE_URL="https://seu-glpi.exemplo.com/apirest.php"
# ou
export GLPI_URL="https://seu-glpi.exemplo.com/apirest.php"

# Tokens de autenticação
export GLPI_APP_TOKEN="seu_app_token_aqui"
export GLPI_USER_TOKEN="seu_user_token_aqui"
```

### Arquivo .env

Alternativamente, crie um arquivo `.env` no diretório raiz do projeto:

```env
GLPI_BASE_URL=https://seu-glpi.exemplo.com/apirest.php
GLPI_APP_TOKEN=seu_app_token_aqui
GLPI_USER_TOKEN=seu_user_token_aqui
```

## 🚀 Uso

### Comandos Básicos

#### Testar Conexão

```bash
# Testar conexão com GLPI
glpi-mapping test-connection

# Com parâmetros específicos
glpi-mapping test-connection --base-url https://glpi.exemplo.com/apirest.php \
                            --app-token TOKEN_APP \
                            --user-token TOKEN_USER
```

#### Listar Catálogos Disponíveis

```bash
glpi-mapping list-catalogs
```

#### Extrair Todos os Catálogos

```bash
# Extração completa (recomendado para produção)
glpi-mapping dump --out ./backend/lookups --detect-levels

# Com limite personalizado
glpi-mapping dump --out ./data/catalogs --limit 2000 --verbose
```

#### Extrair Catálogo Específico

```bash
# Extrair apenas tickets
glpi-mapping dump --catalog tickets --out ./lookups

# Extrair grupos com análise hierárquica
glpi-mapping dump --catalog groups --out ./lookups --detect-levels
```

#### Analisar Estrutura Hierárquica

```bash
# Analisar categorias
glpi-mapping analyze categories

# Analisar grupos com limite
glpi-mapping analyze groups --limit 500
```

### Exemplos Práticos

#### 1. Extração Semanal Automatizada

```bash
#!/bin/bash
# Script para extração semanal

# Carregar variáveis de ambiente
source .env

# Extrair todos os catálogos
glpi-mapping dump \
    --out /data/glpi_lookups \
    --detect-levels \
    --limit 5000 \
    --verbose

# Log do resultado
echo "Extração GLPI concluída em $(date)" >> /var/log/glpi-mapping.log
```

#### 2. Integração com Docker

```dockerfile
# Dockerfile para worker de mapeamento
FROM python:3.11-slim

WORKDIR /app
COPY tools/glpi_mapping/ ./glpi_mapping/
RUN pip install -e ./glpi_mapping/

# Comando padrão
CMD ["glpi-mapping", "dump", "--out", "/data/lookups"]
```

#### 3. Task Celery

```python
# tasks.py
from celery import Celery
import subprocess
import os

app = Celery('glpi_tasks')

@app.task
def update_glpi_catalogs():
    """Task para atualizar catálogos GLPI"""
    try:
        result = subprocess.run([
            'glpi-mapping', 'dump',
            '--out', '/data/lookups',
            '--detect-levels',
            '--verbose'
        ], capture_output=True, text=True, check=True)
        
        return {
            'status': 'success',
            'output': result.stdout,
            'timestamp': datetime.now().isoformat()
        }
    except subprocess.CalledProcessError as e:
        return {
            'status': 'error',
            'error': e.stderr,
            'timestamp': datetime.now().isoformat()
        }
```

## 📊 Catálogos Suportados

| Catálogo | Endpoint GLPI | Descrição |
|----------|---------------|----------|
| `tickets` | Ticket | Tickets/Chamados |
| `users` | User | Usuários do sistema |
| `groups` | Group | Grupos técnicos |
| `categories` | ITILCategory | Categorias ITIL |
| `priorities` | Priority | Prioridades |
| `status` | Status | Status dos tickets |

## 📁 Estrutura de Saída

```
lookups/
├── tickets.json          # Dados dos tickets
├── tickets.csv           # Dados em CSV
├── users.json            # Usuários
├── users.csv
├── groups.json           # Grupos técnicos
├── groups.csv
├── categories.json       # Categorias ITIL
├── categories.csv
├── priorities.json       # Prioridades
├── priorities.csv
├── status.json           # Status
├── status.csv
├── extraction_metadata.json  # Metadados da extração
└── *_hierarchy.json      # Análises hierárquicas (se --detect-levels)
```

### Formato dos Dados

#### JSON
```json
[
  {
    "id": 1,
    "name": "Hardware",
    "level": 1,
    "parent_id": null,
    "category": "categories",
    "status": "active",
    "metadata": {
      "comment": "Categoria para problemas de hardware",
      "is_helpdeskvisible": true
    }
  }
]
```

#### Metadados
```json
{
  "extraction_date": "2024-01-15T10:30:00",
  "glpi_url": "https://glpi.exemplo.com/apirest.php",
  "catalogs": {
    "tickets": 1250,
    "users": 89,
    "groups": 12,
    "categories": 45
  },
  "total_items": 1396
}
```

## 🔧 Integração com Dashboard

### 1. Loader de Lookups

```python
# backend/services/lookup_loader.py
import json
from pathlib import Path
from typing import Dict, Any

class LookupLoader:
    def __init__(self, lookups_dir: Path):
        self.lookups_dir = Path(lookups_dir)
        self._cache = {}
    
    def load_catalog(self, catalog_name: str) -> Dict[str, Any]:
        """Carrega catálogo do arquivo JSON"""
        if catalog_name in self._cache:
            return self._cache[catalog_name]
        
        file_path = self.lookups_dir / f"{catalog_name}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache[catalog_name] = data
                return data
        return []
    
    def get_lookup_dict(self, catalog_name: str) -> Dict[int, str]:
        """Retorna dicionário id -> name para lookups"""
        data = self.load_catalog(catalog_name)
        return {item['id']: item['name'] for item in data}
```

### 2. Endpoint de Reload

```python
# backend/api/routes.py
@api_bp.route('/admin/reload-lookups', methods=['POST'])
def reload_lookups():
    """Recarrega lookups sem redeploy"""
    try:
        # Limpar cache
        lookup_loader._cache.clear()
        
        # Recarregar metadados
        metadata_file = Path('./lookups/extraction_metadata.json')
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            return jsonify({
                'status': 'success',
                'message': 'Lookups recarregados',
                'metadata': metadata
            })
        
        return jsonify({'status': 'success', 'message': 'Cache limpo'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

## 🔄 Automação

### Cron Job

```bash
# Adicionar ao crontab
# Executa toda segunda-feira às 2h
0 2 * * 1 cd /path/to/project && glpi-mapping dump --out ./backend/lookups --detect-levels >> /var/log/glpi-mapping.log 2>&1
```

### Docker Compose Service

```yaml
# docker-compose.yml
services:
  glpi-mapping:
    build:
      context: .
      dockerfile: tools/glpi_mapping/Dockerfile
    environment:
      - GLPI_BASE_URL=${GLPI_BASE_URL}
      - GLPI_APP_TOKEN=${GLPI_APP_TOKEN}
      - GLPI_USER_TOKEN=${GLPI_USER_TOKEN}
    volumes:
      - ./backend/lookups:/data/lookups
    command: >
      sh -c "while true; do
        glpi-mapping dump --out /data/lookups --detect-levels;
        sleep 604800;  # 1 semana
      done"
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=glpi_mapping

# Testes específicos
pytest tests/test_mapper.py -v
```

## 📝 Logs

Os logs são salvos com diferentes níveis:

- **INFO**: Operações normais
- **WARNING**: Problemas não críticos
- **ERROR**: Erros que impedem a operação
- **DEBUG**: Informações detalhadas (use `--verbose`)

## 🔒 Segurança

- **Nunca** commite tokens no código
- Use variáveis de ambiente ou secrets do Docker
- Tokens têm sessão limitada (1 hora)
- Cleanup automático de sessões

## 🚀 Roadmap

- [ ] Suporte a mais catálogos GLPI
- [ ] Integração com S3/MinIO
- [ ] Dashboard web para monitoramento
- [ ] Notificações via webhook
- [ ] Compressão de dados históricos
- [ ] API REST para consulta de catálogos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.