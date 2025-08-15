#!/usr/bin/env pwsh
# =============================================================================
# SCRIPT DE INSTALAÇÃO DO REDIS NO WINDOWS
# =============================================================================
# Este script instala o Redis localmente no Windows usando diferentes métodos

param(
    [ValidateSet("chocolatey", "manual", "wsl")]
    [string]$Method = "chocolatey",
    [switch]$StartService,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] [$Type] $Message" -ForegroundColor $color
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

Write-Status "Iniciando instalação do Redis no Windows" "SUCCESS"

# Verificar se Redis já está instalado
if (Test-Command "redis-server") {
    Write-Status "Redis já está instalado" "SUCCESS"
    if (Test-Port 6379) {
        Write-Status "Redis já está rodando na porta 6379" "SUCCESS"
        exit 0
    }
} else {
    Write-Status "Redis não encontrado, iniciando instalação..." "INFO"
}

switch ($Method) {
    "chocolatey" {
        Write-Status "Instalando Redis via Chocolatey..." "INFO"
        
        # Verificar se Chocolatey está instalado
        if (-not (Test-Command "choco")) {
            Write-Status "Chocolatey não encontrado. Instalando..." "WARNING"
            try {
                Set-ExecutionPolicy Bypass -Scope Process -Force
                [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
                Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
                Write-Status "✓ Chocolatey instalado" "SUCCESS"
            } catch {
                Write-Status "Erro ao instalar Chocolatey: $($_.Exception.Message)" "ERROR"
                exit 1
            }
        }
        
        # Instalar Redis
        try {
            choco install redis-64 -y
            Write-Status "✓ Redis instalado via Chocolatey" "SUCCESS"
        } catch {
            Write-Status "Erro ao instalar Redis: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }
    
    "manual" {
        Write-Status "Instalação manual do Redis..." "INFO"
        
        $redisVersion = "5.0.14.1"
        $downloadUrl = "https://github.com/microsoftarchive/redis/releases/download/win-$redisVersion/Redis-x64-$redisVersion.zip"
        $downloadPath = "$env:TEMP\redis.zip"
        $installPath = "C:\Redis"
        
        try {
            # Download
            Write-Status "Baixando Redis $redisVersion..." "INFO"
            Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath
            
            # Extract
            Write-Status "Extraindo Redis..." "INFO"
            if (Test-Path $installPath) {
                Remove-Item $installPath -Recurse -Force
            }
            Expand-Archive -Path $downloadPath -DestinationPath $installPath
            
            # Add to PATH
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
            if ($currentPath -notlike "*$installPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$installPath", "Machine")
                $env:PATH += ";$installPath"
            }
            
            Write-Status "✓ Redis instalado manualmente em $installPath" "SUCCESS"
            
        } catch {
            Write-Status "Erro na instalação manual: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }
    
    "wsl" {
        Write-Status "Instalando Redis via WSL..." "INFO"
        
        if (-not (Test-Command "wsl")) {
            Write-Status "WSL não encontrado. Instale o WSL primeiro" "ERROR"
            exit 1
        }
        
        try {
            wsl sudo apt update
            wsl sudo apt install -y redis-server
            Write-Status "✓ Redis instalado via WSL" "SUCCESS"
        } catch {
            Write-Status "Erro ao instalar Redis via WSL: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }
}

# Iniciar serviço se solicitado
if ($StartService) {
    Write-Status "Iniciando serviço Redis..." "INFO"
    
    try {
        if ($Method -eq "wsl") {
            wsl sudo service redis-server start
        } else {
            Start-Process -FilePath "redis-server" -WindowStyle Hidden
        }
        
        # Aguardar inicialização
        Start-Sleep -Seconds 3
        
        if (Test-Port 6379) {
            Write-Status "✓ Redis iniciado com sucesso na porta 6379" "SUCCESS"
        } else {
            Write-Status "✗ Falha ao iniciar Redis" "ERROR"
        }
        
    } catch {
        Write-Status "Erro ao iniciar Redis: $($_.Exception.Message)" "ERROR"
    }
}

# Testar instalação
Write-Status "Testando instalação..." "INFO"
if (Test-Command "redis-server") {
    Write-Status "✓ Comando redis-server disponível" "SUCCESS"
} else {
    Write-Status "✗ Comando redis-server não encontrado" "ERROR"
}

if (Test-Command "redis-cli") {
    Write-Status "✓ Comando redis-cli disponível" "SUCCESS"
} else {
    Write-Status "✗ Comando redis-cli não encontrado" "ERROR"
}

Write-Status "Instalação do Redis concluída!" "SUCCESS"
Write-Status "Para iniciar o Redis: redis-server" "INFO"
Write-Status "Para testar: redis-cli ping" "INFO"