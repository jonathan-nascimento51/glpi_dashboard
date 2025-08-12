# Documentação de Segurança - GLPI Dashboard

##  Visão Geral

Este documento descreve as implementações de segurança aplicadas ao projeto GLPI Dashboard para garantir a proteção contra vulnerabilidades comuns e seguir as melhores práticas de segurança.

##  Índice

1. [Headers de Segurança](#headers-de-segurança)
2. [Middleware de Segurança](#middleware-de-segurança)
3. [Configurações de Segurança](#configurações-de-segurança)
4. [Análise Estática de Segurança (SAST)](#análise-estática-de-segurança-sast)
5. [Detecção de Segredos](#detecção-de-segredos)
6. [CI/CD de Segurança](#cicd-de-segurança)
7. [Comandos e Scripts](#comandos-e-scripts)
8. [Configurações de Ambiente](#configurações-de-ambiente)

##  Headers de Segurança

### Headers Implementados

O middleware de segurança adiciona automaticamente os seguintes headers HTTP:

| Header | Valor | Descrição |
|--------|-------|----------|
| `X-Frame-Options` | `DENY` | Previne ataques de clickjacking |
| `X-Content-Type-Options` | `nosniff` | Previne MIME type sniffing |
| `X-XSS-Protection` | `1; mode=block` | Ativa proteção XSS do browser |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controla informações de referrer |
| `Permissions-Policy` | Restritiva | Controla APIs do browser |
| `Server` | `GLPI-Dashboard` | Oculta informações do servidor |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Força HTTPS (apenas em HTTPS) |
| `Content-Security-Policy` | Configurável | Previne XSS e injeção de código |

### Content Security Policy (CSP)

O CSP é configurável através de variáveis de ambiente:

```env
CSP_DEFAULT_SRC="\'self\'"
CSP_SCRIPT_SRC="\'self\' \'unsafe-inline\' https://cdn.plot.ly"
CSP_STYLE_SRC="\'self\' \'unsafe-inline\' https://fonts.googleapis.com"
CSP_IMG_SRC="\'self\' data: https:"
CSP_CONNECT_SRC="\'self\' https://api.glpi.example.com"
```

##  Middleware de Segurança

### Localização
- **Arquivo**: `backend/middleware/security.py`
- **Classe**: `SecurityHeadersMiddleware`

### Integração

O middleware é automaticamente integrado no FastAPI através do `main.py`:

```python
from middleware.security import SecurityHeadersMiddleware

# Adicionar middleware de segurança
if os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true":
    app.add_middleware(SecurityHeadersMiddleware)
```

### Configuração

Habilitar/desabilitar através da variável de ambiente:

```env
SECURITY_HEADERS_ENABLED=true
```

##  Configurações de Segurança

### Arquivo de Configuração
- **Localização**: `backend/config/security.py`
- **Classe**: `SecurityConfig`

### Configurações Disponíveis

```python
class SecurityConfig:
    # CORS
    CORS_ORIGINS: List[str]
    
    # Headers de Segurança
    SECURITY_HEADERS_ENABLED: bool
    CSP_DEFAULT_SRC: str
    CSP_SCRIPT_SRC: str
    CSP_STYLE_SRC: str
    CSP_IMG_SRC: str
    CSP_CONNECT_SRC: str
    
    # Chaves e Segredos
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    
    # Ambiente
    IS_DEVELOPMENT: bool
    ALLOWED_HOSTS: List[str]
```

##  Análise Estática de Segurança (SAST)

### Ferramentas Implementadas

#### 1. Bandit
- **Propósito**: Análise de segurança para código Python
- **Configuração**: `bandit.yaml`
- **Comando**: `make security-bandit`

#### 2. Semgrep
- **Propósito**: Análise de padrões de segurança
- **Configuração**: Regras automáticas
- **Comando**: `make security-semgrep`

#### 3. Safety
- **Propósito**: Verificação de vulnerabilidades em dependências
- **Comando**: `make security-safety`

### Configuração do Bandit

O arquivo `bandit.yaml` contém:
- Testes de segurança habilitados
- Exclusões para falsos positivos
- Configurações de severidade
- Diretórios excluídos

##  Detecção de Segredos

### Ferramentas Implementadas

#### 1. GitLeaks
- **Configuração**: `.gitleaks.toml`
- **Comando**: `make security-gitleaks`
- **Regras customizadas** para:
  - Tokens GLPI
  - Chaves de API
  - Strings de conexão de banco
  - URLs do Redis
  - Chaves JWT
  - DSNs do Sentry

#### 2. TruffleHog
- **Integração**: GitHub Actions e pre-commit
- **Verificação**: Apenas segredos verificados

### Configuração do GitLeaks

Regras customizadas em `.gitleaks.toml`:

```toml
[[rules]]
id = "glpi-token"
description = "GLPI API Token"
regex = '''(?i)(glpi[_-]?token|glpi[_-]?key)[\s]*[=:][\s]*["'']?([a-zA-Z0-9_\-]{20,})["'']?'''
keywords = ["glpi_token", "glpi_key", "glpi-token"]
```

##  CI/CD de Segurança

### GitHub Actions

**Arquivo**: `.github/workflows/security.yml`

#### Jobs Implementados:

1. **secret-scan**
   - TruffleHog OSS
   - GitLeaks

2. **sast-scan**
   - Bandit
   - Safety
   - Semgrep

3. **dependency-check**
   - pip-audit (Python)
   - npm audit (Node.js)

#### Triggers:
- Push para `main` e `develop`
- Pull Requests
- Execução diária às 2:00 AM UTC

### Relatórios

Todos os jobs geram:
- Relatórios JSON como artefatos
- Comentários automáticos em PRs
- Resumos de segurança

##  Comandos e Scripts

### Makefile

Comandos disponíveis:

```bash
# Segurança completa
make security

# Verificação rápida
make security-quick

# Ferramentas individuais
make security-bandit
make security-safety
make security-gitleaks
make security-semgrep

# Pre-commit hooks
make pre-commit

# Validação completa
make validate  # lint + test + security-quick
make ci        # pipeline completa de CI
```

### Script Python

**Arquivo**: `scripts/security_check.py`

```bash
# Verificação completa
python scripts/security_check.py

# Modo rápido
python scripts/security_check.py --quick
```

#### Funcionalidades:
- Verificação de dependências
- Execução de todas as ferramentas
- Geração de relatórios consolidados
- Resumo visual dos resultados

### Pre-commit Hooks

**Arquivo**: `.pre-commit-config.yaml`

Hooks configurados:
- Formatação (black, isort)
- Linting (ruff)
- Segurança (bandit, safety, semgrep)
- Detecção de segredos (gitleaks, trufflehog)
- Verificação de Dockerfile (hadolint)
- Verificação de YAML (yamllint)

##  Configurações de Ambiente

### Arquivo .env.example

Template limpo com todas as variáveis necessárias:

```env
# === AMBIENTE ===
FLASK_ENV=development
DEBUG=false

# === GLPI ===
GLPI_URL=https://glpi.example.com/apirest.php
GLPI_APP_TOKEN=your_app_token_here
GLPI_USER_TOKEN=your_user_token_here

# === SEGURANÇA ===
SECURITY_HEADERS_ENABLED=true
CSP_DEFAULT_SRC="\'self\'"
CSP_SCRIPT_SRC="\'self\' \'unsafe-inline\' https://cdn.plot.ly"
CSP_STYLE_SRC="\'self\' \'unsafe-inline\' https://fonts.googleapis.com"
CSP_IMG_SRC="\'self\' data: https:"
CSP_CONNECT_SRC="\'self\' https://api.glpi.example.com"

# === CHAVES SECRETAS ===
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
```

##  Relatórios de Segurança

### Localização
- **Diretório**: `security_reports/`
- **Arquivos**:
  - `bandit_report.json`
  - `safety_report.json`
  - `semgrep_report.json`
  - `gitleaks_report.json`
  - `security_summary.json`

### Formato do Resumo

```json
{
  "timestamp": "2024-01-15 10:30:00",
  "reports": [
    {
      "tool": "bandit",
      "issues_found": 0,
      "report_file": "security_reports/bandit_report.json"
    }
  ]
}
```

##  Fluxo de Trabalho

### Desenvolvimento Local

1. **Antes do commit**:
   ```bash
   make security-quick  # Verificação rápida
   make pre-commit      # Hooks do pre-commit
   ```

2. **Antes do push**:
   ```bash
   make security        # Verificação completa
   make validate        # Lint + test + security
   ```

### Pipeline CI/CD

1. **Pull Request**:
   - Execução automática de todos os scans
   - Comentários com resumo de segurança
   - Artefatos com relatórios detalhados

2. **Merge para main**:
   - Verificação completa de segurança
   - Atualização de relatórios
   - Deploy apenas se todos os checks passarem

##  Tratamento de Vulnerabilidades

### Processo de Resposta

1. **Detecção**:
   - Alertas automáticos via CI/CD
   - Verificações diárias agendadas
   - Monitoramento contínuo

2. **Avaliação**:
   - Classificação de severidade
   - Análise de impacto
   - Priorização de correção

3. **Correção**:
   - Criação de branch de segurança
   - Implementação de fix
   - Testes de regressão
   - Deploy prioritário

### Severidades

- **CRITICAL**: Correção imediata (< 24h)
- **HIGH**: Correção urgente (< 72h)
- **MEDIUM**: Correção planejada (< 1 semana)
- **LOW**: Correção em próxima release

##  Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [GitLeaks Documentation](https://github.com/zricethezav/gitleaks)
- [Semgrep Rules](https://semgrep.dev/explore)

##  Contribuição

Para contribuir com melhorias de segurança:

1. Crie uma branch `sec/SEC-XX-descricao`
2. Implemente as melhorias
3. Execute `make security` para validar
4. Abra um Pull Request
5. Aguarde review de segurança

---

**Última atualização**: Janeiro 2024  
**Versão**: 1.0.0  
**Responsável**: Equipe de Segurança
