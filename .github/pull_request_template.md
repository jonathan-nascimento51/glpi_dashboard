# Pull Request

## 📋 Descrição

<!-- Descreva brevemente as mudanças implementadas neste PR -->

### Tipo de Mudança

<!-- Marque o tipo de mudança que este PR representa -->

- [ ] 🐛 Bug fix (mudança que corrige um problema)
- [ ] ✨ Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] 💥 Breaking change (mudança que quebra compatibilidade)
- [ ] 📚 Documentação (mudanças apenas na documentação)
- [ ] 🎨 Estilo (formatação, espaços em branco, etc.)
- [ ] ♻️ Refatoração (mudança de código que não corrige bug nem adiciona funcionalidade)
- [ ] ⚡ Performance (mudança que melhora performance)
- [ ] ✅ Testes (adição ou correção de testes)
- [ ] 🔧 Chore (mudanças no processo de build, ferramentas auxiliares, etc.)

## 🔗 Issue Relacionada

<!-- Link para a issue que este PR resolve -->
Fixes #(número da issue)

## 🧪 Como Testar

<!-- Descreva os passos para testar as mudanças -->

1. 
2. 
3. 

## 📸 Screenshots (se aplicável)

<!-- Adicione screenshots para mudanças na UI -->

| Antes | Depois |
|-------|--------|
| <!-- screenshot --> | <!-- screenshot --> |

## ✅ Checklist

### Código

- [ ] Meu código segue as diretrizes de estilo do projeto
- [ ] Realizei uma auto-revisão do meu código
- [ ] Comentei meu código, especialmente em áreas difíceis de entender
- [ ] Minhas mudanças não geram novos warnings
- [ ] Removi código comentado e console.logs desnecessários

### Testes

- [ ] Adicionei testes que provam que minha correção é efetiva ou que minha funcionalidade funciona
- [ ] Testes unitários novos e existentes passam localmente com minhas mudanças
- [ ] Testes de integração passam (se aplicável)
- [ ] Cobertura de testes mantida ou melhorada

### Documentação

- [ ] Fiz mudanças correspondentes na documentação
- [ ] Atualizei o README.md (se necessário)
- [ ] Atualizei comentários no código
- [ ] Adicionei/atualizei docstrings (Python) ou JSDoc (TypeScript)

### Segurança

- [ ] Não expus informações sensíveis (senhas, tokens, etc.)
- [ ] Validei entradas do usuário adequadamente
- [ ] Implementei tratamento de erros apropriado
- [ ] Considerei implicações de segurança das mudanças

### Performance

- [ ] Considerei o impacto na performance
- [ ] Otimizei consultas de banco de dados (se aplicável)
- [ ] Implementei cache quando apropriado
- [ ] Evitei vazamentos de memória

### Compatibilidade

- [ ] Minhas mudanças são compatíveis com versões anteriores
- [ ] Se introduzi breaking changes, documentei adequadamente
- [ ] Testei em diferentes navegadores (se aplicável)
- [ ] Testei em diferentes resoluções de tela (se aplicável)

## 🔄 Mudanças Específicas

### Backend (Python/FastAPI)

<!-- Se aplicável, descreva mudanças no backend -->

- [ ] Novos endpoints adicionados
- [ ] Modelos de dados modificados
- [ ] Lógica de negócio alterada
- [ ] Integração com GLPI modificada
- [ ] Sistema de cache atualizado
- [ ] Validações implementadas/modificadas

### Frontend (React/TypeScript)

<!-- Se aplicável, descreva mudanças no frontend -->

- [ ] Novos componentes criados
- [ ] Hooks modificados/criados
- [ ] Serviços de API atualizados
- [ ] Estilos/UI modificados
- [ ] Roteamento alterado
- [ ] Estado global modificado

### Banco de Dados

<!-- Se aplicável, descreva mudanças no banco -->

- [ ] Novas tabelas criadas
- [ ] Esquema modificado
- [ ] Migrações adicionadas
- [ ] Índices criados/modificados
- [ ] Dados de seed atualizados

### DevOps/Infraestrutura

<!-- Se aplicável, descreva mudanças na infraestrutura -->

- [ ] Docker files modificados
- [ ] CI/CD pipeline atualizado
- [ ] Configurações de ambiente alteradas
- [ ] Scripts de deploy modificados
- [ ] Monitoramento/logging implementado

## 🚨 Breaking Changes

<!-- Se este PR introduz breaking changes, descreva-os aqui -->

- 

## 📝 Notas Adicionais

<!-- Qualquer informação adicional que os revisores devem saber -->

### Dependências

<!-- Liste novas dependências adicionadas -->

- 

### Configuração

<!-- Mudanças necessárias na configuração -->

- 

### Migração

<!-- Passos necessários para migração (se aplicável) -->

1. 
2. 

## 🔍 Revisão

### Pontos de Atenção

<!-- Destaque áreas que precisam de atenção especial na revisão -->

- 

### Perguntas para Revisores

<!-- Perguntas específicas para os revisores -->

- 

## 📊 Impacto

### Performance

<!-- Descreva o impacto na performance -->

- [ ] Melhoria na performance
- [ ] Sem impacto na performance
- [ ] Possível impacto negativo (justifique)

### Usuários

<!-- Descreva o impacto nos usuários -->

- [ ] Melhoria na experiência do usuário
- [ ] Nova funcionalidade disponível
- [ ] Mudança no comportamento existente
- [ ] Requer treinamento/comunicação

## 🚀 Deploy

### Pré-requisitos

<!-- Liste pré-requisitos para deploy -->

- [ ] Backup do banco de dados
- [ ] Variáveis de ambiente atualizadas
- [ ] Dependências instaladas
- [ ] Migrações executadas

### Rollback

<!-- Descreva como fazer rollback se necessário -->

- 

---

**Checklist do Revisor:**

- [ ] Código revisado e aprovado
- [ ] Testes executados e passando
- [ ] Documentação adequada
- [ ] Sem problemas de segurança
- [ ] Performance aceitável
- [ ] Compatibilidade verificada

**Para o Merge:**

- [ ] Todos os checks de CI passando
- [ ] Pelo menos uma aprovação
- [ ] Branch atualizada com a base
- [ ] Conflitos resolvidos
- [ ] Squash commits (se necessário)