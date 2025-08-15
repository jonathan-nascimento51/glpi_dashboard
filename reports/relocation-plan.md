# Plano de Relocação - Fase 1
*Revisor Estrutural de Repositório TRAE*

## Resumo Executivo
- **Data:** 2025-01-14
- **Branch:** chore/structure-sweep-20250814
- **Total de arquivos Python analisados:** 80
- **Arquivos órfãos identificados:** 51
- **Arquivos suspeitos:** 4
- **Risco geral:** MÉDIO (muitos órfãos, poucos suspeitos)

## Status
 **ANÁLISE CONCLUÍDA** - Inventário completo e órfãos identificados

## 1. ARQUIVOS SUSPEITOS (Remoção Imediata)

### 1.1 Arquivos de Backup/Mock (Risco: BAIXO)
| Arquivo | Destino | Motivo | Ação |
|---------|---------|--------|---------|
| `app_backup.py` | `./_attic/20250114/` | Backup obsoleto | Mover |
| `app_mock.py` | `./_attic/20250114/` | Mock não usado | Mover |
| `app_mock_v2.py` | `./_attic/20250114/` | Mock versão antiga | Mover |
| `app_temp.py` | `./_attic/20250114/` | Arquivo temporário | Mover |

## 2. ARQUIVOS ÓRFÃOS (Análise Detalhada Necessária)

### 2.1 Configurações e Exemplos (Risco: BAIXO)
| Arquivo | Status | Recomendação |
|---------|--------|-------------|
| `config_safe_changes.py` | Órfão | Verificar se é usado pelo sistema TRAE |
| `example_ai_context.py` | Órfão | Mover para `docs/examples/` |
| `example_monitoring.py` | Órfão | Mover para `docs/examples/` |
| `example_safe_changes.py` | Órfão | Mover para `docs/examples/` |

### 2.2 Scripts de Validação (Risco: MÉDIO)
| Arquivo | Status | Recomendação |
|---------|--------|-------------|
| `enhanced_validation.py` | Órfão | Verificar dependências antes de mover |
| `reorganize_structure.py` | Órfão | Mover para `scripts/` se funcional |
| `validate_simple.py` | Órfão | Consolidar com outros validadores |
| `validate_system.py` | Órfão | Consolidar com outros validadores |

## 3. ESTRUTURA PROPOSTA

```
project/
 _attic/20250114/          # Arquivos removidos temporariamente
    app_backup.py
    app_mock.py
    app_mock_v2.py
    app_temp.py
 docs/
    examples/             # Arquivos de exemplo
        example_ai_context.py
        example_monitoring.py
        example_safe_changes.py
 scripts/                  # Scripts utilitários
    reorganize_structure.py
    validation/
        enhanced_validation.py
        validate_simple.py
        validate_system.py
 (arquivos principais mantidos na raiz)
```

## 4. PLANO DE EXECUÇÃO

### Fase 4.1: Remoção Segura (Risco: BAIXO)
1. Criar diretório `_attic/20250114/`
2. Mover arquivos suspeitos para attic
3. Testar build e execução
4. Commit: `chore: move suspicious backup/mock files to attic`

### Fase 4.2: Reorganização de Exemplos (Risco: BAIXO)
1. Criar `docs/examples/`
2. Mover arquivos example_*.py
3. Atualizar README se necessário
4. Commit: `chore: organize example files in docs/examples`

### Fase 4.3: Consolidação de Scripts (Risco: MÉDIO)
1. Analisar scripts de validação
2. Consolidar funcionalidades duplicadas
3. Mover para `scripts/validation/`
4. Atualizar imports se necessário
5. Commit: `refactor: consolidate validation scripts`

## 5. ROLLBACK PLAN

Em caso de problemas:
1. `git checkout HEAD~1` (voltar commit anterior)
2. Restaurar arquivos do `_attic/` se necessário
3. Reverter mudanças de import
4. Executar testes de validação

## 6. VALIDAÇÕES OBRIGATÓRIAS

### Antes de cada commit:
- [ ] `python app.py` executa sem erro
- [ ] `python trae_quick_check.py` passa
- [ ] Frontend builda sem erro
- [ ] Testes básicos passam

### Após reorganização completa:
- [ ] Sistema TRAE AI funcional
- [ ] Dashboard carrega corretamente
- [ ] Todos os endpoints respondem
- [ ] Logs sem erros críticos

## 7. MÉTRICAS DE SUCESSO

-  Redução de 51 para ~15 arquivos órfãos
-  Remoção de 4 arquivos suspeitos
-  Organização clara de examples e scripts
-  Manutenção da funcionalidade TRAE AI
-  Zero quebras de build/execução

---

**Próximo passo:** Executar dry-run para simular todas as mudanças.
