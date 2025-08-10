# Script de Monitoramento de Métricas de Qualidade
# Executa verificações periódicas e gera relatórios

Write-Host "📊 Sistema de Monitoramento de Qualidade" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Função para coletar métricas do backend
function Get-BackendMetrics {
    Write-Host "\n Coletando métricas do backend..." -ForegroundColor Cyan
    
    $metrics = @{}
    
    try {
        # Verificar cobertura de testes
        Set-Location backend
        $coverageResult = pytest --cov=. --cov-report=json --quiet 2>$null
        if (Test-Path "coverage.json") {
            $coverage = Get-Content "coverage.json" | ConvertFrom-Json
            $metrics.BackendCoverage = [math]::Round($coverage.totals.percent_covered, 2)
        } else {
            $metrics.BackendCoverage = 0
        }
        
        # Verificar qualidade do código (Ruff)
        $ruffResult = ruff check . --output-format=json 2>$null
        if ($LASTEXITCODE -eq 0) {
            $metrics.BackendLintIssues = 0
        } else {
            $ruffOutput = $ruffResult | ConvertFrom-Json
            $metrics.BackendLintIssues = $ruffOutput.Count
        }
        
        # Verificar tipos (MyPy)
        $mypyResult = mypy . --json-report mypy-report 2>$null
        if ($LASTEXITCODE -eq 0) {
            $metrics.BackendTypeIssues = 0
        } else {
            $metrics.BackendTypeIssues = "Errors found"
        }
        
        Set-Location ..
        
    } catch {
        Write-Host "  Erro ao coletar métricas do backend: $_" -ForegroundColor Yellow
        $metrics.BackendCoverage = "Error"
        $metrics.BackendLintIssues = "Error"
        $metrics.BackendTypeIssues = "Error"
    }
    
    return $metrics
}

# Função para coletar métricas do frontend
function Get-FrontendMetrics {
    Write-Host "\n Coletando métricas do frontend..." -ForegroundColor Cyan
    
    $metrics = @{}
    
    try {
        Set-Location frontend
        
        # Verificar cobertura de testes
        $testResult = npm run test:coverage --silent 2>$null
        if (Test-Path "coverage\coverage-summary.json") {
            $coverage = Get-Content "coverage\coverage-summary.json" | ConvertFrom-Json
            $metrics.FrontendCoverage = [math]::Round($coverage.total.lines.pct, 2)
        } else {
            $metrics.FrontendCoverage = 0
        }
        
        # Verificar ESLint
        $eslintResult = npm run lint --silent 2>$null
        if ($LASTEXITCODE -eq 0) {
            $metrics.FrontendLintIssues = 0
        } else {
            $metrics.FrontendLintIssues = "Issues found"
        }
        
        # Verificar TypeScript
        $tscResult = npm run type-check --silent 2>$null
        if ($LASTEXITCODE -eq 0) {
            $metrics.FrontendTypeIssues = 0
        } else {
            $metrics.FrontendTypeIssues = "Errors found"
        }
        
        # Verificar tamanho do build
        if (Test-Path "dist") {
            $buildSize = (Get-ChildItem -Recurse dist | Measure-Object -Property Length -Sum).Sum / 1MB
            $metrics.BuildSizeMB = [math]::Round($buildSize, 2)
        } else {
            $metrics.BuildSizeMB = "No build found"
        }
        
        Set-Location ..
        
    } catch {
        Write-Host "  Erro ao coletar métricas do frontend: $_" -ForegroundColor Yellow
        $metrics.FrontendCoverage = "Error"
        $metrics.FrontendLintIssues = "Error"
        $metrics.FrontendTypeIssues = "Error"
        $metrics.BuildSizeMB = "Error"
    }
    
    return $metrics
}

