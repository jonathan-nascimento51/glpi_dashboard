# Teste direto com curl para validar tokens GLPI
$env:GLPI_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
$env:GLPI_APP_TOKEN = "c1U4Emxp0n7ClNDz7Kd2jSkcVB5gG4XFTLlnTm85"
$env:GLPI_USER_TOKEN = "WPjwz02rLe4jLt3YzJrpJJTzQmIwIXkKFvDsJpEU"

Write-Host "=== TESTE CURL DIRETO ==="
Write-Host "URL: $env:GLPI_URL"
Write-Host "App Token: $($env:GLPI_APP_TOKEN.Substring(0,10))..."
Write-Host "User Token: $($env:GLPI_USER_TOKEN.Substring(0,10))..."

# Teste com curl
curl -X GET "$env:GLPI_URL/initSession" `
  -H "Content-Type: application/json" `
  -H "App-Token: $env:GLPI_APP_TOKEN" `
  -H "Authorization: user_token $env:GLPI_USER_TOKEN" `
  --connect-timeout 10
