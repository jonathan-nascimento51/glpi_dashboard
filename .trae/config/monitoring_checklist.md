# Checklist de Monitoramento e Validação - GLPI Dashboard

## VALIDAÇÃO PRÉ-DESENVOLVIMENTO

### 1. Estado Inicial do Sistema
```bash
# Verificar branch atual
git branch
git status

# Verificar serviços
ps aux | grep python  # Backend rodando?
ps aux | grep node    # Frontend rodando?

# Testar endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/status
```

### 2. Funcionalidade Baseline
- [ ] Dashboard carrega sem erros
- [ ] Dados aparecem na tela
- [ ] Estilos estão aplicados
- [ ] Navegação funciona
- [ ] Console sem erros críticos
- [ ] Performance aceitável

## VALIDAÇÃO DURANTE DESENVOLVIMENTO

### 3. Após Cada Mudança de Código
```bash
# Frontend
npm run build  # Build deve passar
npm run dev    # Dev server deve iniciar

# Backend
python -m pytest  # Se testes existirem
python app.py     # Deve iniciar sem erros
```

### 4. Checklist de Funcionalidade
- [ ] Aplicação carrega (não tela branca)
- [ ] Componentes renderizam
- [ ] Dados são exibidos
- [ ] Estilos mantidos
- [ ] Sem erros no console
- [ ] API responde

## SINAIS DE ALERTA CRÍTICOS

### 5. Erros que Exigem Parada Imediata

#### Frontend
```javascript
// Erros críticos no console
"url is not defined"
"Cannot read property of undefined"
"Module not found"
"Unexpected token"
"SyntaxError"
```

#### Backend
```python
# Erros críticos nos logs
"ModuleNotFoundError"
"ImportError"
"SyntaxError"
"500 Internal Server Error"
"Connection refused"
```

### 6. Problemas Visuais Críticos
- Tela completamente branca
- Componentes não renderizando
- CSS não carregando
- Layout quebrado
- Dados não aparecendo

## PROTOCOLO DE RESPOSTA A PROBLEMAS

### 7. Ação Imediata para Erros

#### Passo 1: Parar e Avaliar
```bash
# Parar desenvolvimento
# Não fazer mais mudanças
# Documentar erro exato
```

#### Passo 2: Reverter
```bash
git stash  # Salvar mudanças
git checkout -- .  # Reverter arquivos
# OU
git reset --hard HEAD~1  # Reverter último commit
```

#### Passo 3: Validar Reversão
- [ ] Sistema volta a funcionar
- [ ] Erro desaparece
- [ ] Funcionalidade restaurada

#### Passo 4: Analisar e Planejar
- Identificar causa raiz
- Planejar abordagem alternativa
- Fazer mudança menor e mais segura

## MÉTRICAS DE QUALIDADE

### 8. Indicadores de Saúde do Sistema

#### Performance
- Tempo de carregamento < 3 segundos
- Resposta da API < 1 segundo
- Build do frontend < 30 segundos
- Inicialização do backend < 10 segundos

#### Estabilidade
- Zero erros críticos no console
- Zero erros 500 no backend
- 100% dos componentes renderizando
- 100% dos dados carregando

#### Usabilidade
- Interface responsiva
- Navegação fluida
- Feedback visual adequado
- Dados atualizados

## FERRAMENTAS DE MONITORAMENTO

### 9. Comandos de Diagnóstico

#### Sistema
```bash
# Verificar processos
netstat -tulpn | grep :5000  # Backend
netstat -tulpn | grep :5173  # Frontend

# Verificar logs
tail -f backend/logs/app.log
# Console do navegador (F12)
```

#### Git
```bash
# Estado do repositório
git log --oneline -5
git diff HEAD~1
git status
```

#### Dependências
```bash
# Frontend
npm list --depth=0
npm audit

# Backend
pip list
pip check
```

### 10. Pontos de Verificação Obrigatórios

#### Antes de Commit
- [ ] Código compila/builda
- [ ] Aplicação funciona localmente
- [ ] Testes passam (se existirem)
- [ ] Sem erros no console
- [ ] Funcionalidade testada manualmente

#### Antes de Push
- [ ] Múltiplos testes locais
- [ ] Documentação atualizada
- [ ] Changelog atualizado
- [ ] Branch limpo e organizado

## RECUPERAÇÃO DE EMERGÊNCIA

### 11. Plano de Contingência

#### Cenário 1: Sistema Completamente Quebrado
```bash
git checkout backup-pre-refactoring
npm install
pip install -e .
# Verificar funcionalidade
```

#### Cenário 2: Problemas Parciais
```bash
git stash
git checkout -- arquivo-problemático
# Testar correção
```

#### Cenário 3: Dependências Corrompidas
```bash
# Frontend
rm -rf node_modules package-lock.json
npm install

# Backend
pip uninstall -y -r requirements.txt
pip install -e .
```

### 12. Contatos e Recursos

#### Documentação Crítica
- README.md - Instruções básicas
- .env.example - Configurações
- package.json - Dependências frontend
- pyproject.toml - Dependências backend

#### Branches de Segurança
- `main` - Versão estável
- `backup-pre-refactoring` - Backup funcional
- `develop` - Desenvolvimento ativo

---

**LEMBRETE**: Este checklist deve ser seguido religiosamente. Cada item ignorado aumenta exponencialmente o risco de quebrar o sistema. A disciplina na validação é o que separa desenvolvimento profissional de tentativa e erro.