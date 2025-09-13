# 🎯 PLANO DE MIGRAÇÃO: NOVO FRONTEND FIGMA

## 📋 **ANÁLISE DO NOVO FRONTEND (src/)**

### **Características Identificadas:**
- **Framework**: React + TypeScript + Vite
- **UI Library**: shadcn/ui (componentes modernos)
- **Estilização**: TailwindCSS
- **Cor Principal**: #5A9BD4 (azul corporativo)
- **Ícones**: Lucide React
- **Layout**: Grid responsivo com sidebar de tickets

### **Componentes Principais no App.tsx:**
1. **Header** (linhas 24-64)
   - Logo "Dashboard GLPI"
   - Busca global
   - Notificações
   - Perfil do usuário

2. **Cards de Métricas Gerais** (linhas 72-128)
   - Novos: 3 (hardcoded)
   - Em Progresso: 45 (hardcoded)
   - Pendentes: 26 (hardcoded)
   - Resolvidos: 10.2K (hardcoded)

3. **Cards de Níveis N1-N4** (linhas 131-311)
   - N1 Total: 1.495 (hardcoded)
   - N2 Total: 1.266 (hardcoded)
   - N3 Total: 5.262 (hardcoded)
   - N4 Total: 42 (hardcoded)

4. **Ranking de Técnicos** (linhas 314-396)
   - Top 4 técnicos com gradientes coloridos
   - Dados hardcoded

5. **Lista de Tickets Novos** (linhas 400-465)
   - 8 tickets listados
   - Scroll customizado

---

## 🔄 **MAPEAMENTO DE SUBSTITUIÇÕES**

### **1. Dados Hardcoded → API Real**

| **Componente** | **Valor Atual (Hardcoded)** | **Substituir Por (API)** | **Endpoint** |
|----------------|------------------------------|---------------------------|--------------|
| **MÉTRICAS GERAIS** |
| Novos | `3` | `metrics.niveis.geral.novos` | `/api/metrics` |
| Em Progresso | `45` | `metrics.niveis.geral.progresso` | `/api/metrics` |
| Pendentes | `26` | `metrics.niveis.geral.pendentes` | `/api/metrics` |
| Resolvidos | `10.2K` | `metrics.niveis.geral.resolvidos` | `/api/metrics` |
| **NÍVEL N1** |
| Total | `1.495` | `metrics.niveis.n1.total` | `/api/metrics` |
| Novos | `1` | `metrics.niveis.n1.novos` | `/api/metrics` |
| Em Progresso | `8` | `metrics.niveis.n1.progresso` | `/api/metrics` |
| Pendentes | `3` | `metrics.niveis.n1.pendentes` | `/api/metrics` |
| Resolvidos | `1.483` | `metrics.niveis.n1.resolvidos` | `/api/metrics` |
| **NÍVEL N2** |
| Total | `1.266` | `metrics.niveis.n2.total` | `/api/metrics` |
| Novos | `0` | `metrics.niveis.n2.novos` | `/api/metrics` |
| Em Progresso | `11` | `metrics.niveis.n2.progresso` | `/api/metrics` |
| Pendentes | `11` | `metrics.niveis.n2.pendentes` | `/api/metrics` |
| Resolvidos | `1.244` | `metrics.niveis.n2.resolvidos` | `/api/metrics` |
| **NÍVEL N3** |
| Total | `5.262` | `metrics.niveis.n3.total` | `/api/metrics` |
| Novos | `1` | `metrics.niveis.n3.novos` | `/api/metrics` |
| Em Progresso | `21` | `metrics.niveis.n3.progresso` | `/api/metrics` |
| Pendentes | `9` | `metrics.niveis.n3.pendentes` | `/api/metrics` |
| Resolvidos | `5.231` | `metrics.niveis.n3.resolvidos` | `/api/metrics` |
| **NÍVEL N4** |
| Total | `42` | `metrics.niveis.n4.total` | `/api/metrics` |
| Novos | `0` | `metrics.niveis.n4.novos` | `/api/metrics` |
| Em Progresso | `1` | `metrics.niveis.n4.progresso` | `/api/metrics` |
| Pendentes | `1` | `metrics.niveis.n4.pendentes` | `/api/metrics` |
| Resolvidos | `40` | `metrics.niveis.n4.resolvidos` | `/api/metrics` |
| **RANKING** |
| #1 Nome | `Roberlâncio O.` | `ranking[0].name` | `/api/technicians/ranking` |
| #1 Total | `2.723` | `ranking[0].total` | `/api/technicians/ranking` |
| #1 Resolvidos | `2.710` | `ranking[0].ticketsResolved` | `/api/technicians/ranking` |
| **TICKETS** |
| Lista | Tickets hardcoded | `tickets[]` | `/api/tickets/new?limit=8` |

