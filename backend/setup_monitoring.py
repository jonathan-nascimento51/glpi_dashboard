#!/usr/bin/env python3
"""
Script de Configuração do Sistema de Monitoramento

Este script configura a execução automática do sistema de monitoramento,
criando tarefas agendadas e configurações necessárias.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringSetup:
    """Configurador do sistema de monitoramento"""

    def __init__(self) -> None:
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "monitoring_config.json"
        self.log_dir = self.base_dir / "logs"
        self.reports_dir = self.base_dir / "monitoring_reports"

    def create_directories(self) -> None:
        """Cria diretórios necessários"""
        logger.info("Criando diretórios necessários...")

        directories = [self.log_dir, self.reports_dir]
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logger.info(f"Diretório criado/verificado: {directory}")

    def create_config_file(self) -> None:
        """Cria arquivo de configuração do monitoramento"""
        logger.info("Criando arquivo de configuração...")

        config = {
            "monitoring": {
                "enabled": True,
                "interval_minutes": 60,  # Executar a cada hora
                "alert_thresholds": {
                    "high_severity_max": 0,  # Máximo de alertas de alta severidade
                    "medium_severity_max": 3,  # Máximo de alertas de média severidade
                    "total_alerts_max": 10,  # Máximo total de alertas
                },
                "notifications": {
                    "email_enabled": False,
                    "email_recipients": [],
                    "slack_enabled": False,
                    "slack_webhook": "",
                },
                "retention": {
                    "reports_days": 30,  # Manter relatórios por 30 dias
                    "logs_days": 7,  # Manter logs por 7 dias
                },
            },
            "checks": {
                "technician_groups_consistency": {"enabled": True, "critical": True},
                "ranking_completeness": {"enabled": True, "critical": True},
                "api_connectivity": {"enabled": True, "critical": True},
                "data_freshness": {"enabled": True, "critical": False},
            },
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Arquivo de configuração criado: {self.config_file}")

    def create_batch_script(self) -> None:
        """Cria script batch para execução no Windows"""
        logger.info("Criando script batch para Windows...")

        batch_content = f"""@echo off
REM Script de execução do monitoramento GLPI Dashboard
REM Criado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

cd /d "{self.base_dir}"

REM Ativar ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

REM Executar monitoramento
python monitoring_system.py

REM Verificar código de saída
if %ERRORLEVEL% neq 0 (
    echo ERRO: Monitoramento falhou com código %ERRORLEVEL%
    echo Timestamp: %date% %time%
    echo.
) else (
    echo Monitoramento executado com sucesso
    echo Timestamp: %date% %time%
    echo.
)

pause
"""

        batch_file = self.base_dir / "run_monitoring.bat"
        with open(batch_file, "w", encoding="utf-8") as f:
            f.write(batch_content)

        logger.info(f"Script batch criado: {batch_file}")

    def create_powershell_script(self) -> None:
        """Cria script PowerShell para execução"""
        logger.info("Criando script PowerShell...")

        ps_content = f"""# Script PowerShell para execução do monitoramento GLPI Dashboard
# Criado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

$ErrorActionPreference = "Stop"
$BaseDir = "{self.base_dir}"

try {{
    Set-Location $BaseDir
    
    # Ativar ambiente virtual se existir
    if (Test-Path ".venv\Scripts\Activate.ps1") {{
        & ".venv\Scripts\Activate.ps1"
    }} elseif (Test-Path "..\venv\Scripts\Activate.ps1") {{
        & "..\venv\Scripts\Activate.ps1"
    }}
    
    # Executar monitoramento
    Write-Host "Iniciando monitoramento..." -ForegroundColor Green
    python monitoring_system.py
    
    if ($LASTEXITCODE -eq 0) {{
        Write-Host "Monitoramento executado com sucesso" -ForegroundColor Green
        Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
    }} else {{
        Write-Host "ERRO: Monitoramento falhou com código $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
        exit $LASTEXITCODE
    }}
}} catch {{
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
    exit 1
}}
"""

        ps_file = self.base_dir / "run_monitoring.ps1"
        with open(ps_file, "w", encoding="utf-8") as f:
            f.write(ps_content)

        logger.info(f"Script PowerShell criado: {ps_file}")

    def create_task_scheduler_xml(self) -> None:
        """Cria arquivo XML para agendamento no Windows Task Scheduler"""
        logger.info("Criando arquivo XML para Task Scheduler...")

        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>GLPI Dashboard Monitoring</Author>
    <Description>Monitoramento automático do Dashboard GLPI</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT1H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T09:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -File "{self.base_dir}\run_monitoring.ps1"</Arguments>
      <WorkingDirectory>{self.base_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""

        xml_file = self.base_dir / "glpi_monitoring_task.xml"
        with open(xml_file, "w", encoding="utf-16") as f:
            f.write(xml_content)

        logger.info(f"Arquivo XML criado: {xml_file}")

    def create_readme(self) -> None:
        """Cria arquivo README com instruções"""
        logger.info("Criando arquivo README...")

        readme_content = f"""# Sistema de Monitoramento - Dashboard GLPI

