# Sistema de Treinamento e Otimiza��o do AI Context

##  Vis�o Geral

O Sistema de AI Context � uma solu��o avan�ada para alimentar continuamente o contexto da IA com informa��es atualizadas do projeto GLPI Dashboard. O sistema monitora mudan�as no c�digo, extrai padr�es relevantes e mant�m um contexto sem�ntico atualizado atrav�s de MCPs (Model Context Protocols) especializados.

##  Objetivos

- **Contexto Cont�nuo**: Alimenta��o autom�tica da IA com informa��es do projeto
- **MCPs Especializados**: Configura��o de protocolos de contexto espec�ficos
- **Monitoramento Inteligente**: Detec��o autom�tica de mudan�as relevantes
- **An�lise Sem�ntica**: Extra��o de padr�es e depend�ncias do c�digo
- **Otimiza��o Autom�tica**: Limpeza e organiza��o do contexto
- **Integra��o Flex�vel**: Compatibilidade com diferentes ferramentas e workflows

##  Arquitetura

### Componentes Principais

1. **AIContextSystem**: Sistema principal de monitoramento e contexto
2. **MCPs Especializados**: Protocolos para diferentes tipos de contexto
3. **Analisadores de Conte�do**: Extra��o de informa��es espec�ficas por tipo
4. **Sistema de M�tricas**: Monitoramento de performance e uso
5. **Armazenamento Otimizado**: Persist�ncia eficiente do contexto

### Tipos de Contexto Suportados

- **ARCHITECTURE**: Documenta��o de arquitetura e design
- **CODE_PATTERNS**: Padr�es e estruturas de c�digo
- **DEPENDENCIES**: Depend�ncias e imports
- **METRICS**: M�tricas de performance e sistema
- **TROUBLESHOOTING**: Informa��es de debug e solu��o de problemas
- **PERFORMANCE**: Otimiza��es e benchmarks
- **SECURITY**: Configura��es e padr�es de seguran�a
- **TESTING**: Testes e valida��es
- **DOCUMENTATION**: Documenta��o geral
- **CONFIGURATION**: Arquivos de configura��o

##  Como Usar

### 1. Instala��o de Depend�ncias

```bash
pip install aiofiles pyyaml
```

### 2. Configura��o B�sica

```python
from ai_context_system import AIContextSystem

# Inicializar o sistema
system = AIContextSystem("config_ai_context.py")

# Obter resumo do contexto
summary = await system.get_context_summary()
print(summary)
```

### 3. Execu��o do Monitoramento

```bash
# Monitoramento cont�nuo
python ai_context_system.py

# Exemplos pr�ticos
python example_ai_context.py
```

### 4. Exemplo Pr�tico

```python
import asyncio
from ai_context_system import AIContextSystem, ContextType, Priority

async def exemplo_uso():
    system = AIContextSystem()
    
    # Iniciar monitoramento
    await system.start_monitoring()
    
    # O sistema agora monitora automaticamente:
    # - Mudan�as em arquivos
    # - Atualiza��es de MCPs
    # - Gera��o de m�tricas
    # - Otimiza��o de armazenamento

if __name__ == "__main__":
    asyncio.run(exemplo_uso())
```

##  Configura��o

### Ambientes Suportados

- **Development**: Monitoramento detalhado e logs verbosos
- **Staging**: Configura��o intermedi�ria para testes
- **Production**: Configura��o otimizada para performance

### MCPs Configurados

1. **filesystem**: Monitoramento do sistema de arquivos
2. **git**: Integra��o com controle de vers�o
3. **knowledge_graph**: Grafo de conhecimento sem�ntico
4. **code_analysis**: An�lise de padr�es de c�digo
5. **documentation**: Processamento de documenta��o
6. **metrics_collector**: Coleta de m�tricas
7. **api_monitor**: Monitoramento de APIs

### Configura��o de Prioridades

```python
PRIORITY_MAPPING = {
    "ARCHITECTURE.md": "critical",
    "README.md": "high",
    "requirements.txt": "high",
    "docker-compose.yml": "high",
    ".env": "critical"
}
```

### Tags Autom�ticas

O sistema detecta automaticamente tags baseadas em:
- Conte�do do arquivo (async, database, api, testing, etc.)
- Nome do arquivo (model, service, controller, etc.)
- Padr�es de c�digo (imports, classes, fun��es, etc.)

##  M�tricas e Monitoramento

### M�tricas Coletadas

- **context_items**: N�mero total de itens de contexto
- **file_changes**: Frequ�ncia de mudan�as em arquivos
- **mcp_status**: Status dos MCPs configurados
- **storage_usage**: Uso de armazenamento
- **processing_time**: Tempo de processamento

### Localiza��o dos Dados

