# Script PowerShell para configurar ambiente de preview para testes E2E

Write-Host " Configurando Ambiente de Preview para E2E" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Função para verificar se uma porta está em uso
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Verificar e parar processos existentes
Write-Host "\n🔍 Verificando portas disponíveis..." -ForegroundColor Cyan

if (Test-Port 8000) {
    Write-Host "  Porta 8000 já está em uso" -ForegroundColor Yellow
    Write-Host "Parando processos na porta 8000..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}

if (Test-Port 3000) {
    Write-Host "⚠️  Porta 3000 já está em uso" -ForegroundColor Yellow
    Write-Host "Parando processos na porta 3000..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}

# Configurar backend
Write-Host "\n Iniciando backend em modo preview..." -ForegroundColor Cyan
Set-Location backend

# Ativar ambiente virtual se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host " Ativando ambiente virtual..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
}

# Instalar dependências
Write-Host " Instalando dependências do backend..." -ForegroundColor Cyan
pip install -r requirements.txt

# Configurar variáveis de ambiente
$env:ENVIRONMENT = "preview"
$env:DEBUG = "true"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:3001"
$env:LOG_LEVEL = "INFO"

# Iniciar backend em background
Write-Host " Iniciando servidor backend..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python main.py
}

$backendJob.Id | Out-File -FilePath "..\backend.pid" -Encoding UTF8

Set-Location ..

# Aguardar backend inicializar
Write-Host " Aguardando backend inicializar..." -ForegroundColor Cyan
Start-Sleep 5

# Verificar se backend está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ Backend rodando em http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host " Falha ao iniciar backend" -ForegroundColor Red
    exit 1
}

# Configurar frontend
Write-Host "\n Configurando frontend para preview..." -ForegroundColor Cyan
Set-Location frontend

# Instalar dependências
Write-Host "📦 Instalando dependências do frontend..." -ForegroundColor Cyan
npm ci

# Gerar cliente API
Write-Host "🔄 Gerando cliente API..." -ForegroundColor Cyan
npm run api:generate

# Configurar variáveis de ambiente
@"
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=preview
"@ | Out-File -FilePath ".env.local" -Encoding UTF8

# Iniciar frontend em background
Write-Host "🔄 Iniciando servidor frontend..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev -- --host 0.0.0.0 --port 3000
}

$frontendJob.Id | Out-File -FilePath "..\frontend.pid" -Encoding UTF8

Set-Location ..

# Aguardar frontend inicializar
Write-Host "⏳ Aguardando frontend inicializar..." -ForegroundColor Cyan
Start-Sleep 10

# Verificar se frontend está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
    Write-Host " Frontend rodando em http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host " Falha ao iniciar frontend" -ForegroundColor Red
    exit 1
}

Write-Host "\n Ambiente de preview configurado com sucesso!" -ForegroundColor Green
Write-Host " Serviços disponíveis:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "\n Para executar testes E2E:" -ForegroundColor Cyan
Write-Host "  cd frontend && npm run test:e2e" -ForegroundColor White
Write-Host "\n Para parar os serviços:" -ForegroundColor Cyan
Write-Host "  .\scripts\stop-preview.ps1" -ForegroundColor White
