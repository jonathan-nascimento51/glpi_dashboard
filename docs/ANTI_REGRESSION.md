# 🛡️ Medidas Anti-Regressão

Este documento descreve as medidas implementadas para prevenir regressões silenciosas no projeto.

## 📊 Cobertura de Código

### Backend (Python)

A cobertura é configurada via `pytest.ini` com as seguintes exigências:

- **Cobertura mínima global**: 80%
- **Cobertura de branches**: Habilitada
- **Relatórios**: HTML, XML, JSON e terminal
- **Falha automática**: Se cobertura < 80%

```bash
# Executar testes com cobertura
cd backend
pytest --cov=. --cov-report=term-missing
```

### Frontend (TypeScript/React)

A cobertura é configurada via `vitest.config.ts` com limites específicos:

- **Global**: 80% (branches, functions, lines, statements)
- **Components** (`./src/components/`): 85%
- **Hooks** (`./src/hooks/`): 90%
- **Services** (`./src/services/`): 85%

```bash
# Executar testes com cobertura
cd frontend
npm run test:coverage
```

## 🔄 Verificação de Drift da API

### Script check:drift

O script `check:drift` no frontend verifica se os tipos gerados pelo Orval estão sincronizados:

```bash
cd frontend
npm run check:drift
```

**O que faz:**
1. Executa `orval` para gerar tipos da API
2. Verifica se há diferenças não commitadas em `src/api/`
3. Falha se houver drift detectado

### Integração no CI

O drift check é executado automaticamente no job `frontend-tests` do CI, garantindo que:
- Tipos da API estejam sempre atualizados
- Mudanças na API sejam explicitamente commitadas
- Não haja inconsistências entre backend e frontend

## ✅ Template de Pull Request

O template `.github/pull_request_template.md` inclui verificações obrigatórias:

### Frontend
- [ ] Executei `npm run check:drift` sem detectar drift da API
- [ ] A cobertura de testes atende aos limites mínimos (80% global, 85% components/services, 90% hooks)

### Backend
- [ ] A cobertura de testes não diminuiu significativamente (mínimo 80%)

## 🚫 Gates de Qualidade no CI

### Frontend Gates
1. **Lint & Format**: ESLint + Prettier
2. **Type Check**: TypeScript
3. **Unit Tests**: Vitest com cobertura mínima
4. **API Drift Check**: Verificação automática de sincronização

### Backend Gates
1. **Lint & Format**: flake8, black, isort
2. **Type Check**: mypy
3. **Unit Tests**: pytest com cobertura mínima (80%)
4. **API Fuzzing**: Schemathesis

## 🔧 Configuração Local

### Pré-requisitos

```bash
# Backend
cd backend
pip install pytest pytest-cov

# Frontend
cd frontend
npm install
```

### Verificação Completa

```bash
# Backend
cd backend
pytest --cov=. --cov-fail-under=80

# Frontend
cd frontend
npm run test:coverage
npm run check:drift
```

## 📈 Monitoramento

### Codecov Integration

- **Backend**: Upload automático via `coverage.xml`
- **Frontend**: Upload automático via `lcov.info`
- **Flags**: `backend` e `frontend` para separação

### Relatórios Locais

- **Backend**: `htmlcov/index.html`
- **Frontend**: `coverage/index.html`

## 🚨 Troubleshooting

### Cobertura Baixa

1. Identifique arquivos com baixa cobertura:
   ```bash
   # Backend
   pytest --cov=. --cov-report=term-missing
   
   # Frontend
   npm run test:coverage
   ```

2. Adicione testes para as linhas não cobertas
3. Execute novamente para verificar

### API Drift Detectado

1. Execute o Orval para atualizar tipos:
   ```bash
   cd frontend
   npm run gen:api
   ```

2. Revise as mudanças:
   ```bash
   git diff src/api/
   ```

3. Commite as mudanças se corretas:
   ```bash
   git add src/api/
   git commit -m "feat(api): update generated types"
   ```

## 📋 Checklist de Implementação

- [x] Configuração de cobertura mínima no backend (80%)
- [x] Configuração de cobertura mínima no frontend (80-90%)
- [x] Script `check:drift` para verificação de API
- [x] Template de PR com verificações obrigatórias
- [x] Integração no CI com gates de qualidade
- [x] Documentação das medidas anti-regressão

---

**Nota**: Estas medidas garantem que o código mantenha alta qualidade e que mudanças sejam explícitas e testadas, prevenindo regressões silenciosas.