# Função para gerar relatório
function New-QualityReport {
    param(
        [hashtable]$BackendMetrics,
        [hashtable]$FrontendMetrics
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $reportDate = Get-Date -Format "yyyy-MM-dd"
    
    $report = @"
#  Relatório de Qualidade - $reportDate

Gerado em: $timestamp

##  Resumo Executivo

### Backend
- **Cobertura de Testes**: $($BackendMetrics.BackendCoverage)% (Meta: 80%)
- **Issues de Lint**: $($BackendMetrics.BackendLintIssues)
- **Erros de Tipo**: $($BackendMetrics.BackendTypeIssues)

### Frontend
- **Cobertura de Testes**: $($FrontendMetrics.FrontendCoverage)% (Meta: 80%)
- **Issues de Lint**: $($FrontendMetrics.FrontendLintIssues)
- **Erros de Tipo**: $($FrontendMetrics.FrontendTypeIssues)
- **Tamanho do Build**: $($FrontendMetrics.BuildSizeMB) MB (Meta: 5MB)

##  Status dos Quality Gates

### Backend Quality Gates
"@
    
    # Avaliar status do backend
    if ($BackendMetrics.BackendCoverage -ge 80) {
        $report += "`n-  **Cobertura**: PASSOU ($($BackendMetrics.BackendCoverage)%)"
    } else {
        $report += "`n-  **Cobertura**: FALHOU ($($BackendMetrics.BackendCoverage)%)"
    }
    
    if ($BackendMetrics.BackendLintIssues -eq 0) {
        $report += "`n-  **Lint**: PASSOU (0 issues)"
    } else {
        $report += "`n-  **Lint**: FALHOU ($($BackendMetrics.BackendLintIssues) issues)"
    }
    
    $report += "`n`n### Frontend Quality Gates"
    
    # Avaliar status do frontend
    if ($FrontendMetrics.FrontendCoverage -ge 80) {
        $report += "`n-  **Cobertura**: PASSOU ($($FrontendMetrics.FrontendCoverage)%)"
    } else {
        $report += "`n-  **Cobertura**: FALHOU ($($FrontendMetrics.FrontendCoverage)%)"
    }
    
    if ($FrontendMetrics.FrontendLintIssues -eq 0) {
        $report += "`n-  **Lint**: PASSOU (0 issues)"
    } else {
        $report += "`n-  **Lint**: FALHOU ($($FrontendMetrics.FrontendLintIssues) issues)"
    }
    
    if ($FrontendMetrics.BuildSizeMB -le 5) {
        $report += "`n-  **Build Size**: PASSOU ($($FrontendMetrics.BuildSizeMB) MB)"
    } else {
        $report += "`n-  **Build Size**: FALHOU ($($FrontendMetrics.BuildSizeMB) MB)"
    }
    
    $report += @"

##  Tendências

*Nota: Para visualizar tendências históricas, execute este script regularmente e compare os resultados.*

##  Próximas Ações

### Se algum Quality Gate falhou:
1. Execute o script de validação local: `.\scripts\validate-quality-gates.ps1`
2. Corrija os problemas identificados
3. Execute novamente este monitoramento

### Para melhorar métricas:
- **Cobertura baixa**: Adicione mais testes unitários
- **Issues de lint**: Execute `ruff check --fix` (backend) ou `npm run lint:fix` (frontend)
- **Erros de tipo**: Revise anotações de tipo e configurações do MyPy/TypeScript
- **Build grande**: Analise dependências e otimize imports

---
*Relatório gerado automaticamente pelo sistema de monitoramento de qualidade*
"@
    
    return $report
}

# Execução principal
try {
    Write-Host " Iniciando coleta de métricas..." -ForegroundColor Green
    
    $backendMetrics = Get-BackendMetrics
    $frontendMetrics = Get-FrontendMetrics
    
    Write-Host "\n Gerando relatório..." -ForegroundColor Cyan
    $report = New-QualityReport -BackendMetrics $backendMetrics -FrontendMetrics $frontendMetrics
    
    # Salvar relatório
    $reportPath = "reports\quality-report-$(Get-Date -Format 'yyyy-MM-dd-HHmm').md"
    if (!(Test-Path "reports")) {
        New-Item -ItemType Directory -Path "reports" -Force | Out-Null
    }
    
    $report | Out-File -FilePath $reportPath -Encoding UTF8 -Force
    
    Write-Host "\n Relatório gerado: $reportPath" -ForegroundColor Green
    
    # Exibir resumo no console
    Write-Host "\n RESUMO DE QUALIDADE" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    Write-Host "Backend Coverage: $($backendMetrics.BackendCoverage)%" -ForegroundColor $(if($backendMetrics.BackendCoverage -ge 80) { "Green" } else { "Red" })
    Write-Host "Frontend Coverage: $($frontendMetrics.FrontendCoverage)%" -ForegroundColor $(if($frontendMetrics.FrontendCoverage -ge 80) { "Green" } else { "Red" })
    Write-Host "Build Size: $($frontendMetrics.BuildSizeMB) MB" -ForegroundColor $(if($frontendMetrics.BuildSizeMB -le 5) { "Green" } else { "Red" })
    
} catch {
    Write-Host " Erro durante monitoramento: $_" -ForegroundColor Red
    exit 1
}
