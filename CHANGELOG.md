# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado

- Sistema de Knowledge Graph persistente para capturar lições aprendidas
- Sistema de validação automática com testes de regressão
- Documentação viva e contextual auto-atualizável
- Guias de troubleshooting específicos para métricas
- Mapeamento completo de dependências arquiteturais

### Alterado

- Estrutura de logs para formato JSON estruturado
- Pipeline de validação com snapshots históricos
- Sistema de alertas automáticos aprimorado

### Corrigido

- Problema de dados zerados em métricas do dashboard
- Falhas de autenticação intermitentes com GLPI
- Descoberta dinâmica de IDs de campos GLPI
- Inconsistências no mapeamento de níveis N1-N4

## [1.0.0] - 2024-08-14

### Recursos Adicionados

- Dashboard inicial com métricas GLPI
- API FastAPI para integração com GLPI
- Frontend React com componentes de visualização
- Sistema básico de autenticação GLPI
- Testes unitários e de integração
- Configuração Docker Compose
- CI/CD com GitHub Actions

### Decisões Arquiteturais

#### 2024-08-14 - Implementação de Knowledge Graph

**Contexto**: Necessidade de capturar e reutilizar conhecimento sobre problemas recorrentes
**Decisão**: Implementar MCP Knowledge Graph persistente
**Consequências**:

- **Rastreamento automático de padrões de falha**: O sistema registra automaticamente padrões de falha, permitindo que os desenvolvedores identifiquem rapidamente problemas recorrentes.
- **Reutilização de soluções conhecidas**: Com o Knowledge Graph, os desenvolvedores podem reutilizar soluções conhecidas para problemas semelhantes, acelerando o processo de resolução de problemas.
- **Contexto histórico para debugging**: O Knowledge Graph fornece um contexto histórico das interações com o GLPI, facilitando a depuração de problemas.
- **Dependência adicional do sistema MCP**: A implementação do Knowledge Graph adiciona uma dependência adicional ao sistema MCP, mas isso é justificado pela maior eficiência e produtividade que ele proporciona.

#### 2024-08-14 - Sistema de Validação Automática

**Contexto**: Dados zerados recorrentes após mudanças
**Decisão**: Criar sistema de validação com snapshots e regressão
**Consequências**:

- Detecção precoce de problemas
- Comparação automática com estados anteriores
- Relatórios detalhados de falhas
- Overhead de execução em cada deploy

- **Detecção precoce de problemas**: O sistema de validação detecta problemas antes que eles afetem os usuários finais, permitindo uma resolução rápida.
- **Comparação automática com estados anteriores**: O sistema compara automaticamente os estados do GLPI com snapshots históricos, identificando mudanças que possam ter causado problemas.
- **Relatórios detalhados de falhas**: Quando um problema é detectado, o sistema gera relatórios detalhados, incluindo informações sobre a causa raiz, o impacto e as etapas para resolução.
- **Overhead de execução em cada deploy**: A validação é executada em cada deploy, o que pode adicionar um pequeno overhead de execução, mas é justificado pela maior segurança e confiabilidade que ele proporciona.

#### 2024-08-14 - Documentação Viva

**Contexto**: Documentação desatualizada e dispersa
**Decisão**: Implementar documentação auto-atualizável
**Consequências**:

- **Sempre sincronizada com código**: A documentação é atualizada automaticamente com cada deploy, garantindo que sempre esteja sincronizada com o código.
- **Contexto técnico centralizado**: A documentação centralizada no Knowledge Graph fornece um contexto técnico centralizado, facilitando a compreensão de como o sistema funciona.
- **Guias de troubleshooting específicos**: Os desenvolvedores podem encontrar guiadas de troubleshooting específicas para problemas comuns, acelerando a resolução de problemas.
- **Necessita manutenção dos scripts de atualização**: A manutenção dos scripts de atualização é necessária para garantir que a documentação esteja sempre atualizada.

### Lições Aprendidas

#### Problema: Dados Zerados Recorrentes

**Causa Raiz**: Descoberta de campos GLPI falhando silenciosamente
**Solução**: Sistema de fallback e validação obrigatória
**Prevenção**: Testes automáticos antes de cada deploy

#### Problema: Autenticação Intermitente

**Causa Raiz**: Tokens GLPI expirando sem renovação
**Solução**: Sistema de renovação automática
**Prevenção**: Monitoramento de saúde dos tokens

#### Problema: Performance Degradada

**Causa Raiz**: Queries GLPI não otimizadas
**Solução**: Cache Redis e agregações eficientes
**Prevenção**: Profiling contínuo de performance

### Dependências Críticas

#### Externas

- **GLPI REST API**: Fonte primária de dados
- **Redis**: Cache e sessões
- **PostgreSQL**: Dados persistentes (futuro)

#### Internas

- **Backend FastAPI**: Core da aplicação
- **Frontend React**: Interface do usuário
- **Sistema de Validação**: Garantia de qualidade
- **Knowledge Graph**: Memória institucional

### Troubleshooting Histórico

#### 2024-08-14 - Dados Zerados

**Sintomas**: Todos os cards exibindo 0
**Diagnóstico**: `python enhanced_validation.py`
**Solução**: Renovação de tokens + redescoberta de campos
**Tempo de Resolução**: 15 minutos

#### 2024-08-10 - Performance Lenta

**Sintomas**: Dashboard carregando > 30s
**Diagnóstico**: Profiling de queries GLPI
**Solução**: Implementação de cache Redis
**Tempo de Resolução**: 2 horas

### Scripts de Manutenção

```bash
# Atualizar documentação
python scripts/update_docs.py

# Validação completa do sistema
python enhanced_validation.py

# Backup do Knowledge Graph
python scripts/backup_knowledge.py

# Análise de performance
python scripts/performance_analysis.py
```

---

**Formato**: [Keep a Changelog](https://keepachangelog.com/)
**Versionamento**: [Semantic Versioning](https://semver.org/)
**Atualização**: Automática via scripts de deploy
