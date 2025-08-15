# Script para verificar e corrigir tokens GLPI
Write-Host "=== DIAGNÓSTICO TOKENS GLPI ==="

# Ler arquivo .env
$envContent = Get-Content .env -Raw
Write-Host "Conteúdo do .env (linhas GLPI):"
$envContent -split "`n" | Where-Object { $_ -like "*GLPI*" } | ForEach-Object {
    Write-Host "  $_"
}

Write-Host "`n=== VERIFICAÇÃO DE CARACTERES ==="

# Verificar se há caracteres especiais
$appTokenLine = $envContent -split "`n" | Where-Object { $_ -like "GLPI_APP_TOKEN=*" } | Select-Object -Last 1
$userTokenLine = $envContent -split "`n" | Where-Object { $_ -like "GLPI_USER_TOKEN=*" } | Select-Object -Last 1

if ($appTokenLine) {
    $appToken = $appTokenLine -replace "GLPI_APP_TOKEN=", ""
    Write-Host "App Token extraído: [$appToken]"
    Write-Host "App Token length: $($appToken.Length)"
    Write-Host "App Token bytes: $([System.Text.Encoding]::UTF8.GetBytes($appToken) -join ",")"
}

if ($userTokenLine) {
    $userToken = $userTokenLine -replace "GLPI_USER_TOKEN=", ""
    Write-Host "User Token extraído: [$userToken]"
    Write-Host "User Token length: $($userToken.Length)"
    Write-Host "User Token bytes: $([System.Text.Encoding]::UTF8.GetBytes($userToken) -join ",")"
}

Write-Host "`n=== SUGESTÕES ==="
Write-Host "1. Verificar se os tokens não expiraram"
Write-Host "2. Regenerar tokens no GLPI"
Write-Host "3. Verificar se não há espaços ou caracteres especiais"
Write-Host "4. Testar com tokens novos"
