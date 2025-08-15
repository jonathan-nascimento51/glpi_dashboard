# Script interativo para atualizar tokens GLPI
Write-Host "=== ATUALIZAÇÃO INTERATIVA DE TOKENS GLPI ===" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE: Certifique-se de ter gerado novos tokens no GLPI antes de continuar!" -ForegroundColor Yellow
Write-Host "URL do GLPI: http://cau.ppiratini.intra.rs.gov.br/glpi" -ForegroundColor Cyan
Write-Host ""

# Solicitar novo App Token
Write-Host "1. NOVO APP TOKEN" -ForegroundColor Green
Write-Host "   Caminho no GLPI: Setup > General > API > Application tokens"
$newAppToken = Read-Host "   Cole o novo App Token aqui"

if ([string]::IsNullOrWhiteSpace($newAppToken)) {
    Write-Host " App Token não pode estar vazio!" -ForegroundColor Red
    exit 1
}

# Solicitar novo User Token
Write-Host ""
Write-Host "2. NOVO USER TOKEN" -ForegroundColor Green
Write-Host "   Caminho no GLPI: Meu Perfil > API > Personal tokens"
$newUserToken = Read-Host "   Cole o novo User Token aqui"

if ([string]::IsNullOrWhiteSpace($newUserToken)) {
    Write-Host " User Token não pode estar vazio!" -ForegroundColor Red
    exit 1
}

# Validar comprimento dos tokens
if ($newAppToken.Length -ne 40) {
    Write-Host "  AVISO: App Token deveria ter 40 caracteres, mas tem $($newAppToken.Length)" -ForegroundColor Yellow
}

if ($newUserToken.Length -ne 40) {
    Write-Host "  AVISO: User Token deveria ter 40 caracteres, mas tem $($newUserToken.Length)" -ForegroundColor Yellow
}

# Confirmar atualização
Write-Host ""
Write-Host "=== CONFIRMAÇÃO ===" -ForegroundColor Yellow
Write-Host "App Token:  $($newAppToken.Substring(0, 10))...$($newAppToken.Substring($newAppToken.Length-5))"
Write-Host "User Token: $($newUserToken.Substring(0, 10))...$($newUserToken.Substring($newUserToken.Length-5))"
Write-Host ""
$confirm = Read-Host "Confirma a atualização dos tokens? (s/N)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host " Operação cancelada pelo usuário." -ForegroundColor Red
    exit 1
}

# Fazer backup do .env atual
Write-Host ""
Write-Host " Fazendo backup do .env atual..." -ForegroundColor Blue
Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Atualizar tokens
Write-Host " Atualizando tokens no arquivo .env..." -ForegroundColor Blue

try {
    # Atualizar App Token
    (Get-Content .env) -replace "GLPI_APP_TOKEN=.*", "GLPI_APP_TOKEN=$newAppToken" | Set-Content .env
    
    # Atualizar User Token
    (Get-Content .env) -replace "GLPI_USER_TOKEN=.*", "GLPI_USER_TOKEN=$newUserToken" | Set-Content .env
    
    Write-Host " Tokens atualizados com sucesso!" -ForegroundColor Green
    
    # Mostrar tokens atualizados
    Write-Host ""
    Write-Host "=== TOKENS ATUALIZADOS ===" -ForegroundColor Green
    Get-Content .env | Where-Object { $_ -like '*GLPI_*TOKEN*' } | ForEach-Object {
        $parts = $_ -split '='
        if ($parts.Length -eq 2) {
            $tokenName = $parts[0]
            $tokenValue = $parts[1]
            Write-Host "$tokenName = $($tokenValue.Substring(0, 10))...$($tokenValue.Substring($tokenValue.Length-5))"
        }
    }
    
    Write-Host ""
    Write-Host "=== PRÓXIMOS PASSOS ===" -ForegroundColor Cyan
    Write-Host "1. Teste a conectividade: python test_simple_glpi.py"
    Write-Host "2. Se funcionar, reinicie o backend (Ctrl+C e execute novamente)"
    Write-Host "3. Verifique se o dashboard mostra dados reais"
    
} catch {
    Write-Host " Erro ao atualizar tokens: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host " Backup salvo como: .env.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')" -ForegroundColor Yellow
    exit 1
}
