# Contexto do Projeto GLPI Dashboard

## VISÃO GERAL DO SISTEMA

### Propósito
Dashboard para visualização de métricas e dados do sistema GLPI (Gestionnaire Libre de Parc Informatique), fornecendo uma interface moderna e responsiva para monitoramento de tickets, equipamentos e estatísticas.

### Arquitetura
- **Backend**: Flask (Python) - API REST
- **Frontend**: React + TypeScript + Vite
- **Integração**: API REST do GLPI
- **Cache**: Redis (com fallback para SimpleCache)
- **Estilo**: CSS modular com componentes estilizados

## ESTRUTURA TÉCNICA DETALHADA

### Backend (Flask)

#### Módulos Principais
```python
# app.py - Ponto de entrada
from flask import Flask
from backend.api.routes import api_bp
from backend.config.settings import Config

# backend/api/routes.py - Endpoints
@api_bp.route('/status')
@api_bp.route('/metrics')
@api_bp.route('/tickets')
@api_bp.route('/equipment')

# backend/services/glpi_service.py - Integração GLPI
class GLPIService:
    def authenticate()
    def get_tickets()
    def get_equipment()
    def get_metrics()
```

#### Configurações Críticas
```python
# .env
GLPI_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
GLPI_USER_TOKEN=xxx
GLPI_APP_TOKEN=xxx
API_KEY=xxx
FLASK_ENV=development
PORT=5000
```

### Frontend (React + TypeScript)

#### Estrutura de Componentes
```typescript
// src/App.tsx - Componente principal
import Dashboard from './components/Dashboard'
import { ApiProvider } from './contexts/ApiContext'

// src/components/Dashboard.tsx - Dashboard principal
interface DashboardProps {
  data: DashboardData
  loading: boolean
  error: string | null
}

// src/services/httpClient.ts - Cliente HTTP
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
```

#### Configurações Críticas
```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:5000/api

# frontend/src/config/constants.ts
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
}
```

## PADRÕES DE CÓDIGO ESTABELECIDOS

### Backend

#### Estrutura de Resposta
```python
# Padrão de resposta da API
{
    "success": True,
    "data": {...},
    "message": "Operação realizada com sucesso",
    "timestamp": "2025-01-15T10:30:00Z"
}

# Padrão de erro
{
    "success": False,
    "error": "Descrição do erro",
    "code": "ERROR_CODE",
    "timestamp": "2025-01-15T10:30:00Z"
}
```

#### Logging
```python
# Padrão de logging estruturado
logger.info("Operação realizada", extra={
    "module": "glpi_service",
    "function": "get_tickets",
    "user_id": user_id,
    "duration": duration
})
```

### Frontend

#### Hooks Customizados
```typescript
// Padrão para hooks de dados
const useApiData = <T>(endpoint: string) => {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Lógica de fetch...
  
  return { data, loading, error, refetch }
}
```

#### Componentes
```typescript
// Padrão para componentes
interface ComponentProps {
  data: DataType
  onAction?: (item: DataType) => void
  className?: string
}

const Component: React.FC<ComponentProps> = ({ data, onAction, className }) => {
  // Implementação...
}

export default Component
```

## FUNCIONALIDADES IMPLEMENTADAS

### Dashboard Principal
- **Status Geral**: Indicadores de saúde do sistema
- **Métricas de Tickets**: Contadores por status, prioridade, categoria
- **Equipamentos**: Listagem e estatísticas de equipamentos
- **Gráficos**: Visualizações de dados temporais
- **Filtros**: Por data, categoria, status

### Componentes Funcionais
- ✅ StatusCard - Cards de status com métricas
- ✅ TicketList - Lista de tickets com paginação
- ✅ EquipmentGrid - Grid de equipamentos
- ✅ MetricsChart - Gráficos de métricas
- ✅ FilterPanel - Painel de filtros
- ❌ StatusByLevel - **PROBLEMA CONHECIDO**: Total de status por nível não funciona

## PROBLEMAS CONHECIDOS E SOLUÇÕES

### 1. Total de Status por Nível (Não Funcional)
```typescript
// Componente problemático
// src/components/StatusByLevel.tsx
// Problema: Dados não estão sendo agrupados corretamente
// Solução necessária: Revisar lógica de agrupamento no backend
```

### 2. Autenticação GLPI
```python
# Warning conhecido nos logs
# "Falha na autenticação com GLPI"
# Sistema funciona com cache/fallback
# Não é crítico para funcionamento
```

### 3. Configuração de Portas
```bash
# Problema recorrente: Mismatch de portas
# Backend: 5000
# Frontend: 5173
# API URL deve ser: http://localhost:5000/api
```

## DEPENDÊNCIAS CRÍTICAS

### Backend
```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.9"
flask = "^2.3.0"
requests = "^2.31.0"
redis = "^4.6.0"
pydantic = "^2.0.0"
```

### Frontend
```json
// package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "axios": "^1.4.0"
  }
}
```

## FLUXO DE DADOS

### 1. Inicialização
```
Frontend (React) → httpClient → Backend (Flask) → GLPI API
                ←             ←                ←
```

### 2. Atualização de Dados
```
Timer/User Action → useApiData Hook → API Call → Cache Check → GLPI/Database
                  ←                 ←          ←             ←
```

### 3. Renderização
```
API Response → State Update → Component Re-render → UI Update
```

## COMANDOS DE DESENVOLVIMENTO

### Inicialização
```bash
# Backend
cd backend
python app.py

# Frontend
cd frontend
npm run dev
```

### Build e Deploy
```bash
# Frontend
npm run build
npm run preview

# Backend
python -m pytest  # Se testes existirem
```

### Debug
```bash
# Logs do backend
tail -f logs/app.log

# Console do frontend
# F12 no navegador

# API testing
curl http://localhost:5000/api/status
```

## ESTILO E UI

### Tema e Cores
```css
/* Paleta principal */
:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --background: #f8fafc;
  --surface: #ffffff;
}
```

### Componentes de UI
- Cards responsivos com sombras sutis
- Tabelas com hover e seleção
- Botões com estados visuais
- Loading states e skeletons
- Tooltips informativos
- Modais para detalhes

## METAS DE DESENVOLVIMENTO

### Curto Prazo
1. ✅ Estabilizar sistema atual
2. ❌ Corrigir "Total de Status por Nível"
3. ⏳ Melhorar tratamento de erros
4. ⏳ Otimizar performance

### Médio Prazo
1. Implementar testes automatizados
2. Melhorar documentação
3. Adicionar mais visualizações
4. Implementar notificações

### Longo Prazo
1. PWA (Progressive Web App)
2. Dashboard customizável
3. Relatórios exportáveis
4. Integração com outros sistemas

---

**NOTA IMPORTANTE**: Este contexto deve ser consultado antes de qualquer modificação significativa no código. Ele representa o conhecimento acumulado sobre o projeto e deve ser mantido atualizado conforme o sistema evolui.