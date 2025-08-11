# 🤖 Guia do Assistente de IA - GLPI Dashboard

## 📋 Índice
- [Visão Geral](#-visão-geral)
- [Contexto do Projeto](#-contexto-do-projeto)
- [Regras de Atuação](#-regras-de-atuação)
- [Fluxo de Trabalho](#-fluxo-de-trabalho)
- [Checklist de Qualidade](#-checklist-de-qualidade)
- [Comandos Úteis](#-comandos-úteis)
- [Troubleshooting](#-troubleshooting)
- [Referências](#-referências)

## 🎯 Visão Geral

Este documento serve como guia completo para assistentes de IA que trabalham no projeto GLPI Dashboard. Ele consolida todas as informações, regras e padrões necessários para uma atuação eficiente e consistente.

### 📚 Documentos de Referência
- [`AI_PROJECT_CONTEXT.md`](./AI_PROJECT_CONTEXT.md) - Contexto geral do projeto
- [`AI_DEVELOPMENT_RULES.md`](./AI_DEVELOPMENT_RULES.md) - Regras específicas de desenvolvimento
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) - Guia de contribuição
- [`TECHNICAL_STANDARDS.md`](./TECHNICAL_STANDARDS.md) - Padrões técnicos
- [`ENVIRONMENT_CONFIG.md`](./ENVIRONMENT_CONFIG.md) - Configurações de ambiente
- [`CI_CD_CONFIG.md`](./CI_CD_CONFIG.md) - Configurações de CI/CD

## 🏗️ Contexto do Projeto

### Arquitetura
```
GLPI Dashboard
├── Frontend (React + TypeScript + Vite)
│   ├── Components (shadcn/ui + Tailwind CSS)
│   ├── Hooks (Custom hooks para lógica)
│   ├── Services (API calls)
│   └── Types (TypeScript definitions)
└── Backend (Python + Flask)
    ├── API Routes (RESTful endpoints)
    ├── Services (Business logic)
    ├── Models (Data models)
    └── Utils (Utilities)
```

### Tecnologias Principais
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend**: Python 3.11, Flask, SQLAlchemy, Redis
- **Database**: MySQL 8.0
- **Testing**: Vitest (Frontend), pytest (Backend), Playwright (E2E)
- **DevOps**: Docker, GitHub Actions, AWS

### Objetivos do Projeto
1. **Dashboard de Métricas**: Visualização de dados do GLPI
2. **Performance de Técnicos**: Ranking e estatísticas
3. **Análise de Tendências**: Gráficos e insights
4. **Interface Moderna**: UX/UI otimizada
5. **Alta Performance**: Cache e otimizações

## ⚡ Regras de Atuação

### 🔍 Análise Antes da Ação
```markdown
1. **SEMPRE** analise o contexto completo antes de agir
2. **SEMPRE** verifique arquivos relacionados
3. **SEMPRE** entenda o impacto das mudanças
4. **SEMPRE** considere as dependências
5. **SEMPRE** valide após implementar
```

### 🎯 Priorização de Tarefas
```markdown
1. **CRÍTICO**: Bugs que quebram funcionalidades
2. **ALTO**: Melhorias de performance e segurança
3. **MÉDIO**: Novas funcionalidades
4. **BAIXO**: Refatorações e otimizações
```

### 🛠️ Regras Técnicas

#### Frontend (React + TypeScript)
```typescript
// ✅ SEMPRE use TypeScript strict
// ✅ SEMPRE defina interfaces para props
// ✅ SEMPRE use React.FC para componentes
// ✅ SEMPRE implemente error boundaries
// ✅ SEMPRE otimize re-renders (useMemo, useCallback)

interface ComponentProps {
  title: string;
  isVisible?: boolean;
  onAction?: (value: string) => void;
}

export const Component: React.FC<ComponentProps> = ({ 
  title, 
  isVisible = true, 
  onAction 
}) => {
  // Implementation
};
```

#### Backend (Python + Flask)
```python
# ✅ SEMPRE use type hints
# ✅ SEMPRE implemente error handling
# ✅ SEMPRE use logging estruturado
# ✅ SEMPRE valide inputs
# ✅ SEMPRE implemente cache quando apropriado

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def get_data(start_date: datetime, limit: Optional[int] = 10) -> List[Dict]:
    """Get data with proper validation and error handling."""
    try:
        # Validation
        if limit and (limit < 1 or limit > 1000):
            raise ValueError("Limit must be between 1 and 1000")
        
        # Implementation
        result = fetch_from_database(start_date, limit)
        logger.info(f"Retrieved {len(result)} records")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise
```

### 🧪 Regras de Testes
```markdown
1. **SEMPRE** mantenha cobertura ≥ 80%
2. **SEMPRE** teste casos de erro
3. **SEMPRE** use mocks para dependências externas
4. **SEMPRE** teste componentes isoladamente
5. **SEMPRE** implemente testes E2E para fluxos críticos
```

## 🔄 Fluxo de Trabalho

### 1. Análise Inicial
```bash
# Verificar status do projeto
git status
git log --oneline -5

# Verificar dependências
cd frontend && npm list
cd .. && pip list

# Verificar testes
cd frontend && npm test
cd .. && python -m pytest
```

### 2. Desenvolvimento
```bash
# Criar branch para feature/fix
git checkout -b feature/nova-funcionalidade

# Desenvolvimento iterativo
# 1. Implementar
# 2. Testar
# 3. Validar
# 4. Refinar

# Commit frequente
git add .
git commit -m "feat: implementa nova funcionalidade"
```

### 3. Validação
```bash
# Frontend
cd frontend
npm run lint
npm run type-check
npm test
npm run build

# Backend
flake8 .
black --check .
mypy .
pytest --cov=.
```

### 4. Deploy
```bash
# Merge para develop
git checkout develop
git merge feature/nova-funcionalidade

# Push para trigger CI/CD
git push origin develop
```

## ✅ Checklist de Qualidade

### 📝 Código
- [ ] TypeScript strict mode ativado
- [ ] Todas as funções têm type hints (Python)
- [ ] Interfaces definidas para todas as props
- [ ] Error handling implementado
- [ ] Logging adequado
- [ ] Validação de inputs
- [ ] Documentação JSDoc/Docstring

### 🧪 Testes
- [ ] Cobertura ≥ 80%
- [ ] Testes unitários passando
- [ ] Testes de integração passando
- [ ] Testes E2E passando (se aplicável)
- [ ] Casos de erro testados
- [ ] Mocks apropriados

### 🎨 UI/UX
- [ ] Design responsivo
- [ ] Acessibilidade (ARIA labels)
- [ ] Loading states
- [ ] Error states
- [ ] Performance otimizada
- [ ] SEO básico

### 🔒 Segurança
- [ ] Inputs validados e sanitizados
- [ ] Autenticação implementada
- [ ] Autorização verificada
- [ ] CORS configurado
- [ ] Rate limiting ativo
- [ ] Logs de segurança

### 📊 Performance
- [ ] Queries otimizadas
- [ ] Cache implementado
- [ ] Bundle size otimizado
- [ ] Lazy loading ativo
- [ ] Compressão habilitada
- [ ] CDN configurado

## 🛠️ Comandos Úteis

### Frontend
```bash
# Desenvolvimento
npm run dev              # Servidor de desenvolvimento
npm run build            # Build de produção
npm run preview          # Preview do build

# Qualidade
npm run lint             # ESLint
npm run lint:fix         # Fix automático
npm run format           # Prettier
npm run type-check       # TypeScript check

# Testes
npm test                 # Testes unitários
npm run test:coverage    # Cobertura
npm run test:e2e         # Testes E2E
npm run test:watch       # Watch mode

# Dependências
npm audit                # Audit de segurança
npm audit fix            # Fix vulnerabilidades
npm outdated             # Dependências desatualizadas
npm update               # Atualizar dependências
```

### Backend
```bash
# Desenvolvimento
python app.py            # Servidor de desenvolvimento
flask run --debug        # Flask debug mode
gunicorn app:app         # Servidor de produção

# Qualidade
flake8 .                 # Linting
black .                  # Formatação
isort .                  # Import sorting
mypy .                   # Type checking

# Testes
pytest                   # Testes unitários
pytest --cov=.           # Cobertura
pytest -v                # Verbose
pytest --lf              # Last failed

# Dependências
pip list                 # Listar dependências
pip check                # Verificar compatibilidade
safety check             # Audit de segurança
pip-audit                # Audit alternativo
```

### Docker
```bash
# Desenvolvimento
docker-compose up -d     # Subir serviços
docker-compose down      # Parar serviços
docker-compose logs -f   # Logs em tempo real

# Produção
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml down

# Manutenção
docker system prune      # Limpar sistema
docker image prune       # Limpar imagens
docker volume prune      # Limpar volumes
```

### Git
```bash
# Fluxo básico
git status               # Status atual
git add .                # Adicionar mudanças
git commit -m "message"  # Commit
git push                 # Push para remote

# Branches
git branch               # Listar branches
git checkout -b feature  # Criar branch
git merge feature        # Merge branch
git branch -d feature    # Deletar branch

# Histórico
git log --oneline        # Log resumido
git diff                 # Diferenças
git show HEAD            # Último commit
```

## 🚨 Troubleshooting

### Problemas Comuns

#### Frontend
```bash
# Erro de dependências
rm -rf node_modules package-lock.json
npm install

# Erro de TypeScript
npm run type-check
# Verificar tsconfig.json

# Erro de build
npm run build
# Verificar imports e exports

# Erro de testes
npm test -- --reporter=verbose
# Verificar mocks e setup
```

#### Backend
```bash
# Erro de dependências
pip install -r requirements.txt
# Verificar versões Python

# Erro de banco
# Verificar conexão e credenciais
# Verificar migrations

# Erro de cache
# Verificar Redis connection
# Limpar cache se necessário

# Erro de testes
pytest -v -s
# Verificar fixtures e mocks
```

#### Docker
```bash
# Erro de build
docker-compose build --no-cache

# Erro de rede
docker network ls
docker network prune

# Erro de volumes
docker volume ls
docker volume prune

# Logs detalhados
docker-compose logs service-name
```

### Debugging

#### Frontend
```typescript
// Console debugging
console.log('Debug:', data);
console.table(array);
console.time('operation');
console.timeEnd('operation');

// React DevTools
// Chrome Extension: React Developer Tools

// Performance
const start = performance.now();
// ... operation
const end = performance.now();
console.log(`Operation took ${end - start} ms`);
```

#### Backend
```python
# Logging debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {data}")

# Breakpoint debugging
import pdb; pdb.set_trace()

# Performance
import time
start = time.time()
# ... operation
end = time.time()
logger.info(f"Operation took {end - start:.2f} seconds")
```

## 📚 Referências

### Documentação Oficial
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/docs/)
- [Vite](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [pytest](https://docs.pytest.org/)
- [Vitest](https://vitest.dev/guide/)
- [Playwright](https://playwright.dev/docs/intro)

### Ferramentas
- [ESLint](https://eslint.org/docs/)
- [Prettier](https://prettier.io/docs/)
- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [MyPy](https://mypy.readthedocs.io/)
- [Docker](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Padrões e Convenções
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [REST API Design](https://restfulapi.net/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Python Style Guide (PEP 8)](https://pep8.org/)

## 🎯 Próximos Passos

### Curto Prazo (1-2 semanas)
1. **Corrigir testes falhando**
   - Investigar falhas em `useDashboard.test.ts`
   - Ajustar mocks e timeouts
   - Garantir 100% de aprovação

2. **Implementar Error Boundaries**
   - Componente de Error Boundary
   - Fallback UI para erros
   - Logging de erros

3. **Otimizar Performance**
   - Implementar lazy loading
   - Otimizar re-renders
   - Adicionar memoização

### Médio Prazo (2-4 semanas)
1. **Implementar Autenticação**
   - Sistema de login
   - JWT tokens
   - Proteção de rotas

2. **Adicionar Monitoramento**
   - Health checks
   - Métricas de performance
   - Alertas automáticos

3. **Configurar CI/CD**
   - Pipeline completo
   - Deploy automático
   - Quality gates

### Longo Prazo (1-3 meses)
1. **Implementar Testes E2E**
   - Cobertura completa
   - Testes de regressão
   - Automação completa

2. **Otimizar Infraestrutura**
   - Load balancing
   - Auto scaling
   - Backup automático

3. **Adicionar Funcionalidades**
   - Relatórios avançados
   - Dashboards customizáveis
   - Integração com outras ferramentas

---

**📝 Nota**: Este documento deve ser atualizado regularmente conforme o projeto evolui. Sempre consulte a versão mais recente antes de iniciar qualquer trabalho.

**🔄 Última atualização**: 2024-12-29  
**📋 Versão**: 1.0.0  
**👤 Responsável**: AI Assistant  
**📧 Contato**: Equipe de Desenvolvimento