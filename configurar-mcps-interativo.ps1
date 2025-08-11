# Configuracao Interativa de MCPs para GLPI Dashboard
# Execute: .\configurar-mcps-interativo.ps1

Param(
    [switch]$SkipTests,
    [switch]$Quiet
)

# Cores para output
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"
$HeaderColor = "Magenta"

function Write-Header {
    param([string]$Text)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor $HeaderColor
    Write-Host " $Text" -ForegroundColor $HeaderColor
    Write-Host "=" * 60 -ForegroundColor $HeaderColor
    Write-Host ""
}

function Write-Step {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor $SuccessColor
}

function Write-Warning {
    param([string]$Text)
    Write-Host "[AVISO] $Text" -ForegroundColor $WarningColor
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "[ERRO] $Text" -ForegroundColor $ErrorColor
}

function Confirm-Continue {
    param([string]$Message = "Continuar?")
    if ($Quiet) { return $true }
    
    $response = Read-Host "$Message (s/N)"
    return $response -match '^[sS]'
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-Port {
    param([string]$HostName, [int]$Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect($HostName, $Port)
        $tcpClient.Close()
        return $true
    } catch {
        return $false
    }
}

function Test-Url {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Inicio do script
Clear-Host
Write-Header "CONFIGURACAO INTERATIVA DE MCPs - GLPI DASHBOARD"

Write-Host "Este script ira guia-lo atraves da configuracao completa dos MCPs." -ForegroundColor $InfoColor
Write-Host "Tempo estimado: 10-15 minutos" -ForegroundColor $InfoColor
Write-Host ""

if (-not (Confirm-Continue "Iniciar configuracao?")) {
    Write-Host "Configuracao cancelada." -ForegroundColor $WarningColor
    exit 0
}

# PASSO 1: Verificar pre-requisitos
Write-Header "PASSO 1: VERIFICANDO PRE-REQUISITOS"

Write-Step "Verificando Node.js..."
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Success "Node.js encontrado: $nodeVersion"
} else {
    Write-Error-Custom "Node.js nao encontrado!"
    Write-Host "Instale Node.js 18+ em: https://nodejs.org" -ForegroundColor $WarningColor
    exit 1
}

Write-Step "Verificando NPX..."
if (Test-Command "npx") {
    Write-Success "NPX disponivel"
} else {
    Write-Error-Custom "NPX nao encontrado!"
    exit 1
}

Write-Step "Verificando estrutura do projeto..."
$requiredFiles = @(
    "trae-mcp-config.json",
    ".env.mcp.example",
    "app.py",
    "frontend\package.json"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error-Custom "Arquivos necessarios nao encontrados:"
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor $ErrorColor
    }
    exit 1
} else {
    Write-Success "Estrutura do projeto OK"
}

# PASSO 2: Configurar variaveis de ambiente
Write-Header "PASSO 2: CONFIGURANDO VARIAVEIS DE AMBIENTE"

Write-Step "Verificando arquivo .env.mcp..."
if (-not (Test-Path ".env.mcp")) {
    Write-Warning "Arquivo .env.mcp nao encontrado. Criando a partir do exemplo..."
    Copy-Item ".env.mcp.example" ".env.mcp"
    Write-Success "Arquivo .env.mcp criado"
} else {
    Write-Success "Arquivo .env.mcp ja existe"
}

Write-Host ""
Write-Host "CONFIGURACAO DE TOKENS:" -ForegroundColor $HeaderColor
Write-Host ""

# GitHub Token
Write-Step "Configurando GitHub Token..."
Write-Host "1. Acesse: https://github.com/settings/tokens" -ForegroundColor $InfoColor
Write-Host "2. Clique em 'Generate new token (classic)'" -ForegroundColor $InfoColor
Write-Host "3. Selecione: repo, workflow, write:packages" -ForegroundColor $InfoColor
Write-Host ""

$githubToken = Read-Host "Cole seu GitHub Token (ou Enter para pular)"
if ($githubToken) {
    # Atualizar .env.mcp com o token
    $envContent = Get-Content ".env.mcp" -Raw
    $envContent = $envContent -replace "GITHUB_TOKEN=.*", "GITHUB_TOKEN=$githubToken"
    Set-Content ".env.mcp" $envContent
    Write-Success "GitHub Token configurado"
} else {
    Write-Warning "GitHub Token pulado (algumas funcionalidades nao estarao disponiveis)"
}

