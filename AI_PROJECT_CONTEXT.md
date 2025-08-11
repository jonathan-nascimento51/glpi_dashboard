# 🤖 AI Project Context - GLPI Dashboard

## 📋 Visão Geral do Projeto

Este é um dashboard para análise de dados do GLPI (Gestão Livre de Parque de Informática), desenvolvido com:
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python + Flask + Redis
- **Banco**: Integração com GLPI MySQL
- **Infraestrutura**: Docker + Docker Compose

## 🎯 Objetivos do Sistema

### Funcionalidades Principais
1. **Dashboard de Métricas**: Visualização de KPIs de tickets e técnicos
2. **Ranking de Técnicos**: Performance e produtividade
3. **Análise de Tendências**: Comparação temporal de métricas
4. **Filtros Avançados**: Por data, status, técnico, etc.
5. **Cache Inteligente**: Otimização de performance com Redis

### Métricas Monitoradas
- Total de tickets (abertos, fechados, pendentes)
- Tempo médio de resolução
- Performance por técnico
- Tendências temporais
- Distribuição por status

## 🏗️ Arquitetura do Sistema

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── dashboard/       # Componentes específicos do dashboard
│   │   ├── ui/             # Componentes de interface (shadcn/ui)
│   │   └── layout/         # Componentes de layout
│   ├── hooks/              # Custom hooks
│   ├── services/           # Serviços de API
│   ├── types/              # Definições TypeScript
│   ├── utils/              # Utilitários
│   └── __tests__/          # Testes unitários
```

### Backend (Python + Flask)
```
backend/
├── api/                    # Rotas da API
├── services/               # Lógica de negócio
│   ├── glpi_service.py    # Integração com GLPI
│   └── api_service.py     # Serviços da API
├── config/                 # Configurações
├── schemas/                # Validação de dados
└── utils/                  # Utilitários
```

## 🔧 Padrões de Desenvolvimento

### Convenções de Código

#### Frontend (TypeScript/React)
- **Componentes**: PascalCase (`MetricsGrid.tsx`)
- **Hooks**: camelCase com prefixo `use` (`useDashboard.ts`)
- **Tipos**: PascalCase com sufixo apropriado (`MetricsData`, `TechnicianRanking`)
- **Props**: Interface com sufixo `Props` (`MetricsGridProps`)
- **Constantes**: UPPER_SNAKE_CASE

#### Backend (Python)
- **Arquivos**: snake_case (`glpi_service.py`)
- **Classes**: PascalCase (`GLPIService`)
- **Funções**: snake_case (`get_technician_ranking`)
- **Constantes**: UPPER_SNAKE_CASE

### Estrutura de Commits
Usar Conventional Commits:
```
feat: adiciona nova funcionalidade
fix: corrige bug
refactor: refatora código
test: adiciona/modifica testes
docs: atualiza documentação
style: formatação de código
perf: melhoria de performance
ci: configuração de CI/CD
```

## 🧪 Estratégia de Testes

### Frontend
- **Unitários**: Vitest + Testing Library
- **Componentes**: Renderização e interações
- **Hooks**: Lógica de estado e efeitos
- **Serviços**: Mocks de API

### Backend
- **Unitários**: pytest
- **Integração**: Testes de API
- **Performance**: Testes de carga

### Cobertura Mínima
- Frontend: 80%
- Backend: 85%
- Crítico: 95%

## 🚀 Fluxo de Desenvolvimento

### 1. Setup Local
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
npm install
npm run dev
```

### 2. Desenvolvimento
1. Criar branch: `git checkout -b feat/nova-funcionalidade`
2. Desenvolver com TDD quando possível
3. Executar testes: `npm test` (frontend) / `pytest` (backend)
4. Build: `npm run build`
5. Commit seguindo convenções
6. Push e criar PR

### 3. Code Review
- Verificar padrões de código
- Executar testes
- Validar performance
- Revisar segurança

## 📊 Monitoramento e Performance

### Métricas Importantes
- **Frontend**: Bundle size, Core Web Vitals
- **Backend**: Response time, Memory usage
- **Cache**: Hit rate do Redis
- **Database**: Query performance

### Alertas
- Response time > 2s
- Error rate > 1%
- Memory usage > 80%
- Cache hit rate < 90%

## 🔒 Segurança

### Práticas Obrigatórias
- Validação de entrada em todas as APIs
- Sanitização de dados do GLPI
- Rate limiting nas APIs
- HTTPS em produção
- Logs de auditoria

### Dados Sensíveis
- Nunca logar senhas ou tokens
- Usar variáveis de ambiente
- Criptografar dados em trânsito

## 🐛 Debugging e Troubleshooting

### Logs Importantes
- **Frontend**: Console errors, Network failures
- **Backend**: API errors, Database queries
- **Cache**: Redis connections, Cache misses

### Ferramentas
- **Frontend**: React DevTools, Network tab
- **Backend**: Flask debug mode, Python debugger
- **Performance**: Lighthouse, Profiler

## 📚 Recursos e Documentação

### Links Úteis
- [GLPI API Documentation](https://glpi-project.org/)
- [React Documentation](https://react.dev/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Comandos Úteis
```bash
# Testes
npm test                    # Frontend tests
npm run test:coverage       # Coverage report
pytest                      # Backend tests
pytest --cov=backend        # Backend coverage

# Build
npm run build              # Production build
npm run preview            # Preview build

# Linting
npm run lint               # ESLint
npm run lint:fix           # Auto-fix
flake8 backend/            # Python linting
black backend/             # Python formatting

# Docker
docker-compose up -d       # Start services
docker-compose logs -f     # View logs
docker-compose down        # Stop services
```

## 🎯 Próximos Passos Prioritários

### Curto Prazo (1-2 semanas)
1. ✅ Corrigir testes falhando
2. 🔄 Implementar Error Boundaries
3. 📝 Adicionar documentação de API
4. 🔧 Configurar pre-commit hooks

### Médio Prazo (1 mês)
1. 🧪 Implementar testes E2E
2. 📊 Adicionar monitoramento
3. 🚀 Configurar CI/CD
4. 🔒 Implementar autenticação

### Longo Prazo (3 meses)
1. 📈 Otimização de performance
2. 🌐 Internacionalização
3. 📱 Responsividade mobile
4. 🔄 Real-time updates

---

**Última atualização**: 2024-12-29
**Versão**: 1.0.0
**Maintainer**: Equipe de Desenvolvimento