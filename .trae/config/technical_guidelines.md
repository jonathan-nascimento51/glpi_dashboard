# Configurações Técnicas de Alto Nível para Trae AI

## Diretrizes Fundamentais de Desenvolvimento

### 1. PRINCÍPIOS DE SEGURANÇA E CONSISTÊNCIA

#### 1.1 Validação Obrigatória Antes de Mudanças
- **SEMPRE** verificar o estado atual do projeto antes de fazer alterações
- **SEMPRE** testar funcionalidades existentes antes de modificar código
- **SEMPRE** fazer backup do estado funcional antes de refatorações
- **NUNCA** assumir que mudanças não afetarão outras partes do sistema

#### 1.2 Abordagem Incremental
- Fazer mudanças pequenas e testáveis
- Validar cada mudança antes de prosseguir
- Manter funcionalidades existentes durante refatorações
- Documentar cada alteração significativa

### 2. ARQUITETURA E ESTRUTURA DO PROJETO

#### 2.1 Backend (Flask)
```
backend/
├── api/                 # Endpoints da API
├── config/              # Configurações centralizadas
├── schemas/             # Validação de dados
├── services/            # Lógica de negócio
└── utils/               # Utilitários compartilhados
```

#### 2.2 Frontend (React + TypeScript)
```
frontend/src/
├── components/          # Componentes reutilizáveis
├── hooks/               # Hooks customizados
├── services/            # Comunicação com API
├── types/               # Definições TypeScript
└── utils/               # Utilitários do frontend
```

### 3. PADRÕES DE DESENVOLVIMENTO

#### 3.1 Modificação de Arquivos
- **SEMPRE** ler o arquivo completo antes de modificar
- **SEMPRE** manter padrões de código existentes
- **SEMPRE** preservar imports e dependências
- **NUNCA** remover código sem verificar dependências

#### 3.2 Gerenciamento de Estado
- Manter consistência entre frontend e backend
- Validar tipos de dados em ambas as pontas
- Implementar tratamento de erros robusto
- Manter cache e estado sincronizados

### 4. PROTOCOLO DE MUDANÇAS SEGURAS

#### 4.1 Antes de Qualquer Alteração
1. Verificar status atual dos serviços
2. Testar funcionalidades críticas
3. Identificar dependências da mudança
4. Criar backup se necessário

#### 4.2 Durante a Implementação
1. Fazer mudanças incrementais
2. Testar cada alteração
3. Verificar logs de erro
4. Validar interface do usuário

#### 4.3 Após a Implementação
1. Testar todas as funcionalidades afetadas
2. Verificar consistência visual
3. Validar performance
4. Documentar mudanças

### 5. TRATAMENTO DE ERROS E DEBUGGING

#### 5.1 Identificação de Problemas
- Verificar logs do backend e frontend
- Analisar erros de console do navegador
- Verificar conectividade entre serviços
- Validar configurações de ambiente

#### 5.2 Resolução de Problemas
- Isolar o problema antes de fazer mudanças
- Testar soluções em ambiente controlado
- Reverter mudanças se necessário
- Documentar soluções para problemas recorrentes

### 6. CONFIGURAÇÕES ESPECÍFICAS DO PROJETO

#### 6.1 Portas e Serviços
- Backend: http://localhost:5000
- Frontend: http://localhost:5173
- API Base URL: http://localhost:5000/api

#### 6.2 Arquivos Críticos
- `.env` - Configurações de ambiente
- `frontend/.env` - Configurações do frontend
- `frontend/src/config/constants.ts` - Constantes da aplicação
- `frontend/src/services/httpClient.ts` - Cliente HTTP

#### 6.3 Dependências Principais
- Backend: Flask, Redis, Requests
- Frontend: React, TypeScript, Vite, Axios

### 7. CHECKLIST DE VALIDAÇÃO

#### 7.1 Antes de Finalizar Qualquer Tarefa
- [ ] Backend está rodando sem erros
- [ ] Frontend está rodando sem erros
- [ ] API está respondendo corretamente
- [ ] Interface está funcionando
- [ ] Dados estão sendo exibidos
- [ ] Estilos estão consistentes
- [ ] Não há erros no console
- [ ] Performance está adequada

#### 7.2 Sinais de Alerta para Parar
- Erros 500 no backend
- Tela branca no frontend
- Erros de "url is not defined"
- Perda de estilos CSS
- Componentes não renderizando
- Dados não carregando

### 8. RECUPERAÇÃO DE ESTADO FUNCIONAL

#### 8.1 Branches de Backup
- `backup-pre-refactoring` - Estado funcional anterior
- `main` - Branch principal estável

#### 8.2 Processo de Recuperação
1. Identificar último estado funcional
2. Fazer checkout para branch estável
3. Verificar funcionalidades
4. Aplicar mudanças incrementalmente
5. Testar cada etapa

### 9. COMUNICAÇÃO E DOCUMENTAÇÃO

#### 9.1 Relatórios de Progresso
- Sempre informar o que foi alterado
- Documentar problemas encontrados
- Explicar soluções implementadas
- Sugerir próximos passos

#### 9.2 Linguagem e Tom
- Usar português brasileiro
- Ser claro e objetivo
- Explicar decisões técnicas
- Admitir limitações quando necessário

### 10. METAS DE QUALIDADE

#### 10.1 Objetivos Principais
- Manter funcionalidade existente
- Melhorar gradualmente o código
- Garantir consistência visual
- Otimizar performance
- Facilitar manutenção

#### 10.2 Métricas de Sucesso
- Zero regressões funcionais
- Interface consistente e responsiva
- Código limpo e bem estruturado
- Documentação atualizada
- Testes passando

---

**LEMBRETE CRÍTICO**: Este projeto já teve múltiplas tentativas de refatoração que resultaram em quebras. A prioridade é SEMPRE manter a funcionalidade existente e fazer mudanças incrementais e testadas.