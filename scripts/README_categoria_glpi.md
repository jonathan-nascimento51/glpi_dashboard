# Descoberta do Campo Categoria no GLPI

## Resumo dos Achados

Após executar os scripts de descoberta, foram identificados os seguintes pontos sobre o campo categoria no GLPI:

### 1. Campo Categoria Identificado

- **Campo ID**: `7`
- **Nome**: "Categoria"
- **Tabela**: `glpi_itilcategories`
- **Campo**: `completename`
- **Tipo**: `dropdown`

### 2. Funcionamento do Campo

✅ **Confirmações:**
- O campo 7 está funcionando corretamente
- 100% dos tickets analisados possuem categoria
- Os valores são armazenados como texto completo (ex: "Conservação > Carregadores > Movimentação Equipamentos")
- O campo representa a categoria escolhida pelo usuário no momento da criação do chamado

⚠️ **Observações:**
- Os valores no campo são strings com hierarquia separada por " > "
- Não são IDs numéricos, mas sim o nome completo da categoria
- Isso explica por que a validação de IDs falhou - o campo armazena texto, não IDs

### 3. Estrutura das Categorias

As categorias seguem uma estrutura hierárquica:

```
Categoria Principal > Subcategoria > Subcategoria Específica
```

**Exemplos encontrados:**
- `Conservação > Carregadores > Movimentação Equipamentos`
- `Manutenção > Rede Computadores > Instalação de Rede Lógica`
- `Conservação > Limpeza > Recolher materiais recicláveis`
- `Conservação > Mensageria > Movimentação Documentos`

### 4. Categorias Mais Utilizadas

Baseado na análise dos tickets:

1. **Conservação > Carregadores > Movimentação Equipamentos** - 15 tickets
2. **Manutenção > Rede Computadores > Instalação de Rede Lógica** - 4 tickets
3. **Conservação > Carregadores > Movimentação Mobiliário** - 3 tickets
4. **Manutenção > Rede Computadores > Readequação Rede Lógica** - 3 tickets
5. **Manutenção > Rede Computadores > Conserto Rede Lógica** - 3 tickets

## Como Usar o Campo Categoria

### 1. Para Consultas SQL Diretas

```sql
-- Buscar tickets por categoria específica
SELECT * FROM glpi_tickets 
WHERE itilcategories_id IN (
    SELECT id FROM glpi_itilcategories 
    WHERE completename LIKE 'Conservação > Carregadores%'
);
```

### 2. Para API do GLPI

```python
# Buscar tickets por categoria usando a API
search_params = {
    'is_deleted': 0,
    'criteria[0][field]': '7',  # Campo categoria
    'criteria[0][searchtype]': 'contains',
    'criteria[0][value]': 'Conservação > Carregadores'
}
```

### 3. Para Análises e Relatórios

```python
# Agrupar por categoria principal
def get_main_category(complete_name):
    return complete_name.split(' > ')[0] if ' > ' in complete_name else complete_name

# Agrupar por subcategoria
def get_subcategory(complete_name):
    parts = complete_name.split(' > ')
    return ' > '.join(parts[:2]) if len(parts) >= 2 else complete_name
```

## Scripts Criados

### 1. `discover_category_field.py`
- Descobre todos os campos relacionados a categoria
- Identifica o campo correto (ID 7)
- Lista as opções de busca disponíveis

### 2. `test_category_mapping.py`
- Testa o campo categoria com dados reais
- Analisa a distribuição de categorias
- Valida o funcionamento do campo

### 3. `category_usage_report.py`
- Gera relatório detalhado de uso de categorias
- Identifica categorias mais e menos utilizadas
- Salva relatório em JSON para análise posterior

## Recomendações

### Para Desenvolvimento

1. **Use o campo 7** para consultas de categoria
2. **Trate os valores como strings** com hierarquia
3. **Implemente busca por LIKE ou CONTAINS** para categorias parciais
4. **Considere indexação** se fizer muitas consultas por categoria

### Para Análises

1. **Separe por níveis hierárquicos** para análises mais granulares
2. **Monitore categorias sem uso** para limpeza
3. **Analise tendências** de uso por período
4. **Crie dashboards** por categoria principal

### Para Manutenção

1. **Execute os scripts regularmente** para monitorar mudanças
2. **Valide novos campos** se a estrutura do GLPI mudar
3. **Mantenha backup** das configurações de categoria
4. **Documente mudanças** na estrutura de categorias

## Conclusão

O campo categoria (ID 7) no GLPI está funcionando corretamente e armazena o nome completo da categoria escolhida pelo usuário. Os valores são strings hierárquicas que podem ser facilmente processadas para análises e relatórios.

A implementação atual no dashboard está correta ao usar o campo 7 para consultas de categoria.