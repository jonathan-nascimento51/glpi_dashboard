# Scripts do Projeto GLPI Dashboard

Esta pasta contém todos os scripts auxiliares organizados por categoria.

## 📁 Estrutura

### `/debug`
Scripts para debug e análise do sistema:
- `debug_metrics.py` - Debug das métricas do dashboard
- `debug_trends.py` - Debug das tendências e cálculos
- `debug_react_keys.py` - Debug de chaves React duplicadas
- `check_duplicate_keys.py` - Verificação de chaves duplicadas

### `/tests`
Scripts e arquivos de teste:
- `test_trends.py` - Testes das funcionalidades de tendências
- `test_debounce_throttle.html` - Teste das implementações de debounce/throttle
- `test_date_filters.html` - Teste dos filtros de data
- `test_filters.html` - Teste geral dos filtros

### `/validation`
Scripts de validação e verificação:
- `validate_frontend_trends.py` - Validação das tendências no frontend
- `validate_trends_math.py` - Validação dos cálculos matemáticos das tendências

## 🚀 Como usar

### Scripts de Debug
```bash
# Debug das métricas
python scripts/debug/debug_metrics.py

# Debug das tendências
python scripts/debug/debug_trends.py
```

### Scripts de Teste
```bash
# Teste das tendências
python scripts/tests/test_trends.py

# Abrir testes HTML no navegador
start scripts/tests/test_debounce_throttle.html
```

### Scripts de Validação
```bash
# Validar tendências do frontend
python scripts/validation/validate_frontend_trends.py

# Validar cálculos matemáticos
python scripts/validation/validate_trends_math.py
```

## 📋 Notas

- Todos os scripts Python devem ser executados a partir da raiz do projeto
- Os arquivos HTML de teste podem ser abertos diretamente no navegador
- Certifique-se de que o ambiente virtual esteja ativado antes de executar os scripts Python