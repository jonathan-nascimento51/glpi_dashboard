# 🧪 Sandbox de Testes para IA - GLPI Dashboard

## 🎯 Objetivo

O sandbox fornece um ambiente seguro e isolado para testar integrações de IA, prompts automáticos e funcionalidades experimentais sem afetar o ambiente de produção.

## 🏗️ Estrutura do Sandbox

```
docs/ai/sandbox/
├── README.md                 # Este arquivo
├── test-prompts/            # Prompts para teste
│   ├── feature-development.md
│   ├── bug-analysis.md
│   └── code-review.md
├── mock-data/               # Dados simulados
│   ├── glpi-responses/
│   ├── api-contracts/
│   └── test-scenarios/
├── experiments/             # Experimentos de IA
│   ├── prompt-optimization/
│   ├── code-generation/
│   └── documentation-auto/
└── results/                 # Resultados dos testes
    ├── performance/
    ├── accuracy/
    └── reports/
```

## 🚀 Como Usar o Sandbox

### 1. Configuração Inicial

```bash
# Navegar para o diretório do projeto
cd glpi_dashboard

# Criar ambiente virtual para sandbox (opcional)
python -m venv sandbox-env
source sandbox-env/bin/activate  # Linux/Mac
# ou
sandbox-env\Scripts\activate     # Windows

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt
```

### 2. Executar Testes de Prompt

```bash
# Testar prompts de desenvolvimento
python docs/ai/sandbox/scripts/test_prompts.py --category development

# Testar prompts de debug
python docs/ai/sandbox/scripts/test_prompts.py --category debug

# Executar todos os testes
python docs/ai/sandbox/scripts/run_all_tests.py
```

### 3. Simular Integrações

```bash
# Simular chamadas GLPI com dados mock
python docs/ai/sandbox/scripts/simulate_glpi.py

# Testar geração automática de código
python docs/ai/sandbox/scripts/test_code_generation.py

# Validar documentação automática
python docs/ai/sandbox/scripts/test_auto_docs.py
```

## 🧪 Tipos de Teste Disponíveis

### 1. Testes de Prompt

**Objetivo**: Validar eficácia dos prompts contextuais

**Métricas**:
- Precisão das respostas
- Tempo de resposta
- Qualidade do código gerado
- Aderência aos padrões do projeto

**Exemplo**:
```python
# docs/ai/sandbox/scripts/test_prompts.py
import json
from typing import Dict, List

class PromptTester:
    def test_development_prompt(self, scenario: str) -> Dict:
        """Testa prompt de desenvolvimento com cenário específico"""
        prompt = self.load_prompt('development', scenario)
        response = self.simulate_ai_response(prompt)
        
        return {
            'accuracy': self.measure_accuracy(response),
            'completeness': self.check_completeness(response),
            'code_quality': self.analyze_code_quality(response),
            'adherence': self.check_standards_adherence(response)
        }
```

### 2. Simulação de Dados

**Objetivo**: Testar com dados realistas sem afetar sistemas reais

**Dados Disponíveis**:
- Respostas GLPI simuladas
- Cenários de erro
- Dados de performance
- Casos extremos

**Exemplo**:
```json
// docs/ai/sandbox/mock-data/glpi-responses/tickets.json
{
  "data": [
    {
      "id": "12345",
      "name": "Problema de rede",
      "status": "2",
      "priority": "3",
      "date_creation": "2024-01-15 10:30:00",
      "date_mod": "2024-01-15 14:20:00"
    }
  ],
  "totalcount": 150,
  "count": 50
}
```

### 3. Testes de Performance

**Objetivo**: Medir impacto da IA na performance do sistema

**Métricas**:
- Tempo de processamento
- Uso de memória
- Throughput
- Latência

**Exemplo**:
```python
# docs/ai/sandbox/scripts/performance_test.py
import time
import psutil
from typing import Dict

class PerformanceTester:
    def measure_ai_impact(self, operation: str) -> Dict:
        """Mede impacto da IA em operações específicas"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        # Executar operação com IA
        result = self.execute_with_ai(operation)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        return {
            'execution_time': end_time - start_time,
            'memory_usage': end_memory - start_memory,
            'result_quality': self.assess_quality(result)
        }
```

