# 🤖 AI Quick Reference - GLPI Dashboard

> Referência rápida para assistentes de IA trabalhando no projeto GLPI Dashboard

## 📋 Checklist Inicial

Antes de qualquer ação, SEMPRE:

- [ ] ✅ Analisar o contexto atual do projeto
- [ ] 🔍 Verificar arquivos relacionados à tarefa
- [ ] 📊 Revisar testes existentes
- [ ] 🏗️ Considerar impacto na arquitetura
- [ ] 🔒 Validar aspectos de segurança
- [ ] ⚡ Avaliar performance

## 🎯 Regras Críticas

### ❌ NUNCA FAÇA
1. **Quebrar testes existentes** sem corrigir
2. **Remover validações de segurança**
3. **Ignorar padrões de código estabelecidos**
4. **Fazer commits sem testar**
5. **Expor dados sensíveis em logs**
6. **Usar `any` em TypeScript** sem justificativa
7. **Criar componentes sem testes**
8. **Ignorar tratamento de erros**

### ✅ SEMPRE FAÇA
1. **Seguir convenções de nomenclatura**
2. **Adicionar testes para novo código**
3. **Validar tipos TypeScript**
4. **Tratar erros adequadamente**
5. **Documentar APIs e componentes**
6. **Usar hooks customizados quando apropriado**
7. **Implementar loading states**
8. **Adicionar logs para debugging**

## 🏗️ Arquitetura Rápida

```
Frontend (React + TS)     Backend (Python + Flask)
├── components/           ├── api/
│   ├── ui/              │   └── routes.py
│   └── dashboard/       ├── services/
├── hooks/               │   ├── glpi_service.py
├── services/            │   └── api_service.py
├── types/               ├── schemas/
└── utils/               └── utils/
```

## 🔧 Comandos Essenciais

### Frontend
```bash
# Desenvolvimento
npm run dev              # Servidor dev
npm test                 # Testes
npm run lint             # Linting
npm run type-check       # Verificação tipos

# Build
npm run build            # Build produção
npm run preview          # Preview build
```

### Backend
```bash
# Desenvolvimento
python app.py            # Servidor dev
pytest                   # Testes
flake8 .                # Linting
mypy .                  # Verificação tipos

# Produção
gunicorn app:app         # Servidor produção
```

## 📝 Templates de Código

### React Component
```typescript
import React from 'react';
import { cn } from '@/lib/utils';

interface ComponentProps {
  className?: string;
  // outras props
}

export const Component: React.FC<ComponentProps> = ({ 
  className,
  ...props 
}) => {
  return (
    <div className={cn('base-classes', className)}>
      {/* conteúdo */}
    </div>
  );
};

Component.displayName = 'Component';
```

### Custom Hook
```typescript
import { useState, useEffect } from 'react';
import { ApiResponse } from '@/types';

interface UseHookReturn {
  data: DataType | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export const useHook = (): UseHookReturn => {
  const [data, setData] = useState<DataType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      // fetch logic
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
};
```

### Python Service
```python
from typing import Dict, List, Optional
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class ServiceClass:
    """Descrição do serviço."""
    
    def __init__(self):
        self.config = current_app.config
    
    def method_name(self, param: str) -> Dict:
        """Descrição do método.
        
        Args:
            param: Descrição do parâmetro
            
        Returns:
            Dict com resultado
            
        Raises:
            ValueError: Quando parâmetro inválido
        """
        try:
            # lógica do método
            logger.info(f"Executando método com param: {param}")
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Erro no método: {str(e)}")
            raise
```

## 🧪 Padrões de Teste

### Frontend Test
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Component } from './Component';

describe('Component', () => {
  it('should render correctly', () => {
    render(<Component />);
    expect(screen.getByRole('...')).toBeInTheDocument();
  });

  it('should handle user interaction', () => {
    const mockFn = jest.fn();
    render(<Component onAction={mockFn} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(mockFn).toHaveBeenCalledWith(expectedArgs);
  });
});
```

### Backend Test
```python
import pytest
from unittest.mock import Mock, patch
from services.service_class import ServiceClass

class TestServiceClass:
    """Testes para ServiceClass."""
    
    def setup_method(self):
        self.service = ServiceClass()
    
    def test_method_success(self):
        """Testa execução bem-sucedida do método."""
        result = self.service.method_name("valid_param")
        assert result["success"] is True
        assert "data" in result
    
    def test_method_invalid_param(self):
        """Testa tratamento de parâmetro inválido."""
        with pytest.raises(ValueError):
            self.service.method_name("")
```

## 🔍 Debugging

### Frontend
```typescript
// Console debugging
console.log('Debug:', { data, loading, error });

// React DevTools
// Usar React Developer Tools no browser

// Network debugging
// Verificar Network tab no DevTools
```

### Backend
```python
# Logging
logger.debug(f"Debug info: {variable}")
logger.info(f"Info: {status}")
logger.error(f"Error: {error}")

# Breakpoints
import pdb; pdb.set_trace()

# Flask debugging
app.run(debug=True)
```

## 📊 Métricas de Qualidade

### Frontend
- **Cobertura de testes**: > 90%
- **TypeScript strict**: ✅
- **ESLint errors**: 0
- **Bundle size**: < 500KB
- **Lighthouse**: > 90

### Backend
- **Cobertura de testes**: > 85%
- **Flake8 compliance**: ✅
- **MyPy errors**: 0
- **Response time**: < 200ms
- **Memory usage**: < 512MB

## 🚨 Troubleshooting

### Problemas Comuns

#### Frontend
```bash
# Erro de tipos TypeScript
npm run type-check

# Problemas de dependências
rm -rf node_modules package-lock.json
npm install

# Build falha
npm run lint
npm run type-check
npm run test
```

#### Backend
```bash
# Erro de importação
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Problemas de dependências
pip install -r requirements.txt

# Erro de banco
flask db upgrade
```

## 📚 Documentação Relacionada

- [🤖 AI Assistant Guide](./AI_ASSISTANT_GUIDE.md)
- [🏗️ Project Context](./AI_PROJECT_CONTEXT.md)
- [⚙️ Development Rules](./AI_DEVELOPMENT_RULES.md)
- [🤝 Contributing](./CONTRIBUTING.md)
- [📋 Technical Standards](./TECHNICAL_STANDARDS.md)
- [🌍 Environment Config](./ENVIRONMENT_CONFIG.md)
- [🔄 CI/CD Config](./CI_CD_CONFIG.md)

## 🎯 Próximos Passos Prioritários

### Curto Prazo (1-2 semanas)
1. ✅ Corrigir testes falhando (2/38)
2. 🔧 Implementar Error Boundaries
3. 📊 Adicionar logging estruturado
4. 🧪 Aumentar cobertura de testes E2E

### Médio Prazo (1 mês)
1. 🔒 Implementar autenticação JWT
2. 📈 Sistema de monitoramento
3. 🚀 Pipeline CI/CD completo
4. 📱 Responsividade mobile

### Longo Prazo (3 meses)
1. 🌐 Internacionalização (i18n)
2. 📊 Analytics avançados
3. 🔄 Real-time updates
4. 🎨 Design system completo

---

**💡 Dica**: Mantenha este arquivo sempre atualizado e use-o como primeira referência em qualquer tarefa!