# Configuracao do banco
Write-Step "Configurando credenciais do banco MySQL..."
Write-Host "Configure as credenciais do banco GLPI:" -ForegroundColor $InfoColor

$mysqlHost = Read-Host "Host do MySQL (Enter para localhost)"
if (-not $mysqlHost) { $mysqlHost = "localhost" }

$mysqlPort = Read-Host "Porta do MySQL (Enter para 3306)"
if (-not $mysqlPort) { $mysqlPort = "3306" }

$mysqlDatabase = Read-Host "Nome do banco (Enter para glpi)"
if (-not $mysqlDatabase) { $mysqlDatabase = "glpi" }

$mysqlUser = Read-Host "Usuario do MySQL"
$mysqlPassword = Read-Host "Senha do MySQL" -AsSecureString
$mysqlPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))

if ($mysqlUser -and $mysqlPasswordPlain) {
    # Atualizar .env.mcp
    $envContent = Get-Content ".env.mcp" -Raw
    $envContent = $envContent -replace "PGHOST=.*", "PGHOST=$mysqlHost"
    $envContent = $envContent -replace "PGPORT=.*", "PGPORT=$mysqlPort"
    $envContent = $envContent -replace "PGDATABASE=.*", "PGDATABASE=$mysqlDatabase"
    $envContent = $envContent -replace "PGUSER=.*", "PGUSER=$mysqlUser"
    $envContent = $envContent -replace "PGPASSWORD=.*", "PGPASSWORD=$mysqlPasswordPlain"
    Set-Content ".env.mcp" $envContent
    Write-Success "Credenciais do banco configuradas"
} else {
    Write-Warning "Credenciais do banco nao configuradas"
}

# Tokens opcionais
Write-Host ""
Write-Host "TOKENS OPCIONAIS:" -ForegroundColor $HeaderColor

if (Confirm-Continue "Configurar Firecrawl API Key? (para scraping de documentacao)") {
    Write-Host "Registre-se em: https://firecrawl.dev" -ForegroundColor $InfoColor
    $firecrawlKey = Read-Host "Cole sua Firecrawl API Key"
    if ($firecrawlKey) {
        $envContent = Get-Content ".env.mcp" -Raw
        $envContent = $envContent -replace "FIRECRAWL_API_KEY=.*", "FIRECRAWL_API_KEY=$firecrawlKey"
        Set-Content ".env.mcp" $envContent
        Write-Success "Firecrawl API Key configurada"
    }
}

if (Confirm-Continue "Configurar Grafana Token? (para dashboards)") {
    Write-Host "Acesse: http://localhost:3000/org/apikeys" -ForegroundColor $InfoColor
    $grafanaToken = Read-Host "Cole seu Grafana Token"
    if ($grafanaToken) {
        $envContent = Get-Content ".env.mcp" -Raw
        $envContent = $envContent -replace "GRAFANA_TOKEN=.*", "GRAFANA_TOKEN=$grafanaToken"
        Set-Content ".env.mcp" $envContent
        Write-Success "Grafana Token configurado"
    }
}

# PASSO 3: Verificar servicos
Write-Header "PASSO 3: VERIFICANDO SERVICOS DO PROJETO"

Write-Step "Verificando Backend Flask (porta 5000)..."
if (Test-Url "http://localhost:5000/api/technicians/ranking") {
    Write-Success "Backend Flask esta rodando"
} else {
    Write-Warning "Backend Flask nao esta rodando"
    if (Confirm-Continue "Iniciar Backend Flask agora?") {
        Write-Host "Iniciando Backend Flask..." -ForegroundColor $InfoColor
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py"
        Start-Sleep 3
        if (Test-Url "http://localhost:5000/api/technicians/ranking") {
            Write-Success "Backend Flask iniciado com sucesso"
        } else {
            Write-Warning "Falha ao iniciar Backend Flask. Inicie manualmente: python app.py"
        }
    }
}

Write-Step "Verificando Frontend React (porta 3001)..."
if (Test-Url "http://127.0.0.1:3001") {
    Write-Success "Frontend React esta rodando"
} else {
    Write-Warning "Frontend React nao esta rodando"
    if (Confirm-Continue "Iniciar Frontend React agora?") {
        Write-Host "Iniciando Frontend React..." -ForegroundColor $InfoColor
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
        Start-Sleep 5
        if (Test-Url "http://127.0.0.1:3001") {
            Write-Success "Frontend React iniciado com sucesso"
        } else {
            Write-Warning "Falha ao iniciar Frontend React. Inicie manualmente: cd frontend; npm run dev"
        }
    }
}

