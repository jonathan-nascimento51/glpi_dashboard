# ⚙️ Padrões Técnicos - GLPI Dashboard

## 📋 Índice
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Padrões de Nomenclatura](#-padrões-de-nomenclatura)
- [Templates de Código](#-templates-de-código)
- [Configurações de Ferramentas](#-configurações-de-ferramentas)
- [Padrões de API](#-padrões-de-api)
- [Padrões de Banco de Dados](#-padrões-de-banco-de-dados)

## 📁 Estrutura de Arquivos

### Frontend Structure
```
frontend/src/
├── components/
│   ├── ui/                     # Componentes base (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── index.ts           # Barrel export
│   ├── layout/                # Componentes de layout
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Layout.tsx
│   ├── dashboard/             # Componentes específicos
│   │   ├── MetricsGrid.tsx
│   │   ├── TechnicianRanking.tsx
│   │   └── index.ts
│   └── common/                # Componentes reutilizáveis
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       └── index.ts
├── hooks/                     # Custom hooks
│   ├── useDashboard.ts
│   ├── useApi.ts
│   └── index.ts
├── services/                  # Serviços de API
│   ├── api.ts                # Cliente HTTP base
│   ├── dashboardService.ts   # Serviços específicos
│   └── index.ts
├── types/                     # Definições TypeScript
│   ├── dashboard.ts
│   ├── api.ts
│   └── index.ts
├── utils/                     # Utilitários
│   ├── formatters.ts
│   ├── validators.ts
│   ├── constants.ts
│   └── index.ts
├── lib/                       # Configurações de libs
│   ├── utils.ts              # shadcn/ui utils
│   └── axios.ts              # Configuração axios
└── __tests__/                 # Testes
    ├── components/
    ├── hooks/
    ├── services/
    └── utils/
```

### Backend Structure
```
backend/
├── api/
│   ├── __init__.py
│   ├── routes.py             # Rotas principais
│   └── middleware.py         # Middlewares
├── services/
│   ├── __init__.py
│   ├── base_service.py       # Classe base
│   ├── glpi_service.py       # Integração GLPI
│   ├── dashboard_service.py  # Lógica dashboard
│   └── cache_service.py      # Gerenciamento cache
├── models/
│   ├── __init__.py
│   ├── base.py              # Modelo base
│   ├── ticket.py            # Modelo ticket
│   └── technician.py        # Modelo técnico
├── schemas/
│   ├── __init__.py
│   ├── dashboard.py         # Schemas dashboard
│   └── validation.py        # Validadores
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configurações
│   ├── database.py          # Config DB
│   └── cache.py             # Config cache
├── utils/
│   ├── __init__.py
│   ├── decorators.py        # Decoradores
│   ├── exceptions.py        # Exceções customizadas
│   ├── formatters.py        # Formatadores
│   └── validators.py        # Validadores
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

## 🏷️ Padrões de Nomenclatura

### Frontend (TypeScript)

#### Arquivos e Pastas
```typescript
// Componentes: PascalCase
MetricsGrid.tsx
TechnicianRanking.tsx
DashboardLayout.tsx

// Hooks: camelCase com prefixo 'use'
useDashboard.ts
useApi.ts
useLocalStorage.ts

// Serviços: camelCase com sufixo 'Service'
dashboardService.ts
apiService.ts
cacheService.ts

// Utilitários: camelCase
formatters.ts
validators.ts
constants.ts

// Tipos: camelCase
dashboard.ts
api.ts
common.ts
```

#### Variáveis e Funções
```typescript
// Variáveis: camelCase
const userName = 'João';
const isLoading = false;
const apiResponse = await fetchData();

// Funções: camelCase
function calculateMetrics() {}
const handleSubmit = () => {};
const formatDate = (date: Date) => {};

// Constantes: UPPER_SNAKE_CASE
const API_BASE_URL = 'http://localhost:5000';
const MAX_RETRY_ATTEMPTS = 3;
const CACHE_TTL = 900; // 15 minutes

// Tipos e Interfaces: PascalCase
interface UserData {
  id: number;
  name: string;
}

type ApiResponse<T> = {
  data: T;
  status: number;
};

// Enums: PascalCase
enum TicketStatus {
  Open = 'open',
  InProgress = 'in_progress',
  Resolved = 'resolved',
  Closed = 'closed'
}
```

### Backend (Python)

#### Arquivos e Pastas
```python
# Arquivos: snake_case
dashboard_service.py
glpi_service.py
api_routes.py

# Classes: PascalCase
class DashboardService:
class GLPIService:
class TicketModel:

# Funções e métodos: snake_case
def get_technician_ranking():
def calculate_performance_metrics():
def format_response_data():

# Variáveis: snake_case
user_name = 'João'
is_loading = False
api_response = fetch_data()

# Constantes: UPPER_SNAKE_CASE
API_BASE_URL = 'http://localhost:3306'
MAX_RETRY_ATTEMPTS = 3
CACHE_TTL = 900

# Privados: prefixo underscore
def _internal_method():
_private_variable = 'value'
```

## 📝 Templates de Código

### React Component Template
```typescript
// components/ComponentName.tsx
import React from 'react';
import { cn } from '@/lib/utils';

// Types
interface ComponentNameProps {
  /**
   * Descrição da prop
   */
  title: string;
  /**
   * Prop opcional com valor padrão
   */
  isVisible?: boolean;
  /**
   * Callback function
   */
  onAction?: (value: string) => void;
  /**
   * Classes CSS adicionais
   */
  className?: string;
}

/**
 * ComponentName - Descrição do componente
 * 
 * @param props - Props do componente
 * @returns JSX Element
 */
export const ComponentName: React.FC<ComponentNameProps> = ({
  title,
  isVisible = true,
  onAction,
  className
}) => {
  // State
  const [localState, setLocalState] = React.useState<string>('');
  
  // Effects
  React.useEffect(() => {
    // Effect logic
  }, []);
  
  // Handlers
  const handleClick = React.useCallback(() => {
    onAction?.(localState);
  }, [localState, onAction]);
  
  // Early returns
  if (!isVisible) {
    return null;
  }
  
  // Render
  return (
    <div className={cn('base-styles', className)}>
      <h2>{title}</h2>
      <button onClick={handleClick}>
        Action
      </button>
    </div>
  );
};

// Default export
export default ComponentName;
```

### Custom Hook Template
```typescript
// hooks/useHookName.ts
import { useState, useEffect, useCallback } from 'react';
import { debounce } from '@/utils/debounce';

// Types
interface UseHookNameOptions {
  initialValue?: string;
  debounceMs?: number;
}

interface UseHookNameReturn {
  value: string;
  setValue: (value: string) => void;
  isLoading: boolean;
  error: string | null;
  reset: () => void;
}

/**
 * useHookName - Descrição do hook
 * 
 * @param options - Opções de configuração
 * @returns Objeto com estado e funções
 */
export const useHookName = ({
  initialValue = '',
  debounceMs = 300
}: UseHookNameOptions = {}): UseHookNameReturn => {
  // State
  const [value, setValue] = useState<string>(initialValue);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Debounced function
  const debouncedSetValue = useCallback(
    debounce((newValue: string) => {
      setValue(newValue);
    }, debounceMs),
    [debounceMs]
  );
  
  // Effects
  useEffect(() => {
    // Effect logic
  }, [value]);
  
  // Functions
  const reset = useCallback(() => {
    setValue(initialValue);
    setError(null);
  }, [initialValue]);
  
  return {
    value,
    setValue: debouncedSetValue,
    isLoading,
    error,
    reset
  };
};
```

### Service Template
```typescript
// services/serviceName.ts
import { api } from './api';
import { ApiResponse, ServiceData } from '@/types';

/**
 * ServiceName - Descrição do serviço
 */
export class ServiceName {
  private baseUrl = '/api/service';
  
  /**
   * Método para buscar dados
   */
  async getData(params: GetDataParams): Promise<ServiceData[]> {
    try {
      const response = await api.get<ApiResponse<ServiceData[]>>(
        `${this.baseUrl}/data`,
        { params }
      );
      
      return response.data.data;
    } catch (error) {
      console.error('Error fetching data:', error);
      throw new Error('Falha ao buscar dados');
    }
  }
  
  /**
   * Método para criar dados
   */
  async createData(data: CreateDataParams): Promise<ServiceData> {
    try {
      const response = await api.post<ApiResponse<ServiceData>>(
        `${this.baseUrl}/data`,
        data
      );
      
      return response.data.data;
    } catch (error) {
      console.error('Error creating data:', error);
      throw new Error('Falha ao criar dados');
    }
  }
}

// Export singleton instance
export const serviceNameInstance = new ServiceName();
```

### Python Service Template
```python
# services/service_name.py
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass

from ..config.database import get_db_connection
from ..config.cache import get_cache
from ..utils.exceptions import ServiceError, ValidationError
from ..utils.decorators import log_execution_time, handle_exceptions

logger = logging.getLogger(__name__)

@dataclass
class ServiceData:
    """Data model for service."""
    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class ServiceName:
    """Service for handling specific business logic."""
    
    def __init__(self):
        self.db = get_db_connection()
        self.cache = get_cache()
        self.cache_ttl = 900  # 15 minutes
    
    @log_execution_time
    @handle_exceptions
    async def get_data(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = 10
    ) -> List[ServiceData]:
        """Get data with caching and validation.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results
            
        Returns:
            List of ServiceData objects
            
        Raises:
            ValidationError: If input parameters are invalid
            ServiceError: If data retrieval fails
        """
        # Validation
        if start_date >= end_date:
            raise ValidationError("Start date must be before end date")
        
        if limit and (limit < 1 or limit > 1000):
            raise ValidationError("Limit must be between 1 and 1000")
        
        # Cache check
        cache_key = f"service_data:{start_date}:{end_date}:{limit}"
        cached_result = await self.cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for {cache_key}")
            return cached_result
        
        try:
            # Database query
            query = """
            SELECT id, name, created_at, updated_at
            FROM service_table
            WHERE created_at BETWEEN %s AND %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            results = await self.db.fetch_all(
                query, 
                (start_date, end_date, limit)
            )
            
            # Transform to data objects
            data = [
                ServiceData(
                    id=row['id'],
                    name=row['name'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in results
            ]
            
            # Cache result
            await self.cache.set(cache_key, data, ttl=self.cache_ttl)
            
            logger.info(f"Retrieved {len(data)} records")
            return data
            
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            raise ServiceError(f"Failed to retrieve data: {str(e)}")
    
    @handle_exceptions
    async def create_data(self, data: Dict[str, Any]) -> ServiceData:
        """Create new data entry.
        
        Args:
            data: Data to create
            
        Returns:
            Created ServiceData object
            
        Raises:
            ValidationError: If data is invalid
            ServiceError: If creation fails
        """
        # Validation
        required_fields = ['name']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Field '{field}' is required")
        
        try:
            query = """
            INSERT INTO service_table (name, created_at)
            VALUES (%s, %s)
            RETURNING id, name, created_at
            """
            
            result = await self.db.fetch_one(
                query,
                (data['name'], datetime.utcnow())
            )
            
            created_data = ServiceData(
                id=result['id'],
                name=result['name'],
                created_at=result['created_at']
            )
            
            # Invalidate related cache
            await self._invalidate_cache()
            
            logger.info(f"Created data with id {created_data.id}")
            return created_data
            
        except Exception as e:
            logger.error(f"Error creating data: {e}")
            raise ServiceError(f"Failed to create data: {str(e)}")
    
    async def _invalidate_cache(self):
        """Invalidate related cache entries."""
        pattern = "service_data:*"
        await self.cache.delete_pattern(pattern)
        logger.info("Cache invalidated for service data")

# Singleton instance
service_instance = ServiceName()
```

### Test Template
```typescript
// __tests__/components/ComponentName.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { ComponentName } from '../ComponentName';

// Mocks
const mockOnAction = vi.fn();

// Test data
const defaultProps = {
  title: 'Test Title',
  onAction: mockOnAction
};

describe('ComponentName', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  describe('Rendering', () => {
    it('should render with required props', () => {
      render(<ComponentName {...defaultProps} />);
      
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
    
    it('should not render when isVisible is false', () => {
      render(<ComponentName {...defaultProps} isVisible={false} />);
      
      expect(screen.queryByText('Test Title')).not.toBeInTheDocument();
    });
    
    it('should apply custom className', () => {
      const { container } = render(
        <ComponentName {...defaultProps} className="custom-class" />
      );
      
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });
  
  describe('Interactions', () => {
    it('should call onAction when button is clicked', async () => {
      render(<ComponentName {...defaultProps} />);
      
      fireEvent.click(screen.getByRole('button'));
      
      await waitFor(() => {
        expect(mockOnAction).toHaveBeenCalledTimes(1);
      });
    });
    
    it('should not call onAction when prop is not provided', () => {
      const { onAction, ...propsWithoutAction } = defaultProps;
      render(<ComponentName {...propsWithoutAction} />);
      
      fireEvent.click(screen.getByRole('button'));
      
      expect(mockOnAction).not.toHaveBeenCalled();
    });
  });
  
  describe('Edge Cases', () => {
    it('should handle empty title', () => {
      render(<ComponentName {...defaultProps} title="" />);
      
      expect(screen.getByRole('heading')).toBeInTheDocument();
    });
  });
});
```

## ⚙️ Configurações de Ferramentas

### ESLint Configuration
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": ["@typescript-eslint", "react", "react-hooks"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "prefer-const": "error",
    "no-var": "error",
    "no-console": "warn"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

### Prettier Configuration
```json
// .prettierrc.json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### TypeScript Configuration
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## 🌐 Padrões de API

### REST API Conventions
```
# Recursos (substantivos no plural)
GET    /api/tickets              # Listar tickets
GET    /api/tickets/{id}         # Obter ticket específico
POST   /api/tickets              # Criar ticket
PUT    /api/tickets/{id}         # Atualizar ticket completo
PATCH  /api/tickets/{id}         # Atualizar ticket parcial
DELETE /api/tickets/{id}         # Deletar ticket

# Sub-recursos
GET    /api/tickets/{id}/comments    # Comentários do ticket
POST   /api/tickets/{id}/comments    # Adicionar comentário

# Ações específicas (verbos)
POST   /api/tickets/{id}/assign      # Atribuir ticket
POST   /api/tickets/{id}/resolve     # Resolver ticket
POST   /api/tickets/{id}/close       # Fechar ticket

# Filtros e paginação
GET    /api/tickets?status=open&page=1&limit=20
GET    /api/tickets?technician_id=123&start_date=2024-01-01
```

### Response Format
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  },
  "meta": {
    "timestamp": "2024-12-29T10:00:00Z",
    "version": "1.0.0",
    "request_id": "uuid-here"
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dados inválidos fornecidos",
    "details": {
      "field": "email",
      "reason": "Formato de email inválido"
    }
  },
  "meta": {
    "timestamp": "2024-12-29T10:00:00Z",
    "request_id": "uuid-here"
  }
}
```

## 🗄️ Padrões de Banco de Dados

### Naming Conventions
```sql
-- Tabelas: snake_case, plural
tickets
technicians
ticket_comments
user_sessions

-- Colunas: snake_case
id
user_id
created_at
updated_at
first_name
last_name

-- Índices: idx_table_column(s)
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_technician_created ON tickets(technician_id, created_at);

-- Foreign Keys: fk_table_referenced_table
ALTER TABLE tickets ADD CONSTRAINT fk_tickets_technicians 
  FOREIGN KEY (technician_id) REFERENCES technicians(id);

-- Constraints: chk_table_condition
ALTER TABLE tickets ADD CONSTRAINT chk_tickets_status 
  CHECK (status IN ('open', 'in_progress', 'resolved', 'closed'));
```

### Migration Template
```sql
-- migrations/001_create_tickets_table.sql
-- Description: Create tickets table with basic structure
-- Author: Developer Name
-- Date: 2024-12-29

BEGIN;

CREATE TABLE tickets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('open', 'in_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    priority ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium',
    technician_id BIGINT,
    requester_id BIGINT NOT NULL,
    category_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    closed_at TIMESTAMP NULL,
    
    INDEX idx_tickets_status (status),
    INDEX idx_tickets_technician (technician_id),
    INDEX idx_tickets_created_at (created_at),
    INDEX idx_tickets_priority_status (priority, status),
    
    FOREIGN KEY (technician_id) REFERENCES technicians(id) ON DELETE SET NULL,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

COMMIT;
```

---

**Última atualização**: 2024-12-29
**Versão**: 1.0.0