# 🤝 Guia de Contribuição - GLPI Dashboard

Obrigado por seu interesse em contribuir com o GLPI Dashboard! Este documento fornece diretrizes para contribuições efetivas e colaboração produtiva.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Desenvolvimento](#padrões-de-desenvolvimento)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Funcionalidades](#sugerindo-funcionalidades)
- [Documentação](#documentação)

## 🤝 Código de Conduta

Este projeto adere ao [Contributor Covenant](https://www.contributor-covenant.org/). Ao participar, você concorda em manter um ambiente respeitoso e inclusivo.

### Comportamentos Esperados:
- Uso de linguagem acolhedora e inclusiva
- Respeito por diferentes pontos de vista
- Aceitação construtiva de críticas
- Foco no que é melhor para a comunidade

## 🚀 Como Contribuir

### Tipos de Contribuição

1. **🐛 Correção de Bugs**
2. **✨ Novas Funcionalidades**
3. **📚 Documentação**
4. **🧪 Testes**
5. **🎨 Melhorias de UI/UX**
6. **⚡ Otimizações de Performance**

### Fluxo de Contribuição

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua contribuição
4. **Desenvolva** seguindo os padrões
5. **Teste** suas alterações
6. **Commit** com mensagens descritivas
7. **Push** para seu fork
8. **Abra** um Pull Request

## 🛠️ Configuração do Ambiente

### Pré-requisitos

- **Python 3.9+**
- **Node.js 18+**
- **Git**
- **Redis** (opcional, para desenvolvimento)
- **GLPI 10.0+** (para testes de integração)

### Setup Inicial

```bash
# 1. Fork e clone o repositório
git clone https://github.com/SEU_USUARIO/glpi_dashboard.git
cd glpi_dashboard

# 2. Configure o upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/glpi_dashboard.git

# 3. Configure o backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configure o frontend
cd ../frontend
npm install

# 5. Configure pre-commit hooks
cd ..
pre-commit install

# 6. Configure variáveis de ambiente
cp backend/.env.example backend/.env
# Edite backend/.env com suas configurações
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Frontend (Node.js)
cd frontend
npm install
```

### 3. Mantenha seu Fork Atualizado

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## 🌿 Convenções de Branch

### Nomenclatura de Branches

Use o seguinte padrão para nomear suas branches:

```
<tipo>/<descrição-curta>
```

**Tipos de Branch:**

- `feature/` - Novas funcionalidades
- `bugfix/` - Correção de bugs
- `hotfix/` - Correções urgentes para produção
- `docs/` - Mudanças na documentação
- `refactor/` - Refatoração de código
- `test/` - Adição ou correção de testes
- `chore/` - Tarefas de manutenção

**Exemplos:**

```bash
feature/dashboard-filters
bugfix/memory-leak-charts
hotfix/security-vulnerability
docs/api-documentation
refactor/service-layer
test/integration-tests
chore/update-dependencies
```

### Criando uma Branch

```bash
# Certifique-se de estar na main atualizada
git checkout main
git pull upstream main

# Crie e mude para a nova branch
git checkout -b feature/nova-funcionalidade
```

## 💬 Convenções de Commit

### Formato de Mensagem

Use o formato **Conventional Commits**:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, ponto e vírgula ausente, etc
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção
- `perf`: Melhoria de performance
- `ci`: Mudanças no CI/CD
- `build`: Mudanças no sistema de build
- `revert`: Reversão de commit anterior

### Exemplos de Commits

```bash
# Funcionalidade
feat(dashboard): adicionar filtros de data para métricas

# Correção de bug
fix(api): corrigir vazamento de memória no cache Redis

# Documentação
docs: atualizar README com instruções de instalação

# Teste
test(service): adicionar testes unitários para GLPIService

# Refatoração
refactor(components): extrair lógica de filtros para hook customizado

# Breaking change
feat(api)!: alterar formato de resposta da API de métricas

BREAKING CHANGE: O campo 'data' agora retorna objeto em vez de array
```

### Boas Práticas de Commit

- ✅ **Commits atômicos**: Um commit = uma mudança lógica
- ✅ **Mensagens descritivas**: Explique o "o quê" e "por quê"
- ✅ **Presente imperativo**: "adicionar" não "adicionado"
- ✅ **Primeira linha ≤ 50 caracteres**
- ✅ **Corpo detalhado quando necessário**
- ❌ **Evite commits genéricos**: "fix", "update", "changes"

## ⚙️ Configuração do Ambiente

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Redis (para testes de integração)
- Git

### Configuração Completa

```bash
# 1. Clone e configure
git clone https://github.com/SEU_USERNAME/glpi_dashboard.git
cd glpi_dashboard

# 2. Configure pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Se existir

# 4. Frontend
cd ../frontend
npm install

# 5. Variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### Ferramentas de Desenvolvimento

```bash
# Instalar ferramentas de qualidade de código
pip install black isort flake8 pytest pytest-cov bandit safety
npm install -g prettier eslint
```

## 🧪 Executando Testes

### Backend (Python)

```bash
cd backend

# Testes unitários
pytest tests/unit/ -v

# Testes de integração
pytest tests/integration/ -v

# Todos os testes
pytest -v

# Com cobertura
pytest --cov=. --cov-report=html --cov-report=term-missing

# Testes específicos
pytest tests/unit/test_glpi_service.py::TestGLPIService::test_get_tickets -v
```

### Frontend (TypeScript/React)

```bash
cd frontend

# Todos os testes
npm test

# Com cobertura
npm run test:coverage

# Modo watch
npm run test:watch

# Testes específicos
npm test -- --testNamePattern="Dashboard"
```

### Verificações de Qualidade

```bash
# Backend
flake8 backend/
black --check backend/
isort --check-only backend/
bandit -r backend/

# Frontend
npm run lint
npm run format:check
npm run type-check
```

### Executar Tudo

```bash
# Com pre-commit (recomendado)
pre-commit run --all-files

# Ou manualmente
./scripts/run-all-tests.sh  # Se existir
```

## 📤 Enviando Pull Requests

### Antes de Enviar

1. ✅ **Testes passando**: Todos os testes devem passar
2. ✅ **Linting limpo**: Sem erros de linting
3. ✅ **Cobertura mantida**: Não diminuir cobertura significativamente
4. ✅ **Documentação atualizada**: Se necessário
5. ✅ **Commits organizados**: Squash se necessário

### Processo de Envio

```bash
# 1. Finalize suas mudanças
git add .
git commit -m "feat(dashboard): adicionar filtros de data"

# 2. Atualize com a main
git fetch upstream
git rebase upstream/main

# 3. Execute testes finais
pytest && npm test

# 4. Push para seu fork
git push origin feature/nova-funcionalidade

# 5. Abra PR no GitHub
```

### Template de PR

Use o template fornecido e preencha:

- 📋 **Descrição**: O que foi implementado
- 🔄 **Tipo de mudança**: Feature, bugfix, etc.
- 🧪 **Como testar**: Passos para validar
- ✅ **Checklist**: Marque todos os itens aplicáveis

## ✅ Checklist de Revisão de Código

### Para o Autor

**Funcionalidade:**
- [ ] A funcionalidade funciona conforme especificado
- [ ] Casos edge foram considerados
- [ ] Performance não foi degradada
- [ ] Não há regressões

**Código:**
- [ ] Código limpo e legível
- [ ] Nomes de variáveis/funções descritivos
- [ ] Funções pequenas e focadas
- [ ] Sem código duplicado
- [ ] Comentários onde necessário

**Testes:**
- [ ] Testes unitários adicionados/atualizados
- [ ] Testes de integração quando aplicável
- [ ] Cobertura de testes mantida (>80%)
- [ ] Testes passando localmente

**Logs e Monitoramento:**
- [ ] Logs apropriados adicionados
- [ ] Níveis de log corretos (DEBUG, INFO, WARNING, ERROR)
- [ ] Informações sensíveis não logadas
- [ ] Métricas de performance quando relevante

**Validações e Tratamento de Erro:**
- [ ] Validação de entrada implementada
- [ ] Tratamento de erro apropriado
- [ ] Mensagens de erro informativas
- [ ] Fallbacks para casos de falha
- [ ] Timeouts configurados adequadamente

**Segurança:**
- [ ] Sem vazamento de informações sensíveis
- [ ] Validação de autorização quando necessária
- [ ] Sanitização de entrada
- [ ] Sem vulnerabilidades óbvias

**Documentação:**
- [ ] Docstrings atualizadas
- [ ] README atualizado se necessário
- [ ] Comentários de código adequados
- [ ] Documentação de API atualizada

### Para o Revisor

**Revisão de Código:**
- [ ] Lógica de negócio está correta
- [ ] Arquitetura e design apropriados
- [ ] Padrões do projeto seguidos
- [ ] Sem code smells óbvios

**Testes e Qualidade:**
- [ ] Testes cobrem cenários importantes
- [ ] Qualidade dos testes é adequada
- [ ] CI/CD pipeline passou
- [ ] Cobertura de código aceitável

**Performance e Escalabilidade:**
- [ ] Sem problemas de performance óbvios
- [ ] Uso eficiente de recursos
- [ ] Consultas de banco otimizadas
- [ ] Cache utilizado apropriadamente

**Integração:**
- [ ] Compatibilidade com código existente
- [ ] APIs mantêm retrocompatibilidade
- [ ] Dependências justificadas
- [ ] Configuração adequada

## 📏 Padrões de Código

### Backend (Python)

```python
# Imports organizados
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from flask import Flask, request
from redis import Redis

from config.settings import active_config
from services.glpi_service import GLPIService

# Docstrings
def get_dashboard_metrics(date_filter: Optional[str] = None) -> Dict[str, Any]:
    """Obtém métricas do dashboard com filtro de data opcional.
    
    Args:
        date_filter: Filtro de data no formato 'YYYY-MM-DD'
        
    Returns:
        Dict contendo métricas do dashboard
        
    Raises:
        ValueError: Se date_filter tem formato inválido
        GLPIServiceError: Se falha na comunicação com GLPI
    """
    pass

# Type hints
class GLPIService:
    def __init__(self, base_url: str, app_token: str, user_token: str) -> None:
        self.base_url = base_url
        self.app_token = app_token
        self.user_token = user_token
        self._session_token: Optional[str] = None
```

### Frontend (TypeScript/React)

```typescript
// Interfaces bem definidas
interface DashboardMetrics {
  totalTickets: number;
  openTickets: number;
  closedTickets: number;
  trends: TrendData[];
}

// Componentes funcionais com tipos
interface DashboardProps {
  dateFilter?: string;
  onFilterChange: (filter: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ dateFilter, onFilterChange }) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hooks customizados
  const { data, isLoading, error: apiError } = useDashboardMetrics(dateFilter);

  return (
    <div className="dashboard">
      {/* JSX limpo e organizado */}
    </div>
  );
};

export default Dashboard;
```

### Estrutura de Arquivos

```
backend/
├── api/           # Endpoints da API
├── config/        # Configurações
├── services/      # Lógica de negócio
├── utils/         # Utilitários
├── tests/         # Testes
└── schemas/       # Schemas de validação

frontend/src/
├── components/    # Componentes React
├── hooks/         # Hooks customizados
├── services/      # Serviços de API
├── types/         # Definições de tipos
├── utils/         # Utilitários
└── __tests__/     # Testes
```

## 🆘 Obtendo Ajuda

- 📖 **Documentação**: Consulte o README e docs/
- 💬 **Discussões**: Use GitHub Discussions
- 🐛 **Issues**: Reporte bugs com template
- 📧 **Email**: Para questões sensíveis

## 📝 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

**Obrigado por contribuir! 🎉**

Sua contribuição ajuda a tornar o GLPI Dashboard melhor para todos!