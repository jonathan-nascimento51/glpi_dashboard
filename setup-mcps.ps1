# 🤖 Script de Configuração Automática dos MCPs - GLPI Dashboard
# Executa: PowerShell -ExecutionPolicy Bypass -File setup-mcps.ps1

Write-Host "🚀 Configurando MCPs para Trae AI - GLPI Dashboard" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray

# Verificar Node.js
Write-Host "📦 Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado. Instale em: https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Verificar NPX
Write-Host "📦 Verificando NPX..." -ForegroundColor Yellow
try {
    $npxVersion = npx --version
    Write-Host "✅ NPX encontrado: $npxVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ NPX não encontrado. Instale Node.js mais recente." -ForegroundColor Red
    exit 1
}

# Testar MCPs individualmente
Write-Host "`n🧪 Testando MCPs..." -ForegroundColor Yellow

# Array de MCPs para testar
$mcps = @(
    @{name="Context7"; package="@upstash/context7-mcp"},
    @{name="Filesystem"; package="@modelcontextprotocol/server-filesystem"},
    @{name="GitHub"; package="github-mcp-server"},
    @{name="Firecrawl"; package="firecrawl-mcp"},
    @{name="OpenAPI"; package="openapi-mcp-server"},
    @{name="PostgreSQL"; package="mcp-postgres"},
    @{name="Prometheus"; package="prometheus-mcp-server"},
    @{name="Grafana"; package="grafana-mcp"}
)

$successCount = 0
$failedMcps = @()

foreach ($mcp in $mcps) {
    Write-Host "  🔍 Testando $($mcp.name)..." -ForegroundColor Cyan
    
    try {
        # Timeout de 30 segundos para cada teste
        $job = Start-Job -ScriptBlock {
            param($package)
            npx -y $package --help 2>&1
        } -ArgumentList $mcp.package
        
        $result = Wait-Job $job -Timeout 30
        $output = Receive-Job $job
        Remove-Job $job -Force
        
        if ($result) {
            Write-Host "    ✅ $($mcp.name) OK" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "    ⚠️  $($mcp.name) Timeout" -ForegroundColor Yellow
            $failedMcps += $mcp.name
        }
    } catch {
        Write-Host "    ❌ $($mcp.name) Falhou: $($_.Exception.Message)" -ForegroundColor Red
        $failedMcps += $mcp.name
    }
}

Write-Host "`n📊 Resultado dos Testes:" -ForegroundColor Yellow
Write-Host "  ✅ Sucessos: $successCount/$($mcps.Count)" -ForegroundColor Green
if ($failedMcps.Count -gt 0) {
    Write-Host "  ❌ Falhas: $($failedMcps -join ', ')" -ForegroundColor Red
}

# Verificar serviços locais
Write-Host "`n🔍 Verificando serviços locais..." -ForegroundColor Yellow

# Verificar Backend Flask (GLPI Dashboard)
Write-Host "  🐍 Verificando Backend Flask (localhost:5000)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/technicians/ranking" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    ✅ Backend Flask OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️  Backend Flask não encontrado em localhost:5000" -ForegroundColor Yellow
    Write-Host "    💡 Inicie com: python app.py" -ForegroundColor Gray
}

# Verificar Frontend React (GLPI Dashboard)
Write-Host "  ⚛️  Verificando Frontend React (localhost:3001)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:3001" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    ✅ Frontend React OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️  Frontend React não encontrado em localhost:3001" -ForegroundColor Yellow
    Write-Host "    💡 Inicie com: cd frontend && npm run dev" -ForegroundColor Gray
}

# Verificar OpenAPI endpoint (Flask)
Write-Host "  📋 Verificando OpenAPI endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/openapi.json" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    ✅ OpenAPI endpoint OK" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️  OpenAPI endpoint não encontrado" -ForegroundColor Yellow
    Write-Host "    💡 Verifique se Flask-RESTX está configurado" -ForegroundColor Gray
}