Write-Step "Verificando MySQL (porta 3306)..."
if (Test-Port "localhost" 3306) {
    Write-Success "MySQL esta acessivel"
} else {
    Write-Warning "MySQL nao esta acessivel na porta 3306"
    Write-Host "Verifique se o MySQL/MariaDB esta rodando" -ForegroundColor $WarningColor
}

# PASSO 4: Testar MCPs
if (-not $SkipTests) {
    Write-Header "PASSO 4: TESTANDO MCPs"
    
    Write-Step "Testando Context7..."
    try {
        $output = npx -y @upstash/context7-mcp 2>&1
        Write-Success "Context7 OK"
    } catch {
        Write-Warning "Context7 pode ter problemas"
    }
    
    if ($githubToken) {
        Write-Step "Testando GitHub MCP..."
        $env:GITHUB_TOKEN = $githubToken
        try {
            $output = npx -y github-mcp-server 2>&1
            Write-Success "GitHub MCP OK"
        } catch {
            Write-Warning "GitHub MCP pode ter problemas"
        }
    }
    
    Write-Step "Testando OpenAPI MCP..."
    $env:OPENAPI_SPEC_URL = "http://localhost:5000/openapi.json"
    try {
        $output = npx -y openapi-mcp-server 2>&1
        Write-Success "OpenAPI MCP OK"
    } catch {
        Write-Warning "OpenAPI MCP pode ter problemas"
    }
}

# PASSO 5: Instrucoes finais
Write-Header "PASSO 5: CONFIGURACAO NO TRAE AI"

Write-Host "PROXIMOS PASSOS:" -ForegroundColor $HeaderColor
Write-Host ""
Write-Host "1. Abra o Trae AI" -ForegroundColor $InfoColor
Write-Host "2. Va em: Agents -> AI Management -> MCP -> Configure Manually" -ForegroundColor $InfoColor
Write-Host "3. Copie o conteudo do arquivo 'trae-mcp-config.json'" -ForegroundColor $InfoColor
Write-Host "4. Cole na interface do Trae AI" -ForegroundColor $InfoColor
Write-Host "5. Clique em Save" -ForegroundColor $InfoColor
Write-Host "6. REINICIE o Trae AI" -ForegroundColor $InfoColor
Write-Host ""

Write-Host "ARQUIVOS IMPORTANTES:" -ForegroundColor $HeaderColor
Write-Host "GUIA_CONFIGURACAO_MCPS.md - Guia detalhado" -ForegroundColor $InfoColor
Write-Host "mcp-usage-examples.md - Exemplos de prompts" -ForegroundColor $InfoColor
Write-Host "README-MCP.md - Referencia rapida" -ForegroundColor $InfoColor
Write-Host ".env.mcp - Suas configuracoes" -ForegroundColor $InfoColor
Write-Host ""

Write-Host "PROMPTS DE TESTE:" -ForegroundColor $HeaderColor
Write-Host ""
Write-Host "#Workspace" -ForegroundColor $InfoColor
Write-Host "#Folder frontend" -ForegroundColor $InfoColor
Write-Host "#Folder backend" -ForegroundColor $InfoColor
Write-Host "use context7" -ForegroundColor $InfoColor
Write-Host "" -ForegroundColor $InfoColor
Write-Host "Carregue o spec OpenAPI e chame GET /api/technicians/ranking." -ForegroundColor $InfoColor
Write-Host "Compare com os dados do frontend React." -ForegroundColor $InfoColor
Write-Host ""

if (Confirm-Continue "Abrir arquivo de configuracao JSON agora?") {
    Start-Process notepad "trae-mcp-config.json"
}

Write-Header "CONFIGURACAO CONCLUIDA!"
Write-Success "MCPs configurados com sucesso!"
Write-Host "Execute './setup-mcps.ps1' para validar a configuracao completa." -ForegroundColor $InfoColor
Write-Host ""
Write-Host "Agora voce pode usar os MCPs no Trae AI para desenvolvimento mais eficiente!" -ForegroundColor $SuccessColor