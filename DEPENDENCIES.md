# Gerenciamento de Dependências

Este documento descreve a rotina de atualização de dependências e builds reprodutíveis para o projeto GLPI Dashboard.

## Estrutura de Dependências

### Backend (Python)
- **Arquivo principal**: `backend/requirements.txt`
- **Lockfile**: `backend/requirements.lock` (com hashes SHA256)
- **Ferramenta**: `pip-tools` (pip-compile)

### Frontend (Node.js)
- **Arquivo principal**: `frontend/package.json`
- **Lockfile**: `frontend/package-lock.json`
- **Ferramenta**: `npm`

### Projeto Raiz (Python)
- **Arquivo principal**: `pyproject.toml`
- **Ferramenta**: `uv` ou `pip`

## Scripts de Build

### Backend
- **Linux/macOS**: `backend/build.sh`
- **Windows**: `backend/build.ps1`

### Frontend
- **Linux/macOS**: `frontend/build.sh`
- **Windows**: `frontend/build.ps1`

## Rotina de Atualização de Dependências

### 1. Preparação
```bash
# Criar branch para atualizações
git checkout -b deps/DEPS-XX-atualizacao-dependencias
```

### 2. Backend (Python)
```bash
cd backend

# Instalar pip-tools se necessário
pip install pip-tools

# Gerar lockfile com hashes
pip-compile requirements.txt --generate-hashes --output-file requirements.lock

# Instalar dependências
pip install -r requirements.lock

# Executar build e testes
./build.sh  # ou build.ps1 no Windows
```

### 3. Frontend (Node.js)
```bash
cd frontend

# Instalar dependências e gerar lockfile
npm install

# Auditoria de segurança
npm audit

# Executar build e testes
./build.sh  # ou build.ps1 no Windows
```

### 4. Validação
- Executar todos os testes
- Verificar builds locais
- Validar funcionalidades críticas
- Revisar relatórios de segurança

## Builds Reprodutíveis

### Características
- **Lockfiles com hashes**: Garantem integridade das dependências
- **Versões fixas**: Evitam surpresas em diferentes ambientes
- **Scripts padronizados**: Mesma sequência de build em qualquer ambiente
- **Auditoria de segurança**: Verificação automática de vulnerabilidades

### Benefícios
- Builds consistentes entre desenvolvimento, CI/CD e produção
- Detecção precoce de problemas de dependências
- Facilita debugging e rollback
- Melhora a segurança do projeto

## Troubleshooting

### Problemas Comuns

#### Backend
- **Erro de versão não encontrada**: Verificar se a versão existe no PyPI
- **Conflitos de dependências**: Usar `pip-compile --upgrade` para resolver
- **Hashes inválidos**: Regenerar o lockfile

#### Frontend
- **Vulnerabilidades**: Executar `npm audit fix` (cuidado com breaking changes)
- **Dependências desatualizadas**: Usar `npm outdated` para verificar
- **Conflitos de versão**: Limpar `node_modules` e reinstalar

### Comandos Úteis

```bash
# Backend - verificar dependências desatualizadas
pip list --outdated

# Frontend - verificar dependências desatualizadas
npm outdated

# Limpar caches
pip cache purge
npm cache clean --force
```

## Checklist de Atualização

- [ ] Branch criado para atualizações
- [ ] Backend: requirements.lock gerado com hashes
- [ ] Frontend: package-lock.json atualizado
- [ ] Scripts de build executados com sucesso
- [ ] Testes passando
- [ ] Auditoria de segurança revisada
- [ ] Documentação atualizada
- [ ] PR criado com checklist de qualidade

## Frequência Recomendada

- **Dependências críticas de segurança**: Imediatamente
- **Dependências principais**: Mensalmente
- **Dependências de desenvolvimento**: Trimestralmente
- **Auditoria completa**: Semestralmente
