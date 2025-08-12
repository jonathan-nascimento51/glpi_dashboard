# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-  **Middleware de Segurança**: Implementação de headers HTTP de segurança
  - X-Frame-Options para proteção contra clickjacking
  - Content-Security-Policy configurável via variáveis de ambiente
  - X-Content-Type-Options para prevenção de MIME sniffing
  - X-XSS-Protection para ativação da proteção XSS do browser
  - Referrer-Policy para controle de informações de referrer
  - Permissions-Policy para controle de APIs do browser
  - Strict-Transport-Security para forçar HTTPS
  - Header Server customizado para ocultar informações do servidor

-  **Análise Estática de Segurança (SAST)**:
  - Bandit para análise de segurança em código Python
  - Semgrep para detecção de padrões inseguros
  - Safety para verificação de vulnerabilidades em dependências
  - Configuração personalizada em `bandit.yaml`

-  **Detecção de Segredos**:
  - GitLeaks com regras customizadas para tokens GLPI
  - TruffleHog para verificação de segredos em repositório
  - Configuração detalhada em `.gitleaks.toml`
  - Regras específicas para:
    - Tokens e chaves de API GLPI
    - URLs de conexão de banco de dados
    - Chaves secretas e JWT
    - DSNs do Sentry
    - Tokens do Unleash

-  **CI/CD de Segurança**:
  - Workflow GitHub Actions para verificações automáticas
  - Jobs separados para secret scanning, SAST e dependency check
  - Execução em push, pull requests e agendamento diário
  - Upload de relatórios como artefatos
  - Verificação de dependências Python e Node.js

-  **Ferramentas e Scripts**:
  - Makefile com comandos de segurança (`make security`, `make security-quick`)
  - Script Python `scripts/security_check.py` para validação local
  - Pre-commit hooks para verificações automáticas
  - Comandos individuais para cada ferramenta de segurança

-  **Configurações**:
  - Classe `SecurityConfig` em `config/security.py`
  - Variáveis de ambiente para configuração de CSP
  - Template `.env.example` atualizado com configurações de segurança
  - Middleware integrado ao FastAPI em `main.py`

-  **Documentação**:
  - Documentação completa de segurança em `SECURITY.md`
  - Seção de segurança adicionada ao `README.md`
  - Configuração de pre-commit hooks em `.pre-commit-config.yaml`
  - Este arquivo CHANGELOG.md

### Security
- Implementação de múltiplas camadas de proteção contra vulnerabilidades OWASP Top 10
- Detecção automática de credenciais e segredos em commits
- Análise contínua de dependências para vulnerabilidades conhecidas
- Headers de segurança para proteção contra ataques web comuns
- Pipeline de segurança integrado ao processo de desenvolvimento

### Changed
- Atualização do `main.py` para incluir middleware de segurança
- Expansão do `.env.example` com variáveis de configuração de segurança
- Estrutura do projeto organizada com diretórios `middleware/` e `config/`

### Technical Details
- **Arquivos criados**:
  - `backend/middleware/security.py` - Middleware de headers de segurança
  - `backend/middleware/__init__.py` - Inicialização do pacote middleware
  - `backend/config/security.py` - Configurações centralizadas de segurança
  - `.github/workflows/security.yml` - Pipeline de segurança CI/CD
  - `bandit.yaml` - Configuração do Bandit
  - `.gitleaks.toml` - Configuração do GitLeaks
  - `.pre-commit-config.yaml` - Hooks de pre-commit
  - `scripts/security_check.py` - Script de validação local
  - `Makefile` - Comandos de automação
  - `SECURITY.md` - Documentação de segurança
  - `CHANGELOG.md` - Este arquivo

- **Arquivos modificados**:
  - `backend/main.py` - Integração do middleware de segurança
  - `.env.example` - Adição de variáveis de segurança
  - `README.md` - Seção de segurança

### Dependencies
- Nenhuma nova dependência Python adicionada (uso de bibliotecas padrão)
- Ferramentas de segurança configuradas para instalação via pip/npm
- Pre-commit hooks gerenciados automaticamente

---

## Versões Anteriores

### [1.0.0] - Data anterior
- Versão inicial do projeto GLPI Dashboard
- Implementação básica da API FastAPI
- Interface Dash/Plotly para visualização
- Integração com GLPI via API REST

---

**Formato de Versionamento**: [MAJOR.MINOR.PATCH]
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Funcionalidades adicionadas de forma compatível
- **PATCH**: Correções de bugs compatíveis

**Categorias de Mudanças**:
- `Added` para novas funcionalidades
- `Changed` para mudanças em funcionalidades existentes
- `Deprecated` para funcionalidades que serão removidas
- `Removed` para funcionalidades removidas
- `Fixed` para correções de bugs
- `Security` para correções de vulnerabilidades
