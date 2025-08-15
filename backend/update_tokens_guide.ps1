# Script para atualizar tokens GLPI no arquivo .env
# Execute este script após gerar novos tokens no GLPI

Write-Host "=== ATUALIZAÇÃO DE TOKENS GLPI ==="
Write-Host "Tokens atuais no .env:"
Get-Content .env | Where-Object { $_ -like '*GLPI*' } | ForEach-Object {
    if ($_ -like '*TOKEN*') {
        $parts = $_ -split '='
        if ($parts.Length -eq 2) {
            $tokenName = $parts[0]
            $tokenValue = $parts[1]
            Write-Host "  $tokenName = $($tokenValue.Substring(0, [Math]::Min(10, $tokenValue.Length)))..."
        }
    } else {
        Write-Host "  $_"
    }
}

Write-Host "`n=== INSTRUÇÕES ==="
Write-Host "1. Acesse: http://cau.ppiratini.intra.rs.gov.br/glpi"
Write-Host "2. Gere novos tokens:"
Write-Host "   - App Token: Setup > General > API > Application tokens"
Write-Host "   - User Token: Meu Perfil > API > Personal tokens"
Write-Host "3. Execute os comandos abaixo com os NOVOS tokens:"
Write-Host ""
Write-Host "# Substitua NOVO_APP_TOKEN pelo token gerado:"
Write-Host '(Get-Content .env) -replace "GLPI_APP_TOKEN=.*", "GLPI_APP_TOKEN=NOVO_APP_TOKEN" | Set-Content .env'
Write-Host ""
Write-Host "# Substitua NOVO_USER_TOKEN pelo token gerado:"
Write-Host '(Get-Content .env) -replace "GLPI_USER_TOKEN=.*", "GLPI_USER_TOKEN=NOVO_USER_TOKEN" | Set-Content .env'
Write-Host ""
Write-Host "4. Teste a conectividade:"
Write-Host "python test_simple_glpi.py"
Write-Host ""
Write-Host "5. Se funcionar, reinicie o backend:"
Write-Host "Ctrl+C no terminal do backend e execute novamente"