## 📊 Cenários de Teste

### Cenário 1: Desenvolvimento de Nova Feature

**Descrição**: Simular desenvolvimento de endpoint para relatórios

**Entrada**:
```markdown
Criar endpoint /api/reports/summary que retorna:
- Total de tickets por status
- Tempo médio de resolução
- Top 5 categorias mais frequentes
- Dados dos últimos 30 dias
```

**Saída Esperada**:
- Código Python funcional
- Testes unitários
- Documentação da API
- Integração com frontend

**Validação**:
- Código executa sem erros
- Testes passam
- Segue padrões do projeto
- Performance adequada

### Cenário 2: Debug de Issue

**Descrição**: Diagnosticar problema de performance

**Entrada**:
```markdown
API /api/metrics está lenta (>2s resposta)
Logs mostram:
- Múltiplas chamadas GLPI
- Cache miss frequente
- Timeout ocasional
```

**Saída Esperada**:
- Análise das causas
- Plano de correção
- Código otimizado
- Testes de regressão

### Cenário 3: Refatoração de Código

**Descrição**: Melhorar estrutura do GLPIService

**Entrada**:
```python
# Código atual com problemas
class GLPIService:
    def get_data(self, type, filters):
        # Código monolítico
        # Sem tratamento de erro
        # Sem cache
        pass
```

**Saída Esperada**:
- Código refatorado
- Separação de responsabilidades
- Tratamento de erros
- Cache implementado
- Testes atualizados

## 🔧 Scripts de Automação

### Script Principal de Testes

```python
#!/usr/bin/env python3
# docs/ai/sandbox/scripts/run_sandbox.py

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

class SandboxRunner:
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.results = []
    
    def run_all_tests(self) -> Dict:
        """Executa todos os testes do sandbox"""
        results = {
            'prompt_tests': self.run_prompt_tests(),
            'performance_tests': self.run_performance_tests(),
            'integration_tests': self.run_integration_tests(),
            'code_quality_tests': self.run_code_quality_tests()
        }
        
        self.generate_report(results)
        return results
    
    def run_prompt_tests(self) -> List[Dict]:
        """Executa testes de prompts"""
        test_cases = self.load_test_cases('prompts')
        results = []
        
        for case in test_cases:
            result = self.execute_prompt_test(case)
            results.append(result)
            
        return results
    
    def generate_report(self, results: Dict) -> None:
        """Gera relatório dos testes"""
        report_path = Path('docs/ai/sandbox/results/latest_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Relatório gerado: {report_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sandbox de Testes IA')
    parser.add_argument('--config', help='Arquivo de configuração')
    parser.add_argument('--test-type', choices=['all', 'prompts', 'performance', 'integration'])
    
    args = parser.parse_args()
    
    runner = SandboxRunner(args.config)
    
    if args.test_type == 'all':
        results = runner.run_all_tests()
    elif args.test_type == 'prompts':
        results = runner.run_prompt_tests()
    # ... outros tipos
    
    print(f"Testes concluídos. Resultados: {len(results)} casos testados")
```

### Configuração do Sandbox

```json
// docs/ai/sandbox/config/sandbox.json
{
  "environment": "sandbox",
  "ai_models": {
    "primary": "claude-3-sonnet",
    "fallback": "gpt-4"
  },
  "test_settings": {
    "timeout": 30,
    "max_retries": 3,
    "parallel_tests": 4
  },
  "mock_data": {
    "glpi_url": "http://localhost:8080/mock-glpi",
    "redis_url": "redis://localhost:6379/15"
  },
  "metrics": {
    "accuracy_threshold": 0.85,
    "performance_threshold": 2.0,
    "quality_threshold": 0.90
  }
}
```

## 📈 Métricas e Relatórios

### Dashboard de Métricas

