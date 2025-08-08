# Estratégia de Branches e Commits - GLPI Dashboard

## Política de Branches

### Estrutura de Branches

#### Branch Principal
- **`main`**: Branch de produção protegida
  - Contém código estável e testado
  - Merges apenas via Pull Requests aprovados
  - Deploy automático para produção
  - Protegida contra push direto

#### Branch de Desenvolvimento
- **`develop`**: Branch de integração
  - Base para novas features
  - Integração contínua ativa
  - Testes automatizados obrigatórios
  - Deploy automático para ambiente de staging

#### Branches de Feature
- **`feature/[nome-da-feature]`**: Desenvolvimento de novas funcionalidades
  - Criadas a partir de `develop`
  - Nomenclatura descritiva (ex: `feature/dashboard-filters`, `feature/user-authentication`)
  - Vida útil curta (máximo 2 semanas)
  - Merge via Pull Request para `develop`

#### Branches de Correção
- **`bugfix/[nome-do-bug]`**: Correções de bugs não críticos
  - Criadas a partir de `develop`
  - Nomenclatura descritiva (ex: `bugfix/date-validation`, `bugfix/api-timeout`)
  - Merge via Pull Request para `develop`

#### Branches de Hotfix
- **`hotfix/[nome-do-hotfix]`**: Correções críticas em produção
  - Criadas a partir de `main`
  - Merge para `main` E `develop`
  - Deploy imediato após aprovação

#### Branches de Release
- **`release/[versao]`**: Preparação para release
  - Criadas a partir de `develop`
  - Apenas correções de bugs e ajustes finais
  - Merge para `main` e `develop` após testes

### Regras de Proteção

#### Branch `main`
- ✅ Require pull request reviews (mínimo 2 aprovações)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require conversation resolution
- ✅ Restrict pushes that create files larger than 100MB
- ✅ Block force pushes
- ✅ Restrict deletions

#### Branch `develop`
- ✅ Require pull request reviews (mínimo 1 aprovação)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Block force pushes

## Política de Commits

### Formato de Commit

Utilizamos o padrão **Conventional Commits**:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos de Commit

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Alterações na documentação
- **style**: Formatação, ponto e vírgula, etc (sem mudança de código)
- **refactor**: Refatoração de código (sem nova funcionalidade ou correção)
- **perf**: Melhoria de performance
- **test**: Adição ou correção de testes
- **chore**: Tarefas de manutenção, configuração, etc
- **ci**: Mudanças na configuração de CI/CD
- **build**: Mudanças no sistema de build ou dependências
- **revert**: Reversão de commit anterior

### Exemplos de Commits

```bash
# Feature
feat(dashboard): add date range filter validation

# Bug fix
fix(api): resolve timeout issue in GLPI service

# Documentation
docs: update API documentation with new endpoints

# Refactoring
refactor(components): extract common validation logic

# Performance
perf(api): implement caching for dashboard metrics

# Tests
test(dashboard): add unit tests for useDashboard hook

# Breaking change
feat(api)!: change response format for dashboard metrics

BREAKING CHANGE: response now includes metadata object
```

### Regras de Commit

1. **Commits Atômicos**: Cada commit deve ter uma única responsabilidade
2. **Mensagens Descritivas**: Descrição clara do que foi alterado e por quê
3. **Presente Imperativo**: Use "add" ao invés de "added" ou "adds"
4. **Limite de Caracteres**: Primeira linha máximo 72 caracteres
5. **Corpo Explicativo**: Para mudanças complexas, inclua contexto no corpo
6. **Referências**: Inclua número da issue quando aplicável (ex: "fixes #123")

## Fluxo de Trabalho

### Para Novas Features

1. **Criar Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/nome-da-feature
   ```

2. **Desenvolvimento**
   - Fazer commits atômicos e descritivos
   - Executar testes localmente
   - Manter branch atualizada com develop

3. **Preparar Pull Request**
   ```bash
   git push origin feature/nome-da-feature
   ```
   - Criar PR para `develop`
   - Preencher template de PR
   - Solicitar revisão

4. **Após Aprovação**
   - Merge via "Squash and merge" (se múltiplos commits)
   - Deletar branch após merge

### Para Correções de Bug

1. **Identificar Severidade**
   - Bug crítico → `hotfix/` (a partir de main)
   - Bug normal → `bugfix/` (a partir de develop)

2. **Seguir Fluxo Apropriado**
   - Hotfix: merge para main E develop
   - Bugfix: merge apenas para develop

### Para Releases

1. **Criar Branch de Release**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.2.0
   ```

2. **Preparação**
   - Atualizar versão
   - Executar testes completos
   - Correções finais apenas

3. **Finalizar Release**
   ```bash
   # Merge para main
   git checkout main
   git merge release/v1.2.0
   git tag v1.2.0
   
   # Merge para develop
   git checkout develop
   git merge release/v1.2.0
   ```

## Checklist de Pull Request

### Antes de Criar PR

- [ ] Código testado localmente
- [ ] Testes unitários adicionados/atualizados
- [ ] Documentação atualizada (se necessário)
- [ ] Commits seguem padrão estabelecido
- [ ] Branch atualizada com base
- [ ] Sem conflitos de merge

### Template de PR

```markdown
## Descrição
Descreva brevemente as mudanças realizadas.

## Tipo de Mudança
- [ ] Bug fix (correção que resolve um problema)
- [ ] Nova feature (funcionalidade que adiciona algo novo)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação
- [ ] Refatoração
- [ ] Performance
- [ ] Testes

## Como Testar
1. Passo 1
2. Passo 2
3. Passo 3

## Checklist
- [ ] Código testado
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Sem warnings de lint
- [ ] Performance verificada

## Issues Relacionadas
Fixes #123
Related to #456
```

## Ferramentas de Apoio

### Git Hooks

Configurar hooks para validação automática:

```bash
# Pre-commit: validar formato de commit
# Pre-push: executar testes
# Commit-msg: validar mensagem de commit
```

### Aliases Úteis

```bash
# .gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
    graph = log --oneline --graph --decorate --all
    feature = checkout -b feature/
    bugfix = checkout -b bugfix/
    hotfix = checkout -b hotfix/
```

## Monitoramento e Métricas

### Métricas de Qualidade

- **Lead Time**: Tempo entre criação e merge do PR
- **Cycle Time**: Tempo de desenvolvimento ativo
- **Deployment Frequency**: Frequência de deploys
- **Mean Time to Recovery**: Tempo médio para correção
- **Change Failure Rate**: Taxa de falha em mudanças

### Relatórios Semanais

- Número de PRs criados/merged
- Tempo médio de revisão
- Cobertura de testes
- Número de hotfixes
- Regressões identificadas

## Troubleshooting

### Problemas Comuns

1. **Conflitos de Merge**
   ```bash
   git checkout feature/minha-feature
   git rebase develop
   # Resolver conflitos
   git rebase --continue
   ```

2. **Commit Message Incorreta**
   ```bash
   git commit --amend -m "nova mensagem"
   ```

3. **Branch Desatualizada**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/minha-feature
   git rebase develop
   ```

## Contatos e Suporte

- **Tech Lead**: [nome@empresa.com]
- **DevOps**: [devops@empresa.com]
- **Documentação**: [link-para-wiki]
- **Slack**: #glpi-dashboard-dev