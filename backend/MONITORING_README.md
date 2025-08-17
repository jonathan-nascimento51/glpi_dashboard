# Sistema de Monitoramento - Dashboard GLPI

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
.un_monitoring.ps1
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
   - Argumentos: `-ExecutionPolicy Bypass -File "C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard\backendun_monitoring.ps1"`
   - Diretório: `C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard\backend`

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

**Criado em**: 2025-08-16 23:47:58
**Versão**: 1.0.0
