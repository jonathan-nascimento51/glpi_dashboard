@echo off
REM Script de execução do monitoramento GLPI Dashboard
REM Criado automaticamente em 2025-08-16 23:47:58

cd /d "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard\backend"

REM Ativar ambiente virtual se existir
if exist ".venv\Scriptsctivate.bat" (
    call .venv\Scriptsctivate.bat
) else if exist "..env\Scriptsctivate.bat" (
    call ..env\Scriptsctivate.bat
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