Sistema automatizado para monitoramento da integridade dos dados do Dashboard GLPI.

## Arquivos Criados

- `monitoring_system.py` - Script principal de monitoramento
- `monitoring_config.json` - Arquivo de configuração
- `run_monitoring.bat` - Script batch para execução manual
- `run_monitoring.ps1` - Script PowerShell para execução
- `glpi_monitoring_task.xml` - Arquivo para agendamento no Windows

## Configuração Automática

### 1. Execução Manual

**Windows (Batch):**
```cmd
run_monitoring.bat
```

**Windows (PowerShell):**
```powershell
.\run_monitoring.ps1
```

**Python direto:**
```bash
python monitoring_system.py
```

### 2. Agendamento Automático (Windows)

1. Abra o **Agendador de Tarefas** (Task Scheduler)
2. Clique em **Importar Tarefa...**
3. Selecione o arquivo `glpi_monitoring_task.xml`
4. Configure as credenciais se necessário
5. A tarefa será executada automaticamente a cada hora

### 3. Configuração Manual do Agendamento

Se preferir configurar manualmente:

1. Abra o Agendador de Tarefas
2. Crie uma nova tarefa básica
3. Nome: "GLPI Dashboard Monitoring"
4. Gatilho: Diariamente, repetir a cada 1 hora
5. Ação: Iniciar programa
   - Programa: `powershell.exe`
   - Argumentos: `-ExecutionPolicy Bypass -File "{self.base_dir}\run_monitoring.ps1"`
   - Diretório: `{self.base_dir}`

## Configuração

Edite o arquivo `monitoring_config.json` para personalizar:

- **Intervalo de execução**: `interval_minutes`
- **Limites de alerta**: `alert_thresholds`
- **Notificações**: `notifications` (email, Slack)
- **Retenção de dados**: `retention`
- **Verificações ativas**: `checks`

## Relatórios

Os relatórios são salvos em:
- **Diretório**: `monitoring_reports/`
- **Formato**: `monitoring_report_YYYYMMDD_HHMMSS.json`
- **Logs**: `logs/monitoring.log`

## Tipos de Verificação

1. **Consistência de Grupos**: Verifica se técnicos estão nos grupos corretos
2. **Completude do Ranking**: Verifica se todos os níveis têm técnicos
3. **Conectividade API**: Testa conexão com GLPI
4. **Atualização de Dados**: Verifica se há dados recentes

## Alertas

### Severidades
- **Alta**: Problemas críticos que afetam funcionalidade
- **Média**: Inconsistências que podem causar problemas
- **Baixa**: Avisos informativos

### Tipos de Alerta
- `missing_levels_in_ranking`: Níveis ausentes no ranking
- `no_technicians_in_level`: Nível sem técnicos
- `user_in_group_not_in_mapping`: Usuário em grupo mas não no mapeamento
- `no_recent_tickets`: Ausência de tickets recentes

## Solução de Problemas

### Erro de Conectividade
1. Verifique configurações de rede
2. Confirme credenciais do GLPI
3. Teste conectividade manual

### Erro de Permissões
1. Execute como administrador
2. Verifique permissões de arquivo
3. Configure política de execução do PowerShell:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Logs
Verifique os logs em `logs/monitoring.log` para detalhes de erros.

## Manutenção

- **Limpeza automática**: Configurada para manter relatórios por 30 dias
- **Atualização**: Modifique `monitoring_system.py` conforme necessário
- **Backup**: Faça backup dos arquivos de configuração

---

**Criado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Versão**: 1.0.0
"""

        readme_file = self.base_dir / "MONITORING_README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)

        logger.info(f"README criado: {readme_file}")

    def setup_complete_monitoring(self) -> bool:
        """Executa configuração completa do sistema de monitoramento"""
        logger.info("Iniciando configuração completa do sistema de monitoramento...")

        try:
            self.create_directories()
            self.create_config_file()
            self.create_batch_script()
            self.create_powershell_script()
            self.create_task_scheduler_xml()
            self.create_readme()

            logger.info("✅ Configuração do sistema de monitoramento concluída com sucesso!")

            print("\n" + "=" * 60)
            print("SISTEMA DE MONITORAMENTO CONFIGURADO COM SUCESSO!")
            print("=" * 60)
            print(f"Diretório base: {self.base_dir}")
            print(f"Configuração: {self.config_file}")
            print(f"Logs: {self.log_dir}")
            print(f"Relatórios: {self.reports_dir}")
            print("\nPróximos passos:")
            print("1. Execute manualmente: run_monitoring.bat ou run_monitoring.ps1")
            print("2. Configure agendamento: Importe glpi_monitoring_task.xml no Task Scheduler")
            print("3. Leia o MONITORING_README.md para instruções detalhadas")
            print("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Erro durante configuração: {e}")
            return False


def main() -> int:
    """Função principal"""
    setup = MonitoringSetup()
    success = setup.setup_complete_monitoring()

    if not success:
        print("❌ Falha na configuração do sistema de monitoramento")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
