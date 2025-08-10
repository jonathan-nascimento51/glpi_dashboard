##  Descrição

<!-- Descreva brevemente as mudanças implementadas -->

### Tipo de Mudança
- [ ]  Bug fix (mudança que corrige um problema)
- [ ]  Nova feature (mudança que adiciona funcionalidade)
- [ ]  Breaking change (mudança que quebra compatibilidade)
- [ ]  Documentação (mudanças apenas na documentação)
- [ ]  Refatoração (mudança que não adiciona feature nem corrige bug)
- [ ]  Performance (mudança que melhora performance)
- [ ]  Testes (adição ou correção de testes)
- [ ]  Chore (mudanças em build, CI, dependências, etc.)

##  Como Testar

<!-- Descreva os passos para testar as mudanças -->

1. 
2. 
3. 

##  Checklist de Qualidade

### Backend (Python/FastAPI)
- [ ]  **Lint OK**: Executei `ruff check` sem erros
- [ ]  **Format OK**: Executei `ruff format --check` sem erros
- [ ]  **Types OK**: Executei `mypy` sem erros
- [ ]  **Tests OK**: Executei `pytest` e todos os testes passaram
- [ ]  A cobertura de testes não diminuiu significativamente
- [ ]  Executei `bandit` e `safety` sem vulnerabilidades críticas

### Frontend (TypeScript/React)
- [ ]  **Lint OK**: Executei `npm run lint` sem erros
- [ ]  **Format OK**: Executei `npm run format:check` sem erros
- [ ]  **Types OK**: Executei `npm run type-check` sem erros
- [ ]  **Tests OK**: Executei `npm test` e todos os testes passaram
- [ ]  **Build OK**: Executei `npm run build` com sucesso
- [ ]  **Storybook OK**: Executei `npm run storybook:build` com sucesso
- [ ]  **Orval sem drift**: Executei `npm run check:drift` sem detectar drift da API
- [ ]  A cobertura de testes atende aos limites mínimos (80% global, 85% components/services, 90% hooks)

### CI/CD & Quality Gates
- [ ]  **CI Verde**: O pipeline CI passou completamente em todos os jobs
- [ ]  **Quality Gates**: Todos os quality gates (SonarQube, segurança, etc.) passaram
- [ ]  **Visual Regression**: Chromatic passou ou mudanças visuais foram aprovadas
- [ ]  **Integration Tests**: Testes de integração passaram
- [ ]  **Schemathesis**: Fuzzing da API passou sem erros críticos
- [ ]  **Security Scan**: Varredura de segurança passou
- [ ]  **Performance**: Não há degradação significativa de performance

### Documentação
- [ ]  Atualizei a documentação relevante
- [ ]  Atualizei comentários no código quando necessário
- [ ]  Adicionei/atualizei docstrings para novas funções/classes
- [ ]  Atualizei o Storybook com novos componentes/stories

### Git & Merge
- [ ]  Não há conflitos de merge
- [ ]  O branch está atualizado com a branch base
- [ ]  Commit messages seguem o padrão conventional commits
- [ ]  PR está adequadamente taggeado e categorizado

##  Issues Relacionadas

<!-- Referencie issues relacionadas usando "Closes #123" ou "Fixes #123" -->

Closes #
Fixes #
Related to #

##  Screenshots/Videos

<!-- Adicione screenshots ou videos das mudanças visuais, se aplicável -->

##  Notas Adicionais

<!-- Adicione qualquer informação adicional relevante -->

##  Revisão

<!-- Para os revisores -->

### Pontos de Atenção
- [ ] Verificar se a lógica de negócio está correta
- [ ] Verificar se os testes cobrem os casos edge
- [ ] Verificar se não há vazamentos de memória
- [ ] Verificar se as mudanças não afetam a performance
- [ ] Verificar se a segurança não foi comprometida
- [ ] Verificar se as feature flags estão sendo usadas corretamente

### Checklist do Revisor
- [ ]  **Código Limpo**: O código está limpo e bem estruturado
- [ ]  **Testes Adequados**: Os testes são adequados e passam
- [ ]  **Documentação**: A documentação está atualizada
- [ ]  **Segurança**: Não há problemas de segurança óbvios
- [ ]  **Resolve o Problema**: O PR resolve o problema descrito
- [ ]  **Performance**: Não há degradação de performance
- [ ]  **UI/UX**: Mudanças visuais estão consistentes com o design system

---

** Lembrete Importante**: 
- Este PR será automaticamente testado pelo CI com múltiplos quality gates
- **Todos os checks devem estar  VERDES** antes de solicitar revisão
- Quality gates incluem: lint, types, tests, security scan, visual regression
- PRs com quality gates falhando serão **automaticamente bloqueados**
- Para mudanças visuais, aprovação explícita no Chromatic é **obrigatória**

** Pipeline Status**: Verifique se todos os jobs do CI estão passando antes de marcar como ready for review.