- **Contexto**: `ai_context_storage/context_items.json`
- **M�tricas**: `ai_context_storage/metrics.json`
- **Logs**: `ai_context.log`
- **Exporta��es**: `exports/`

##  Troubleshooting

### Problemas Comuns

1. **Erro de Permiss�o**
   ```bash
   # Verificar permiss�es do diret�rio
   ls -la ai_context_storage/
   ```

2. **Depend�ncias Ausentes**
   ```bash
   pip install aiofiles pyyaml
   ```

3. **MCPs N�o Funcionando**
   ```python
   # Verificar configura��o
   system = AIContextSystem()
   for name, mcp in system.mcp_configs.items():
       print(f"{name}: {mcp.enabled}")
   ```

### Valida��o do Sistema

```bash
# Executar valida��o completa
python example_ai_context.py

# Verificar apenas troubleshooting
python -c "import asyncio; from example_ai_context import exemplo_troubleshooting; asyncio.run(exemplo_troubleshooting())"
```

### Logs e Debugging

```python
# Configurar n�vel de log
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar logs estruturados
tail -f ai_context.log | jq .
```

##  Integra��o

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

##  Seguran�a

### Controles de Seguran�a

- **Sanitiza��o de Conte�do**: Remo��o autom�tica de dados sens�veis
- **Exclus�o de Segredos**: Detec��o de padr�es de credenciais
- **Hash de Dados Sens�veis**: Prote��o de informa��es cr�ticas
- **Valida��o de Entrada**: Verifica��o de conte�do antes do processamento

### Padr�es de Segredos Detectados

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

### Otimiza��es Implementadas

- **Processamento Ass�ncrono**: Opera��es n�o-bloqueantes
- **Cache Inteligente**: TTL configur�vel para dados frequentes
- **Compress�o**: Redu��o do tamanho de armazenamento
- **Deduplica��o**: Remo��o autom�tica de duplicatas
- **Limpeza Autom�tica**: Remo��o de contexto obsoleto

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

##  Exporta��o

### Formatos Suportados

- **JSON**: Formato estruturado para APIs
- **YAML**: Formato leg�vel para configura��o
- **Markdown**: Formato para documenta��o

### Exporta��o Autom�tica

```python
EXPORT_CONFIG = {
    "formats": ["json", "yaml", "markdown"],
    "include_metadata": True,
    "include_metrics": True,
    "compress_exports": True,
    "auto_export_interval": 86400  # 24 horas
}
```

##  Contribui��o

### Estrutura do C�digo

```
ai_context_system.py     # Sistema principal
config_ai_context.py     # Configura��es
example_ai_context.py    # Exemplos pr�ticos
README_AI_CONTEXT.md    # Esta documenta��o
ai_context_storage/      # Armazenamento de dados
 context_items.json   # Itens de contexto
 metrics.json         # M�tricas do sistema
 exports/            # Exporta��es
```

### Padr�es de C�digo

- **Type Hints**: Tipagem completa em Python
- **Docstrings**: Documenta��o estilo Google
- **Async/Await**: Programa��o ass�ncrona
- **Error Handling**: Tratamento robusto de erros
- **Logging Estruturado**: Logs em formato JSON

### Adicionando Novos MCPs

```python
# Em config_ai_context.py
MCP_CONFIGS.append({
    "name": "novo_mcp",
    "type": "custom",
    "description": "Descri��o do novo MCP",
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

# Implementar an�lise espec�fica
async def _analyze_novo_tipo(self, content: str) -> Dict[str, Any]:
    # L�gica de an�lise espec�fica
    return analysis_result
```

##  Licen�a

Este projeto est� licenciado sob a licen�a MIT. Veja o arquivo LICENSE para detalhes.

##  Suporte

### Canais de Suporte

- **Issues**: Para bugs e solicita��es de recursos
- **Discussions**: Para perguntas e discuss�es gerais
- **Wiki**: Para documenta��o adicional

### Informa��es de Debug

Ao reportar problemas, inclua:

1. **Vers�o do Python**: `python --version`
2. **Depend�ncias**: `pip list`
3. **Logs**: �ltimas linhas de `ai_context.log`
4. **Configura��o**: Configura��es relevantes (sem credenciais)
5. **Contexto**: Passos para reproduzir o problema

### Comandos �teis

```bash
# Verificar status do sistema
python -c "import asyncio; from ai_context_system import AIContextSystem; asyncio.run(AIContextSystem().get_context_summary())"

# Limpar armazenamento
rm -rf ai_context_storage/

# Recriar configura��o padr�o
python -c "from ai_context_system import AIContextSystem; AIContextSystem()._create_default_config()"

# Executar apenas valida��o
python example_ai_context.py
```

---

**Desenvolvido pela equipe GLPI Dashboard** 