# Verificar banco MySQL (GLPI)
Write-Host "  🗄️  Verificando conexão MySQL (porta 3306)..." -ForegroundColor Cyan
try {
    # Teste básico de conectividade na porta
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 3306)
    $tcpClient.Close()
    Write-Host "    ✅ MySQL: Porta 3306 acessível" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️  MySQL: Porta 3306 inacessível" -ForegroundColor Red
    Write-Host "    💡 Verifique se o MySQL/MariaDB está rodando" -ForegroundColor Gray
}

# Verificar Prometheus (opcional)
Write-Host "  📊 Verificando Prometheus (localhost:9090)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    ✅ Prometheus OK" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️  Prometheus não encontrado (opcional)" -ForegroundColor Yellow
}

# Verificar Grafana (opcional)
Write-Host "  📈 Verificando Grafana (localhost:3000)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    ✅ Grafana OK" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️  Grafana não encontrado (opcional)" -ForegroundColor Yellow
}

# Gerar relatório de configuração
Write-Host "`n📋 Gerando relatório de configuração..." -ForegroundColor Yellow

$reportPath = "./mcp-setup-report.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$report = @"
🤖 Relatório de Configuração MCPs - GLPI Dashboard
Gerado em: $timestamp

📦 MCPs Testados:
"

foreach ($mcp in $mcps) {
    $status = if ($failedMcps -contains $mcp.name) { "❌ FALHOU" } else { "✅ OK" }
    $report += "  $status $($mcp.name) ($($mcp.package))`n"
}

$report += @"

🔧 Próximos Passos:

1. Configure tokens no arquivo trae-mcp-config.json:
   - GITHUB_TOKEN: Gere em GitHub → Settings → Developer settings → Personal access tokens
   - FIRECRAWL_API_KEY: Registre-se em firecrawl.dev
   - GRAFANA_TOKEN: Acesse Grafana → Configuration → API Keys

2. Ajuste configurações do projeto:
   - Verifique credenciais do banco de dados
   - Configure OpenAPI no Flask backend
   - Inicie serviços necessários

3. Cole a configuração no Trae AI:
   - Vá em Agents → ⚙️ AI Management → MCP → Configure Manually
   - Cole o conteúdo de trae-mcp-config.json

4. Teste com prompts de exemplo:
   - Consulte mcp-usage-examples.md
   - Inicie sempre com: #Workspace #Folder frontend #Folder backend use context7

📚 Documentação:
   - TRAE_MCP_SETUP.md: Guia completo
   - mcp-usage-examples.md: Prompts práticos
   - trae-mcp-config.json: Configuração para colar no Trae

"@

$report | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "📄 Relatório salvo em: $reportPath" -ForegroundColor Green

# Resumo final
Write-Host "`n🎯 Resumo Final:" -ForegroundColor Yellow
Write-Host "=" * 40 -ForegroundColor Gray

if ($successCount -eq $mcps.Count) {
    Write-Host "🎉 Todos os MCPs foram testados com sucesso!" -ForegroundColor Green
    Write-Host "📋 Próximo passo: Configure tokens e cole a configuração no Trae AI" -ForegroundColor Cyan
} elseif ($successCount -gt ($mcps.Count / 2)) {
    Write-Host "⚠️  Maioria dos MCPs OK, mas alguns falharam" -ForegroundColor Yellow
    Write-Host "📋 Verifique os MCPs que falharam e suas dependências" -ForegroundColor Cyan
} else {
    Write-Host "❌ Muitos MCPs falharam" -ForegroundColor Red
    Write-Host "📋 Verifique sua conexão de internet e versão do Node.js" -ForegroundColor Cyan
}

Write-Host "`n📚 Consulte os arquivos de documentação criados:" -ForegroundColor Gray
Write-Host "   - TRAE_MCP_SETUP.md" -ForegroundColor White
Write-Host "   - mcp-usage-examples.md" -ForegroundColor White
Write-Host "   - trae-mcp-config.json" -ForegroundColor White
Write-Host "   - $reportPath" -ForegroundColor White

Write-Host "`n✨ Configuração concluída!" -ForegroundColor Green