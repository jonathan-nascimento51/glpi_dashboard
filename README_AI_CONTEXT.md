# Sistema de Treinamento e Otimização do AI Context

##  Visão Geral

O Sistema de AI Context é uma solução avançada para alimentar continuamente o contexto da IA com informações atualizadas do projeto GLPI Dashboard. O sistema monitora mudanças no código, extrai padrões relevantes e mantém um contexto semântico atualizado através de MCPs (Model Context Protocols) especializados.

##  Objetivos

- **Contexto Contínuo**: Alimentação automática da IA com informações do projeto
- **MCPs Especializados**: Configuração de protocolos de contexto específicos
- **Monitoramento Inteligente**: Detecção automática de mudanças relevantes
- **Análise Semântica**: Extração de padrões e dependências do código
- **Otimização Automática**: Limpeza e organização do contexto
- **Integração Flexível**: Compatibilidade com diferentes ferramentas e workflows

##  Arquitetura

### Componentes Principais

1. **AIContextSystem**: Sistema principal de monitoramento e contexto
2. **MCPs Especializados**: Protocolos para diferentes tipos de contexto
3. **Analisadores de Conteúdo**: Extração de informações específicas por tipo
4. **Sistema de Métricas**: Monitoramento de performance e uso
5. **Armazenamento Otimizado**: Persistência eficiente do contexto

### Tipos de Contexto Suportados

- **ARCHITECTURE**: Documentação de arquitetura e design
- **CODE_PATTERNS**: Padrões e estruturas de código
- **DEPENDENCIES**: Dependências e imports
- **METRICS**: Métricas de performance e sistema
- **TROUBLESHOOTING**: Informações de debug e solução de problemas
- **PERFORMANCE**: Otimizações e benchmarks
- **SECURITY**: Configurações e padrões de segurança
- **TESTING**: Testes e validações
- **DOCUMENTATION**: Documentação geral
- **CONFIGURATION**: Arquivos de configuração

##  Como Usar

### 1. Instalação de Dependências

```bash
pip install aiofiles pyyaml
```

### 2. Configuração Básica

```python
from ai_context_system import AIContextSystem

# Inicializar o sistema
system = AIContextSystem("config_ai_context.py")

# Obter resumo do contexto
summary = await system.get_context_summary()
print(summary)
```

### 3. Execução do Monitoramento

```bash
# Monitoramento contínuo
python ai_context_system.py

# Exemplos práticos
python example_ai_context.py
```

### 4. Exemplo Prático

```python
import asyncio
from ai_context_system import AIContextSystem, ContextType, Priority

async def exemplo_uso():
    system = AIContextSystem()
    
    # Iniciar monitoramento
    await system.start_monitoring()
    
    # O sistema agora monitora automaticamente:
    # - Mudanças em arquivos
    # - Atualizações de MCPs
    # - Geração de métricas
    # - Otimização de armazenamento

if __name__ == "__main__":
    asyncio.run(exemplo_uso())
```

##  Configuração

### Ambientes Suportados

- **Development**: Monitoramento detalhado e logs verbosos
- **Staging**: Configuração intermediária para testes
- **Production**: Configuração otimizada para performance

### MCPs Configurados

1. **filesystem**: Monitoramento do sistema de arquivos
2. **git**: Integração com controle de versão
3. **knowledge_graph**: Grafo de conhecimento semântico
4. **code_analysis**: Análise de padrões de código
5. **documentation**: Processamento de documentação
6. **metrics_collector**: Coleta de métricas
7. **api_monitor**: Monitoramento de APIs

### Configuração de Prioridades

```python
PRIORITY_MAPPING = {
    "ARCHITECTURE.md": "critical",
    "README.md": "high",
    "requirements.txt": "high",
    "docker-compose.yml": "high",
    ".env": "critical"
}
```

### Tags Automáticas

O sistema detecta automaticamente tags baseadas em:
- Conteúdo do arquivo (async, database, api, testing, etc.)
- Nome do arquivo (model, service, controller, etc.)
- Padrões de código (imports, classes, funções, etc.)

##  Métricas e Monitoramento

### Métricas Coletadas

- **context_items**: Número total de itens de contexto
- **file_changes**: Frequência de mudanças em arquivos
- **mcp_status**: Status dos MCPs configurados
- **storage_usage**: Uso de armazenamento
- **processing_time**: Tempo de processamento

### Localização dos Dados

- **Contexto**: `ai_context_storage/context_items.json`
- **Métricas**: `ai_context_storage/metrics.json`
- **Logs**: `ai_context.log`
- **Exportações**: `exports/`

##  Troubleshooting

### Problemas Comuns

1. **Erro de Permissão**
   ```bash
   # Verificar permissões do diretório
   ls -la ai_context_storage/
   ```

2. **Dependências Ausentes**
   ```bash
   pip install aiofiles pyyaml
   ```

3. **MCPs Não Funcionando**
   ```python
   # Verificar configuração
   system = AIContextSystem()
   for name, mcp in system.mcp_configs.items():
       print(f"{name}: {mcp.enabled}")
   ```

### Validação do Sistema

```bash
# Executar validação completa
python example_ai_context.py

# Verificar apenas troubleshooting
python -c "import asyncio; from example_ai_context import exemplo_troubleshooting; asyncio.run(exemplo_troubleshooting())"
```

