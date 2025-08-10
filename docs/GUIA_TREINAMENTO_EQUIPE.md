# 👥 Guia de Treinamento - Metodologia de Revisão em Ciclos

## 🎯 Objetivo

Este guia tem como objetivo treinar a equipe na nova metodologia de revisão em ciclos implementada no projeto GLPI Dashboard, garantindo que todos os membros compreendam e apliquem corretamente os processos de qualidade.

## 📚 Conteúdo do Treinamento

### 1. 📖 Visão Geral da Metodologia

#### Princípios Fundamentais:
- **Metas Claras**: Cada ciclo tem objetivos específicos e mensuráveis
- **Modularidade**: Divisão em ciclos independentes mas complementares
- **Iteração**: Processo de 3 fases (Preparação  Avaliação  Resultados)
- **Melhoria Contínua**: Feedback constante e ajustes baseados em métricas

#### Estrutura dos Ciclos:
1. **Ciclo A - Configuração e Ambiente**
2. **Ciclo B - Backend**
3. **Ciclo C - Frontend**

### 2. 🔧 Ferramentas e Scripts

#### Scripts de Validação Local:
```bash
# PowerShell (Windows)
.\scripts\validate-quality-gates.ps1

# Bash (Linux/Mac)
./scripts/validate-quality-gates.sh
```

#### Ambiente de Preview para E2E:
```bash
# Iniciar ambiente
.\scripts\start-preview.ps1

# Parar ambiente
.\scripts\stop-preview.ps1
```

### 3. 🚦 Quality Gates

#### Backend Quality Gates:
- ✅ **Ruff Linting**: Verificação de estilo de código
-  **MyPy**: Verificação de tipos
-  **Bandit**: Análise de segurança
-  **Safety**: Verificação de vulnerabilidades
-  **Coverage**: Cobertura mínima de 80%

#### Frontend Quality Gates:
- ✅ **ESLint**: Verificação de estilo JavaScript/TypeScript
- ✅ **Prettier**: Formatação de código
- ✅ **TypeScript**: Verificação de tipos
- ✅ **Coverage**: Cobertura mínima de 80%
-  **Build**: Validação de build de produção
-  **Bundle Size**: Limite de 5MB

#### Integration Quality Gates:
-  **API Schema**: Validação de schema da API
-  **API Drift**: Detecção de mudanças não documentadas

### 4.  Processo de Execução

#### Pré-requisitos:
1. **Ambiente configurado** com Python 3.12+ e Node.js 18+
2. **Dependências instaladas** (requirements.txt e package.json)
3. **Variáveis de ambiente** configuradas (.env files)

#### Fluxo de Trabalho:

1. **Antes de cada commit:**
   ```bash
   # Executar validação local
   .\scripts\validate-quality-gates.ps1
   ```

2. **Antes de criar PR:**
   ```bash
   # Testar ambiente E2E
   .\scripts\start-preview.ps1
   cd frontend
   npm run test:e2e
   ```

3. **Durante code review:**
   - Verificar se todos os Quality Gates passaram no CI
   - Revisar métricas de cobertura
   - Validar documentação atualizada

### 5.  Exercícios Práticos

#### Exercício 1: Validação Local
1. Clone o repositório
2. Configure o ambiente
3. Execute o script de validação
4. Corrija eventuais problemas encontrados

#### Exercício 2: Ambiente de Preview
1. Inicie o ambiente de preview
2. Acesse frontend e backend
3. Execute testes E2E
4. Pare o ambiente corretamente

#### Exercício 3: Simulação de Falha
1. Introduza um erro de linting
2. Execute validação local
3. Corrija o erro
4. Valide novamente

### 6.  Métricas e Monitoramento

#### Métricas Quantitativas:
- **Cobertura de Código**: Backend 80%, Frontend 80%
- **Tempo de Build**: 5 minutos
- **Taxa de Falha de Quality Gates**: 10%
- **Tempo de Feedback**: 2 minutos

#### Métricas Qualitativas:
- **Satisfação da Equipe**: Survey trimestral
- **Facilidade de Uso**: Feedback contínuo
- **Efetividade**: Redução de bugs em produção

### 7.  Troubleshooting

#### Problemas Comuns:

**Erro: "Python não encontrado"**
```bash
# Solução: Verificar instalação do Python
python --version
# ou
python3 --version
```

**Erro: "npm ci falhou"**
```bash
# Solução: Limpar cache e reinstalar
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Erro: "Porta já em uso"**
```bash
# Solução: Parar processos existentes
.\scripts\stop-preview.ps1
```

### 8.  Suporte e Contatos

- **Documentação**: `docs/METODOLOGIA_REVISAO_CICLOS.md`
- **Quality Gates**: `docs/QUALITY_GATES_CI.md`
- **Issues**: GitHub Issues do projeto
- **Dúvidas**: Canal #dev-quality no Slack

### 9.  Atualizações

Este guia será atualizado regularmente. Verifique a versão mais recente em:
- **Última atualização**: {data_atual}
- **Versão**: 1.0
- **Próxima revisão**: Trimestral

---

##  Checklist de Conclusão do Treinamento

- [ ] Li e compreendi a metodologia de revisão em ciclos
- [ ] Configurei meu ambiente de desenvolvimento
- [ ] Executei com sucesso os scripts de validação local
- [ ] Testei o ambiente de preview para E2E
- [ ] Realizei os exercícios práticos
- [ ] Compreendi as métricas e Quality Gates
- [ ] Sei onde buscar ajuda em caso de problemas

**Nome**: _______________  
**Data**: _______________  
**Assinatura**: _______________
