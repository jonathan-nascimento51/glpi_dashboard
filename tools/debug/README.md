# Scripts de Debug e Diagnóstico - GLPI Dashboard

Esta pasta contém scripts organizados para debug e diagnóstico do sistema GLPI Dashboard. Os scripts são úteis para identificar problemas, validar funcionalidades e monitorar a saúde do sistema.

## 📁 Estrutura de Pastas

```
tools/debug/
├── api/                    # Scripts para testar API endpoints
├── database/              # Scripts para testar banco de dados
├── frontend/              # Scripts para testar componentes frontend
├── glpi/                  # Scripts para testar integração GLPI
├── ranking/               # Scripts específicos para ranking
├── run_all_tests.py       # Script principal que executa todos os testes
└── README.md              # Esta documentação
```

## 🚀 Script Principal

### `run_all_tests.py`

Script principal que orquestra todos os testes de debug.

**Uso:**
```bash
# Executa todos os testes
python tools/debug/run_all_tests.py

# Executa apenas testes rápidos
python tools/debug/run_all_tests.py --quick

# Executa apenas uma categoria específica
python tools/debug/run_all_tests.py --category api
python tools/debug/run_all_tests.py --category frontend

# Gera relatório JSON
python tools/debug/run_all_tests.py --report debug_report.json

# Saída verbosa
python tools/debug/run_all_tests.py --verbose
```

**Categorias disponíveis:**
- `api`: Testa endpoints da API
- `glpi`: Testa conexão com GLPI
- `database`: Testa queries do banco
- `frontend`: Testa componentes React
- `ranking`: Testa funcionalidades específicas do ranking

## 🌐 Scripts de API

### `api/test_api_endpoints.py`

Testa todos os endpoints da API do backend.

**Funcionalidades:**
- ✅ Testa endpoints básicos (`/api/health`, `/api/dashboard/metrics`, etc.)
- ✅ Testa ranking com diferentes filtros
- ✅ Verifica headers CORS
- ✅ Valida respostas JSON

**Uso:**
```bash
# Testa API local
python api/test_api_endpoints.py

# Testa API em outro host/porta
python api/test_api_endpoints.py --host 192.168.1.100 --port 8000

# Saída verbosa
python api/test_api_endpoints.py --verbose
```

**Exemplo de saída:**
```
🔍 Testando: Health Check
URL: http://localhost:5000/api/health
Status: 200
✅ Sucesso

🔍 Testando: Technician Ranking
URL: http://localhost:5000/api/technicians/ranking
Status: 200
✅ Sucesso
```

## 🔌 Scripts de GLPI

### `glpi/test_glpi_connection.py`

Testa conectividade e autenticação com o sistema GLPI.

**Funcionalidades:**
- ✅ Testa conexão básica com GLPI
- ✅ Valida autenticação (app_token e user_token)
- ✅ Testa busca de tickets
- ✅ Testa busca de usuários/técnicos
- ✅ Gerencia sessões adequadamente

**Uso:**
```bash
# Usa configuração padrão
python glpi/test_glpi_connection.py

# Usa arquivo de configuração específico
python glpi/test_glpi_connection.py --config custom_config.json
```

**Configuração esperada:**
```json
{
  "glpi": {
    "url": "http://localhost/glpi",
    "app_token": "your_app_token",
    "user_token": "your_user_token"
  }
}
```

## 🗄️ Scripts de Banco de Dados

### `database/test_database_queries.py`

Testa queries e integridade do banco de dados SQLite.

**Funcionalidades:**
- ✅ Verifica estrutura das tabelas
- ✅ Testa contagens básicas de dados
- ✅ Executa query de ranking completa
- ✅ Testa filtros de data e nível
- ✅ Verifica integridade referencial

**Uso:**
```bash
# Usa banco padrão
python database/test_database_queries.py

# Usa configuração específica
python database/test_database_queries.py --config db_config.json
```

**Exemplo de saída:**
```
🏗️  Testando estrutura das tabelas...
Tabelas encontradas: 3
  📋 technicians
  📋 tickets
  📋 ticket_assignments

📊 Estrutura da tabela 'technicians':
  - id (INTEGER)
  - name (TEXT)
  - level (TEXT)
```

## 🎨 Scripts de Frontend

### `frontend/test_frontend_components.js`

Testa componentes React e estrutura do frontend.

