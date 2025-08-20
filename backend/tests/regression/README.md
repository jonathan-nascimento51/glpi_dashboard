# Sistema de Testes de Regressão - GLPI Dashboard

Este diretório contém o sistema completo de testes de regressão para detectar divergências nas métricas do GLPI Dashboard.

## 📁 Estrutura

```
regression/
├── metrics_regression_comparator.py  # Comparador principal
├── run_regression_tests.py           # Script de execução
├── README.md                         # Esta documentação
├── snapshots/                        # Snapshots baseline
│   ├── snapshots_index.json         # Índice de snapshots
│   └── *.json                        # Arquivos de snapshot
└── reports/                          # Relatórios de teste
    ├── consolidated_*.json           # Relatórios consolidados
    └── regression_*.json             # Relatórios individuais
```

## 🚀 Início Rápido

### 1. Configurar Snapshots Baseline

```bash
# Capturar snapshots de todos os endpoints principais
python run_regression_tests.py --action setup
```

### 2. Executar Teste Rápido (Smoke Test)

```bash
# Teste rápido dos endpoints críticos
python run_regression_tests.py --action smoke
```

### 3. Executar Suite Completa

```bash
# Executar todos os testes de regressão
python run_regression_tests.py --action test
# ou
python run_regression_tests.py --action full
```

## 🔧 Uso Avançado

### Comparador Direto

```python
from metrics_regression_comparator import MetricsRegressionComparator

# Criar comparador com tolerância personalizada
comparator = MetricsRegressionComparator(tolerance=0.05)  # 5%

# Capturar snapshot baseline
snapshot_path = comparator.capture_baseline_snapshot(
    endpoint="/metrics",
    params={"start_date": "2024-01-01"},
    filename="custom_metrics.json"
)

# Executar teste de regressão
report = comparator.run_regression_test(
    snapshot_path=snapshot_path,
    endpoint="/metrics",
    params={"start_date": "2024-01-01"},
    test_name="custom_test"
)

# Verificar resultado
if report.success:
    print("✅ Teste passou!")
else:
    print(f"❌ {report.failed_comparisons} diferenças encontradas")
    for diff in report.differences:
        if not diff.match:
            print(f"  {diff.field_path}: {diff.expected_value} → {diff.actual_value}")
```

### Configuração de Tolerância

```python
# Tolerância numérica (padrão: 0.01 = 1%)
comparator = MetricsRegressionComparator(tolerance=0.05)

# Tolerância zero (comparação exata)
comparator = MetricsRegressionComparator(tolerance=0.0)
```

## 📊 Endpoints Testados

### Métricas Principais
- `GET /metrics` - Métricas do dashboard
- `GET /metrics?start_date=X&end_date=Y` - Métricas com filtro de data

### Métricas Filtradas
- `GET /metrics/filtered?status=novo` - Tickets novos
- `GET /metrics/filtered?status=progresso` - Tickets em progresso

### Ranking de Técnicos
- `GET /technicians/ranking?limit=10` - Ranking geral
- `GET /technicians/ranking?level=N1&limit=10` - Por nível (N1-N4)

### Tickets
- `GET /tickets/new?limit=5` - Tickets novos

## 📈 Relatórios

### Relatório Individual

```json
{
  "test_name": "dashboard_metrics_baseline",
  "timestamp": "2024-01-15T10:30:00",
  "success": false,
  "total_comparisons": 45,
  "failed_comparisons": 3,
  "execution_time": 1.23,
  "differences": [
    {
      "field_path": "data[0].total",
      "expected_value": 150,
      "actual_value": 148,
      "difference_type": "value_change",
      "match": false
    }
  ]
}
```

### Relatório Consolidado

```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "total_tests": 10,
    "passed_tests": 7,
    "failed_tests": 3,
    "success_rate": 70.0,
    "total_comparisons": 450,
    "total_differences": 12
  },
  "test_results": [...],
  "differences_by_type": {
    "value_change": [...],
    "missing_field": [...],
    "type_mismatch": [...]
  },
  "failed_tests_details": [...]
}
```

## 🔍 Tipos de Diferenças Detectadas

1. **value_change** - Valor alterado
2. **missing_field** - Campo ausente
3. **extra_field** - Campo extra
4. **type_mismatch** - Tipo incompatível
5. **structure_change** - Mudança na estrutura

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# URL base da API (padrão: http://localhost:5000)
export GLPI_DASHBOARD_API_URL="http://localhost:5000"

# Timeout para requisições (padrão: 30s)
export API_TIMEOUT="30"

# Diretório de snapshots personalizado
export SNAPSHOTS_DIR="/path/to/custom/snapshots"
```

### Configuração no Código

```python
comparator = MetricsRegressionComparator(
    base_url="http://localhost:5000",
    tolerance=0.05,
    timeout=30,
    snapshots_dir="custom_snapshots",
    reports_dir="custom_reports"
)
```

## 🚨 Integração com CI/CD

### GitHub Actions

```yaml
name: Regression Tests

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Diário às 2h

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Start GLPI Dashboard
        run: |
          python app.py &
          sleep 10
      
      - name: Run Smoke Test
        run: |
          cd backend/tests/regression
          python run_regression_tests.py --action smoke
      
      - name: Run Full Regression Suite
        run: |
          cd backend/tests/regression
          python run_regression_tests.py --action full
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: regression-reports
          path: backend/tests/regression/reports/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Start Application') {
            steps {
                sh 'python app.py &'
                sh 'sleep 10'
            }
        }
        
        stage('Regression Tests') {
            steps {
                dir('backend/tests/regression') {
                    sh 'python run_regression_tests.py --action full'
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'backend/tests/regression/reports/**/*.json'
        }
        failure {
            emailext (
                subject: "Regression Tests Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Regression tests detected changes in API responses.",
                to: "dev-team@company.com"
            )
        }
    }
}
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### 1. Conexão com API Falha

```bash
# Verificar se a API está rodando
curl http://localhost:5000/health

# Verificar logs da aplicação
tail -f logs/app.log
```

#### 2. Snapshots Desatualizados

```bash
# Recriar snapshots baseline
python run_regression_tests.py --action setup
```

#### 3. Muitas Diferenças Numéricas

```python
# Aumentar tolerância
comparator = MetricsRegressionComparator(tolerance=0.1)  # 10%
```

#### 4. Timeout em Requisições

```python
# Aumentar timeout
comparator = MetricsRegressionComparator(timeout=60)  # 60s
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Executar com logs detalhados
comparator = MetricsRegressionComparator()
report = comparator.run_regression_test(...)
```

## 📝 Melhores Práticas

1. **Snapshots Baseline**
   - Capture snapshots em ambiente estável
   - Atualize regularmente (semanalmente)
   - Versione snapshots importantes

2. **Tolerância**
   - Use 1-5% para métricas numéricas
   - Use 0% para estruturas de dados
   - Ajuste conforme necessário

3. **Frequência de Testes**
   - Smoke tests: A cada commit
   - Suite completa: Diariamente
   - Baseline update: Semanalmente

4. **Monitoramento**
   - Configure alertas para falhas
   - Monitore tendências de diferenças
   - Analise relatórios regularmente

## 🔗 Links Relacionados

- [Documentação da API](../../docs/API.md)
- [Guia de Testes](../../docs/TESTING.md)
- [Protocolo de Testes](../TESTING_PROTOCOL.md)
- [Monitoramento](../../monitoring/README.md)