### Logs e Debugging

```python
# Configurar nível de log
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar logs estruturados
tail -f ai_context.log | jq .
```

##  Integração

### Knowledge Graph

```python
KNOWLEDGE_GRAPH_CONFIG = {
    "enabled": True,
    "endpoint": "http://localhost:8001/knowledge",
    "auto_sync": True,
    "sync_interval": 3600
}
```

### Git Integration

```python
GIT_CONFIG = {
    "enabled": True,
    "track_commits": True,
    "track_branches": True,
    "max_commit_history": 1000
}
```

### Prometheus/Grafana

```python
PROMETHEUS_CONFIG = {
    "enabled": False,
    "endpoint": "http://localhost:9090",
    "metrics_prefix": "ai_context_"
}
```

##  Segurança

### Controles de Segurança

- **Sanitização de Conteúdo**: Remoção automática de dados sensíveis
- **Exclusão de Segredos**: Detecção de padrões de credenciais
- **Hash de Dados Sensíveis**: Proteção de informações críticas
- **Validação de Entrada**: Verificação de conteúdo antes do processamento

### Padrões de Segredos Detectados

```python
SECRET_PATTERNS = [
    r"password\s*=\s*['\"][^'\"]+['\"]",
    r"token\s*=\s*['\"][^'\"]+['\"]",
    r"key\s*=\s*['\"][^'\"]+['\"]",
    r"secret\s*=\s*['\"][^'\"]+['\"]",
    r"api_key\s*=\s*['\"][^'\"]+['\"]"
]
```

##  Performance

### Otimizações Implementadas

- **Processamento Assíncrono**: Operações não-bloqueantes
- **Cache Inteligente**: TTL configurável para dados frequentes
- **Compressão**: Redução do tamanho de armazenamento
- **Deduplicação**: Remoção automática de duplicatas
- **Limpeza Automática**: Remoção de contexto obsoleto

### Limites Recomendados

```python
PERFORMANCE_CONFIG = {
    "max_concurrent_files": 10,
    "max_file_size": 1024 * 1024,  # 1MB
    "batch_size": 50,
    "cache_ttl": 3600,  # 1 hora
    "max_items": 10000,
    "max_storage_size": 100 * 1024 * 1024  # 100MB
}
```

##  Exportação

### Formatos Suportados

- **JSON**: Formato estruturado para APIs
- **YAML**: Formato legível para configuração
- **Markdown**: Formato para documentação

### Exportação Automática

```python
EXPORT_CONFIG = {
    "formats": ["json", "yaml", "markdown"],
    "include_metadata": True,
    "include_metrics": True,
    "compress_exports": True,
    "auto_export_interval": 86400  # 24 horas
}
```

##  Contribuição

### Estrutura do Código

```
ai_context_system.py     # Sistema principal
config_ai_context.py     # Configurações
example_ai_context.py    # Exemplos práticos
README_AI_CONTEXT.md    # Esta documentação
ai_context_storage/      # Armazenamento de dados
 context_items.json   # Itens de contexto
 metrics.json         # Métricas do sistema
 exports/            # Exportações
```

### Padrões de Código

- **Type Hints**: Tipagem completa em Python
- **Docstrings**: Documentação estilo Google
- **Async/Await**: Programação assíncrona
- **Error Handling**: Tratamento robusto de erros
- **Logging Estruturado**: Logs em formato JSON

### Adicionando Novos MCPs

```python
# Em config_ai_context.py
MCP_CONFIGS.append({
    "name": "novo_mcp",
    "type": "custom",
    "description": "Descrição do novo MCP",
    "config_path": "mcp/novo_mcp.json",
    "enabled": True,
    "auto_update": True,
    "update_interval": 3600,
    "dependencies": ["filesystem"]
})
```

### Adicionando Novos Tipos de Contexto

```python
# Em ai_context_system.py
class ContextType(Enum):
    # ... tipos existentes ...
    NOVO_TIPO = "novo_tipo"

# Implementar análise específica
async def _analyze_novo_tipo(self, content: str) -> Dict[str, Any]:
    # Lógica de análise específica
    return analysis_result
```

##  Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para detalhes.

##  Suporte

### Canais de Suporte

- **Issues**: Para bugs e solicitações de recursos
- **Discussions**: Para perguntas e discussões gerais
- **Wiki**: Para documentação adicional

### Informações de Debug

Ao reportar problemas, inclua:

1. **Versão do Python**: `python --version`
2. **Dependências**: `pip list`
3. **Logs**: Últimas linhas de `ai_context.log`
4. **Configuração**: Configurações relevantes (sem credenciais)
5. **Contexto**: Passos para reproduzir o problema

### Comandos Úteis

```bash
# Verificar status do sistema
python -c "import asyncio; from ai_context_system import AIContextSystem; asyncio.run(AIContextSystem().get_context_summary())"

# Limpar armazenamento
rm -rf ai_context_storage/

# Recriar configuração padrão
python -c "from ai_context_system import AIContextSystem; AIContextSystem()._create_default_config()"

# Executar apenas validação
python example_ai_context.py
```

---

**Desenvolvido pela equipe GLPI Dashboard** 
