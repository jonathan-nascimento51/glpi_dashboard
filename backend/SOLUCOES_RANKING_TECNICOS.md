# Soluções para o Problema de Ranking de Técnicos

## Problema Identificado

**CAUSA RAIZ**: O sistema GLPI não possui técnicos ativos. Todos os usuários com perfil de técnico foram deletados ou desativados.

### Evidências
- 683 usuários ativos no GLPI
- 0 usuários com perfil de técnico (ID 6) ativo
- 41 registros Profile_User com perfil técnico, mas todos os usuários associados retornam erro 404
- Perfis 13, 14, 15 existem mas todos os usuários foram deletados

### Diferença nos Métodos
- `get_technician_ranking()` (sem filtro): Usa `_get_technician_ranking_knowledge_base()` que filtra corretamente por Profile_User
- `get_technician_ranking_with_filters()` (com filtro): Usa `_get_all_technician_ids_and_names()` que retorna TODOS os usuários ativos

## Soluções Propostas

### 1. Solução Administrativa (Recomendada)

#### Opção A: Reativar Técnicos Existentes
- Acessar o GLPI como administrador
- Localizar usuários técnicos desativados
- Reativar os usuários necessários
- Verificar se os perfis de técnico estão corretos

#### Opção B: Criar Novos Técnicos
- Criar novos usuários no GLPI
- Atribuir perfil de técnico (ID 6)
- Configurar permissões adequadas
- Associar à entidade correta

### 2. Solução Técnica Imediata

#### Corrigir `_get_all_technician_ids_and_names()`
O método deve filtrar por Profile_User em vez de buscar todos os usuários ativos.

**Problema atual:**
```python
# Busca TODOS os usuários ativos
user_params = {
    "criteria[0][field]": "8",  # is_active
    "criteria[0][searchtype]": "equals",
    "criteria[0][value]": "1"   # ativo
}
```

**Correção necessária:**
```python
# Deve usar a mesma lógica de _get_technician_ranking_knowledge_base()
# Buscar Profile_User com perfil técnico e depois os usuários ativos
```

### 3. Solução de Fallback

#### Implementar Tratamento Robusto
- Detectar quando não há técnicos disponíveis
- Retornar mensagem informativa em vez de erro
- Logs detalhados para diagnóstico
- Fallback para dados de exemplo (opcional)

## Implementação Recomendada

### Passo 1: Correção Técnica
1. Corrigir `_get_all_technician_ids_and_names()` para usar a mesma lógica de filtragem
2. Implementar tratamento de erro quando não há técnicos
3. Adicionar logs informativos

### Passo 2: Solução Administrativa
1. Verificar com administrador do GLPI sobre técnicos
2. Reativar ou criar usuários técnicos conforme necessário
3. Testar o sistema após a correção

### Passo 3: Validação
1. Testar ranking com e sem filtros
2. Verificar todos os cenários de filtragem
3. Validar logs e tratamento de erros

## Arquivos a Modificar

1. `services/glpi_service.py`:
   - Método `_get_all_technician_ids_and_names()`
   - Adicionar tratamento de erro robusto

2. Frontend (se necessário):
   - Melhorar mensagens de erro
   - Tratamento quando não há técnicos

## Campos GLPI Identificados

- **Profile_User campo 2**: users_id (campo correto para user ID)
- **Profile_User campo 4**: profiles_id (ID do perfil)
- **Profile_User campo 5**: username
- **User campo 8**: is_active (status ativo/inativo)

## Próximos Passos

1. **Imediato**: Implementar correção técnica
2. **Curto prazo**: Coordenar com administrador GLPI
3. **Médio prazo**: Testar e validar todas as funcionalidades
4. **Longo prazo**: Implementar monitoramento para evitar recorrência