---

## 📦 **ARQUIVOS A CRIAR NO NOVO FRONTEND**

### **1. Estrutura de Pastas**
```
src/
├── components/       (já existe)
├── services/        (CRIAR)
│   ├── api.ts
│   ├── httpClient.ts
│   └── cache.ts
├── hooks/           (CRIAR)
│   ├── useMetrics.ts
│   ├── useRanking.ts
│   └── useTickets.ts
├── types/           (CRIAR)
│   └── api.ts
├── config/          (CRIAR)
│   └── constants.ts
└── utils/           (CRIAR)
    └── formatters.ts
```

### **2. Arquivos Essenciais**

#### **src/services/httpClient.ts**
```typescript
import axios from 'axios';

export const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 30000,
};

export const httpClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});
```

#### **src/types/api.ts**
```typescript
export interface LevelMetrics {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
}

export interface DashboardMetrics {
  niveis: {
    n1: LevelMetrics;
    n2: LevelMetrics;
    n3: LevelMetrics;
    n4: LevelMetrics;
    geral: LevelMetrics;
  };
  tendencias: {
    novos: string;
    pendentes: string;
    progresso: string;
    resolvidos: string;
  };
}

export interface TechnicianRanking {
  id: string;
  name: string;
  level: string;
  rank: number;
  total: number;
  ticketsResolved?: number;
}

export interface NewTicket {
  id: string;
  title: string;
  description: string;
  date: string;
  requester: string;
  priority: string;
  status: string;
}
```

#### **src/hooks/useMetrics.ts**
```typescript
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { DashboardMetrics } from '../types/api';

export function useMetrics() {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await apiService.getMetrics();
        setData(response);
      } catch (err) {
        setError('Erro ao carregar métricas');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh a cada 30s
    
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error };
}
```

---

## 🛠️ **MODIFICAÇÕES NO App.tsx**

### **1. Imports Necessários**
```typescript
// Adicionar no topo do App.tsx
import { useMetrics } from './hooks/useMetrics';
import { useRanking } from './hooks/useRanking';
import { useTickets } from './hooks/useTickets';
```

### **2. Hook de Dados**
```typescript
export default function App() {
  const { data: metrics, loading: metricsLoading } = useMetrics();
  const { data: ranking, loading: rankingLoading } = useRanking();
  const { data: tickets, loading: ticketsLoading } = useTickets();

  // Loading state
  if (metricsLoading) {
    return <div>Carregando dashboard...</div>;
  }
```

### **3. Substituições de Valores**

#### **Métricas Gerais (linha 78)**
```typescript
// DE:
<p className="text-2xl font-semibold text-gray-900">3</p>

// PARA:
<p className="text-2xl font-semibold text-gray-900">
  {metrics?.niveis.geral.novos || 0}
</p>
```

#### **Métricas N1 (linha 141)**
```typescript
// DE:
<span className="text-xl font-semibold text-gray-900">1.495</span>

// PARA:
<span className="text-xl font-semibold text-gray-900">
  {metrics?.niveis.n1.total || 0}
</span>
```

#### **Ranking (linha 326)**
```typescript
// DE:
<p className="text-xs font-medium mb-1">Roberlâncio O.</p>

// PARA:
<p className="text-xs font-medium mb-1">
  {ranking?.[0]?.name || 'Carregando...'}
</p>
```