```python
# docs/ai/sandbox/scripts/metrics_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

def create_dashboard():
    st.title('🧪 Sandbox IA - Dashboard de Métricas')
    
    # Carregar dados dos testes
    results = load_test_results()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric('Precisão Média', f"{results['accuracy']:.2%}")
    
    with col2:
        st.metric('Tempo Médio', f"{results['avg_time']:.2f}s")
    
    with col3:
        st.metric('Qualidade Código', f"{results['code_quality']:.2%}")
    
    with col4:
        st.metric('Taxa Sucesso', f"{results['success_rate']:.2%}")
    
    # Gráficos
    st.subheader('Performance por Tipo de Teste')
    fig = px.bar(results['by_type'], x='test_type', y='performance')
    st.plotly_chart(fig)
    
    # Histórico
    st.subheader('Histórico de Testes')
    fig_timeline = px.line(results['timeline'], x='date', y='accuracy')
    st.plotly_chart(fig_timeline)

if __name__ == '__main__':
    create_dashboard()
```

### Executar Dashboard

```bash
# Instalar dependências
pip install streamlit plotly

# Executar dashboard
streamlit run docs/ai/sandbox/scripts/metrics_dashboard.py
```

## 🔒 Segurança e Isolamento

### Medidas de Segurança

1. **Isolamento de Dados**:
   - Dados mock apenas
   - Sem acesso a produção
   - Ambiente containerizado

2. **Controle de Acesso**:
   - Tokens específicos para sandbox
   - Rate limiting agressivo
   - Logs de todas as operações

3. **Validação de Código**:
   - Análise estática automática
   - Verificação de vulnerabilidades
   - Sandbox de execução

### Docker para Isolamento

```dockerfile
# docs/ai/sandbox/Dockerfile
FROM python:3.11-slim

WORKDIR /sandbox

# Instalar dependências
COPY requirements-sandbox.txt .
RUN pip install -r requirements-sandbox.txt

# Copiar código do sandbox
COPY docs/ai/sandbox/ .

# Usuário não-root
RUN useradd -m sandbox
USER sandbox

# Comando padrão
CMD ["python", "scripts/run_sandbox.py"]
```

```bash
# Construir e executar
docker build -t glpi-sandbox docs/ai/sandbox/
docker run --rm -v $(pwd)/docs/ai/sandbox/results:/sandbox/results glpi-sandbox
```

## 📚 Documentação dos Resultados

### Formato de Relatório

```json
{
  "test_run": {
    "id": "run_20240115_143022",
    "timestamp": "2024-01-15T14:30:22Z",
    "duration": 45.2,
    "environment": "sandbox"
  },
  "summary": {
    "total_tests": 25,
    "passed": 23,
    "failed": 2,
    "success_rate": 0.92
  },
  "metrics": {
    "accuracy": 0.89,
    "performance": 1.8,
    "code_quality": 0.94,
    "adherence": 0.91
  },
  "details": [
    {
      "test_id": "prompt_dev_001",
      "category": "development",
      "status": "passed",
      "metrics": {
        "accuracy": 0.95,
        "time": 2.1,
        "quality": 0.92
      }
    }
  ],
  "recommendations": [
    "Otimizar prompt para cenários de debug",
    "Adicionar mais exemplos de código",
    "Melhorar validação de entrada"
  ]
}
```

## 🚀 Próximos Passos

1. **Implementar Scripts Base**:
   - `run_sandbox.py`
   - `test_prompts.py`
   - `metrics_dashboard.py`

2. **Criar Dados Mock**:
   - Respostas GLPI realistas
   - Cenários de erro
   - Casos extremos

3. **Configurar CI/CD**:
   - Testes automáticos
   - Relatórios contínuos
   - Alertas de regressão

4. **Expandir Cobertura**:
   - Mais tipos de teste
   - Integração com ferramentas externas
   - Testes de acessibilidade

---

**AI Context Tags**: `sandbox`, `testing`, `ai-integration`, `automation`, `performance`
**Related Files**: `docs/ai/prompts/development.md`, `backend/tests/`, `scripts/`
**Last Updated**: 2024-01-15