# Protocolo de Recuperação e Manutenção do Sistema GLPI Dashboard

## SITUAÇÃO ATUAL CRÍTICA

### Problema Identificado
- O projeto estava funcionalmente estável com apenas "total de status por nível" não funcionando
- Layout e CSS estavam consistentes e bem estruturados
- Dados reais estavam se alinhando corretamente
- Múltiplas tentativas de refatoração causaram regressões
- Interface atual apresenta erro "url is not defined"

### Estado Desejado
- Recuperar funcionalidade completa do dashboard
- Manter consistência visual e de estilo
- Corrigir apenas o problema de "total de status por nível"
- Estabelecer desenvolvimento incremental e seguro

## PROTOCOLO DE RECUPERAÇÃO IMEDIATA

### Fase 1: Diagnóstico e Estabilização

#### 1.1 Verificação de Estado
```bash
# Verificar branch atual
git branch

# Verificar status dos serviços
# Backend: http://localhost:5000/health
# Frontend: http://localhost:5173

# Verificar logs de erro
# Backend: logs do Flask
# Frontend: console do navegador
```

#### 1.2 Identificação de Problemas
- [ ] Backend está respondendo?
- [ ] Frontend está carregando?
- [ ] API está conectada?
- [ ] Dados estão sendo recuperados?
- [ ] Interface está renderizando?

### Fase 2: Recuperação de Estado Funcional

#### 2.1 Opções de Recuperação (em ordem de prioridade)

**Opção A: Branch backup-pre-refactoring**
```bash
git checkout backup-pre-refactoring
npm install  # no frontend
pip install -e .  # no backend
```

**Opção B: Reversão seletiva**
```bash
git log --oneline -10
git revert <commit-hash-problemático>
```

**Opção C: Cherry-pick de funcionalidades**
```bash
git cherry-pick <commit-hash-funcional>
```

#### 2.2 Validação de Recuperação
- [ ] Backend inicia sem erros
- [ ] Frontend carrega completamente
- [ ] Dashboard exibe dados
- [ ] Estilos estão aplicados
- [ ] Navegação funciona
- [ ] Componentes respondem

### Fase 3: Correção Incremental

#### 3.1 Foco Único: Total de Status por Nível
- Identificar componente específico
- Analisar dados necessários
- Verificar endpoint da API
- Implementar correção mínima
- Testar isoladamente

#### 3.2 Validação Contínua
```bash
# Após cada mudança
npm run build  # verificar build
npm run dev    # verificar desenvolvimento
python app.py  # verificar backend
```

## REGRAS DE DESENVOLVIMENTO SEGURO

### Regra 1: Mudança Única por Vez
- Alterar apenas um componente/arquivo por vez
- Testar completamente antes da próxima mudança
- Fazer commit de cada mudança funcional
- Nunca fazer múltiplas alterações simultâneas

### Regra 2: Validação Obrigatória
- Testar no navegador após cada mudança
- Verificar console de erros
- Confirmar dados carregando
- Validar estilos mantidos

### Regra 3: Backup Preventivo
```bash
# Antes de qualquer mudança significativa
git branch backup-$(date +%Y%m%d-%H%M%S)
git add .
git commit -m "Backup antes de mudança"
```

### Regra 4: Rollback Imediato
- Se qualquer erro aparecer, reverter imediatamente
- Não tentar "consertar" erros com mais mudanças
- Voltar ao estado funcional anterior
- Analisar problema isoladamente

## ARQUIVOS CRÍTICOS - NÃO ALTERAR SEM EXTREMA CAUTELA

### Frontend
```
frontend/src/App.tsx
frontend/src/main.tsx
frontend/src/config/constants.ts
frontend/src/services/httpClient.ts
frontend/package.json
frontend/vite.config.ts
```

### Backend
```
app.py
backend/api/routes.py
backend/config/settings.py
backend/services/glpi_service.py
.env
pyproject.toml
```

## SINAIS DE ALERTA - PARAR IMEDIATAMENTE

### Erros Críticos
- "url is not defined"
- Tela branca no frontend
- Erro 500 no backend
- "Cannot read property of undefined"
- Estilos CSS não carregando
- Componentes não renderizando

### Ações Imediatas
1. Parar desenvolvimento
2. Reverter última mudança
3. Verificar estado funcional
4. Analisar logs de erro
5. Planejar abordagem alternativa

## CHECKLIST DE FUNCIONALIDADE MÍNIMA

### Backend
- [ ] Flask inicia sem erros
- [ ] Endpoint /health responde
- [ ] Endpoint /api/status responde
- [ ] Logs não mostram erros críticos
- [ ] Conexão com GLPI funciona (mesmo com warning)

### Frontend
- [ ] Aplicação carrega sem tela branca
- [ ] Console sem erros críticos
- [ ] Componentes renderizam
- [ ] Estilos CSS aplicados
- [ ] Dados aparecem na interface
- [ ] Navegação funciona

### Integração
- [ ] Frontend conecta com backend
- [ ] Dados fluem da API para interface
- [ ] Atualizações refletem na tela
- [ ] Performance aceitável

## PRÓXIMOS PASSOS SEGUROS

### 1. Estabilização Completa
- Garantir que tudo funciona como antes
- Documentar estado atual
- Identificar exatamente o que não funciona

### 2. Correção Pontual
- Focar apenas no "total de status por nível"
- Não alterar nada mais
- Implementar solução mínima

### 3. Melhorias Graduais
- Após estabilização completa
- Uma melhoria por vez
- Sempre com backup e teste

---

**PRINCÍPIO FUNDAMENTAL**: É melhor ter um sistema 95% funcional e estável do que um sistema 100% funcional mas instável. A prioridade é SEMPRE a estabilidade e funcionalidade existente.