#### **Tickets (linha 424)**
```typescript
// DE: (tickets hardcoded)
// PARA:
{tickets?.map((ticket) => (
  <div key={ticket.id} className="border-l-4 border-[#5A9BD4] bg-[#5A9BD4]/5 p-3 rounded-r-lg">
    <div className="flex items-center justify-between mb-2">
      <span className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded">
        #{ticket.id}
      </span>
      <Badge variant="outline" className="border-[#5A9BD4] text-[#5A9BD4] bg-[#5A9BD4]/10 text-xs">
        {ticket.status}
      </Badge>
    </div>
    <h4 className="font-medium text-gray-900 mb-2 text-sm">{ticket.title}</h4>
    <p className="text-xs text-gray-600 mb-2 line-clamp-2">{ticket.description}</p>
    <div className="flex items-center justify-between text-xs">
      <span className="text-gray-700 font-medium">{ticket.requester}</span>
      <span className="text-gray-500">{ticket.date}</span>
    </div>
  </div>
))}
```

---

## 📝 **CONFIGURAÇÕES NECESSÁRIAS**

### **1. package.json**
```json
{
  "name": "glpi-dashboard-figma",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "lucide-react": "^0.300.0",
    "class-variance-authority": "^0.7.0",
    "@radix-ui/react-slot": "^1.0.2",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.31"
  }
}
```

### **2. vite.config.ts**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

### **3. tsconfig.json**
```json
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

---

## 🚀 **PLANO DE EXECUÇÃO**

### **FASE 1: Setup Inicial (15 min)**
1. ✅ Mover `src/` para `frontend-novo/`
2. ✅ Criar `package.json`, `vite.config.ts`, `tsconfig.json`
3. ✅ Instalar dependências
4. ✅ Testar build inicial

### **FASE 2: Integração API (30 min)**
1. ✅ Criar `/services` com httpClient e api.ts
2. ✅ Criar `/types` com interfaces TypeScript
3. ✅ Criar `/hooks` para useMetrics, useRanking, useTickets
4. ✅ Configurar proxy no Vite

### **FASE 3: Substituição de Dados (45 min)**
1. ✅ Importar hooks no App.tsx
2. ✅ Substituir valores hardcoded por dados da API
3. ✅ Adicionar loading states
4. ✅ Adicionar tratamento de erros

### **FASE 4: Testes e Validação (20 min)**
1. ✅ Verificar conexão com backend
2. ✅ Validar dados exibidos (214 N1, 107 N2, etc.)
3. ✅ Testar refresh automático
4. ✅ Verificar responsividade

### **FASE 5: Deploy (10 min)**
1. ✅ Build de produção
2. ✅ Substituir frontend atual
3. ✅ Validação final

---

## ✅ **CHECKLIST DE VALIDAÇÃO**

### **Conectividade**
- [ ] Proxy `/api` → `localhost:8000` funcionando
- [ ] Requisições chegando ao backend
- [ ] CORS configurado corretamente
- [ ] Dados reais sendo recebidos

### **Dados Exibidos**
- [ ] Métricas gerais corretas
- [ ] N1: 214 tickets (real)
- [ ] N2: 107 tickets (real)
- [ ] N3: 52 tickets (real)
- [ ] N4: 13 tickets (real)
- [ ] Ranking de técnicos carregado
- [ ] Tickets novos listados

### **Interface**
- [ ] Design do Figma preservado
- [ ] Cores #5A9BD4 mantidas
- [ ] Gradientes no ranking funcionando
- [ ] Scroll customizado nos tickets
- [ ] Responsividade mantida

### **Performance**
- [ ] Loading states funcionando
- [ ] Refresh automático (30s)
- [ ] Cache ativo
- [ ] Sem vazamentos de memória

---

## 🎯 **RESULTADO ESPERADO**

Após a migração, o novo frontend do Figma estará:
1. **100% conectado** com a API do backend
2. **Exibindo dados reais** do GLPI (214 N1, 107 N2, etc.)
3. **Mantendo o design** moderno do Figma
4. **Funcionando perfeitamente** no ambiente Replit
5. **Pronto para produção** com todas as funcionalidades

---

## 📌 **OBSERVAÇÕES IMPORTANTES**

1. **Preservar Design**: Manter todas as cores, gradientes e estilos do Figma
2. **Dados Mock para Dev**: Manter opção de dados mock para desenvolvimento
3. **Componentes Reutilizáveis**: Extrair cards repetidos em componentes
4. **TypeScript Strict**: Manter tipagem forte em todo o código
5. **Performance**: Implementar lazy loading para componentes pesados