**Funcionalidades:**
- ✅ Verifica existência de componentes críticos
- ✅ Analisa estrutura de hooks
- ✅ Valida serviços de API
- ✅ Testa processo de build
- ✅ Verifica tipos TypeScript
- ✅ Analisa package.json

**Uso:**
```bash
# Testa todos os componentes
node frontend/test_frontend_components.js

# Testa componente específico
node frontend/test_frontend_components.js --component RankingTable
```

**Exemplo de saída:**
```
🏗️  Testando estrutura de componentes...
✅ Componente dashboard/ModernDashboard.tsx: Encontrado
  📊 dashboard/ModernDashboard.tsx: 245 linhas, 8 imports, 1 exports

🎣 Testando hooks...
✅ Hook useDashboard.ts: Encontrado
  📊 useDashboard.ts: 156 linhas, 12 hooks React
```

## 🏆 Scripts de Ranking

Esta pasta contém scripts específicos para debug do sistema de ranking de técnicos. Os scripts são movidos automaticamente do diretório `backend/` quando criados durante o desenvolvimento.

**Scripts típicos:**
- `debug_ranking_*.py`: Scripts para debug específico do ranking
- `debug_glpi_*.py`: Scripts para debug da integração GLPI

## 📊 Relatórios

O script principal pode gerar relatórios em formato JSON com informações detalhadas:

```json
{
  "timestamp": "2024-01-19T10:55:00.000Z",
  "summary": {
    "total_categories": 5,
    "passed_categories": 4,
    "failed_categories": 1
  },
  "details": {
    "api_endpoints": true,
    "glpi_connection": false,
    "database_queries": true,
    "frontend_components": true,
    "ranking_specific": true
  },
  "recommendations": [
    "Verificar configuração de conexão com GLPI"
  ]
}
```

## 🔧 Requisitos

### Python Scripts
- Python 3.7+
- Bibliotecas: `requests`, `sqlite3`, `json`, `pathlib`

### JavaScript Scripts
- Node.js 14+
- npm ou yarn
- Dependências do projeto frontend

## 🚨 Solução de Problemas

### Problemas Comuns

1. **Script não encontrado**
   ```bash
   # Certifique-se de estar no diretório correto
   cd tools/debug
   python run_all_tests.py
   ```

2. **Erro de conexão com API**
   ```bash
   # Verifique se o backend está rodando
   curl http://localhost:5000/api/health
   ```

3. **Erro de banco de dados**
   ```bash
   # Verifique se o arquivo existe
   ls -la backend/glpi_dashboard.db
   ```

4. **Erro no frontend**
   ```bash
   # Instale dependências
   cd frontend
   npm install
   ```

### Logs e Debug

Todos os scripts incluem logs detalhados com timestamps e ícones para facilitar a identificação de problemas:

- 🔍 Informação
- ✅ Sucesso
- ❌ Erro
- ⚠️ Aviso
- 🐛 Debug

## 📝 Contribuindo

Ao adicionar novos scripts de debug:

1. **Coloque na pasta apropriada** (`api/`, `database/`, `frontend/`, `glpi/`, `ranking/`)
2. **Inclua documentação** no cabeçalho do script
3. **Use logging consistente** com ícones e timestamps
4. **Adicione tratamento de erros** adequado
5. **Teste o script** antes de commitar
6. **Atualize este README** se necessário

### Exemplo de Script

```python
#!/usr/bin/env python3
"""
Descrição do script
Uso: python script.py [--option VALUE]
"""

import argparse
from datetime import datetime

def log(message, level='INFO'):
    """Log com timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    icons = {'INFO': '🔍', 'SUCCESS': '✅', 'ERROR': '❌'}
    icon = icons.get(level, 'ℹ️')
    print(f"{icon} [{timestamp}] {message}")

def main():
    parser = argparse.ArgumentParser(description='Descrição')
    # Adicione argumentos aqui
    args = parser.parse_args()
    
    log("Iniciando script", 'INFO')
    # Lógica do script aqui
    log("Script concluído", 'SUCCESS')

if __name__ == "__main__":
    main()
```

## 📞 Suporte

Para problemas com os scripts de debug:

1. Verifique os logs detalhados
2. Execute com `--verbose` para mais informações
3. Teste componentes individuais
4. Consulte a documentação do projeto principal

---

**Última atualização:** 19/01/2025
**Versão:** 1.0.0