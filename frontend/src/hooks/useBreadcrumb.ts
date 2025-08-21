import { useMemo } from 'react';
// import { useLocation } from 'react-router-dom';
import { BreadcrumbItem } from '@/components/ui/Breadcrumb';
import { BarChart3, Users, Settings, FileText, AlertTriangle, CheckCircle, Clock, Ticket } from 'lucide-react';

// Mapeamento de rotas para labels e ícones personalizados
const ROUTE_CONFIG: Record<string, { label: string; icon?: React.ComponentType<{ className?: string }> }> = {
  '': { label: 'Dashboard', icon: BarChart3 },
  'dashboard': { label: 'Dashboard', icon: BarChart3 },
  'tickets': { label: 'Tickets', icon: Ticket },
  'technicians': { label: 'Técnicos', icon: Users },
  'reports': { label: 'Relatórios', icon: FileText },
  'settings': { label: 'Configurações', icon: Settings },
  'new': { label: 'Novos', icon: AlertTriangle },
  'pending': { label: 'Pendentes', icon: Clock },
  'progress': { label: 'Em Progresso', icon: Clock },
  'resolved': { label: 'Resolvidos', icon: CheckCircle },
  'details': { label: 'Detalhes' },
  'edit': { label: 'Editar' },
  'create': { label: 'Criar' },
  'view': { label: 'Visualizar' },
};

// Rotas que devem ser ignoradas nos breadcrumbs
const IGNORED_ROUTES = ['api', 'auth', 'callback'];

// Função para normalizar segmentos de URL
function normalizeSegment(segment: string): string {
  return segment
    .toLowerCase()
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}

// Função para obter configuração de rota
function getRouteConfig(segment: string) {
  const config = ROUTE_CONFIG[segment.toLowerCase()];
  if (config) {
    return config;
  }
  
  // Se não encontrar configuração específica, tenta normalizar
  return {
    label: normalizeSegment(segment),
  };
}

// Função para determinar se um segmento deve ser linkável
function shouldBeClickable(segment: string, index: number, totalSegments: number): boolean {
  // O último segmento nunca é clicável (página atual)
  if (index === totalSegments - 1) {
    return false;
  }
  
  // IDs numéricos geralmente não são clicáveis
  if (/^\d+$/.test(segment)) {
    return false;
  }
  
  // Segmentos ignorados não são clicáveis
  if (IGNORED_ROUTES.includes(segment.toLowerCase())) {
    return false;
  }
  
  return true;
}

export interface UseBreadcrumbOptions {
  /** Incluir ícone de home no primeiro item */
  showHomeIcon?: boolean;
  /** Máximo de itens a exibir (trunca no meio se necessário) */
  maxItems?: number;
  /** Rota base personalizada (padrão: '/') */
  basePath?: string;
  /** Mapeamento personalizado de rotas */
  customRoutes?: Record<string, { label: string; icon?: React.ComponentType<{ className?: string }> }>;
}

export interface UseBreadcrumbReturn {
  /** Lista de itens do breadcrumb */
  items: BreadcrumbItem[];
  /** Caminho atual completo */
  currentPath: string;
  /** Segmentos do caminho */
  pathSegments: string[];
  /** Se está na página inicial */
  isHomePage: boolean;
}

/**
 * Hook para gerenciar breadcrumbs baseado na rota atual
 */
export function useBreadcrumb(options: UseBreadcrumbOptions = {}): UseBreadcrumbReturn {
  // const location = useLocation();
  const {
    showHomeIcon = true,
    maxItems,
    basePath = '/',
    customRoutes = {},
  } = options;

  const breadcrumbData = useMemo(() => {
    // Simulate current path for dashboard
    const currentPath = '/dashboard';
    const pathSegments = currentPath.split('/').filter(Boolean);
    const isHomePage = pathSegments.length === 0;

    // Combinar configurações de rota padrão com personalizadas
    const allRouteConfig = { ...ROUTE_CONFIG, ...customRoutes };

    // Construir itens do breadcrumb
    const items: BreadcrumbItem[] = [];

    // Adicionar item Home
    const homeConfig = allRouteConfig[''] || { label: 'Home' };
    items.push({
      label: homeConfig.label,
      href: basePath,
      icon: showHomeIcon ? homeConfig.icon : undefined,
    });

    // Adicionar segmentos do caminho
    pathSegments.forEach((segment, index) => {
      const config = getRouteConfig(segment);
      const href = basePath + pathSegments.slice(0, index + 1).join('/');
      const isClickable = shouldBeClickable(segment, index, pathSegments.length);

      items.push({
        label: config.label,
        href: isClickable ? href : undefined,
        icon: config.icon,
      });
    });

    // Aplicar truncamento se necessário
    let finalItems = items;
    if (maxItems && items.length > maxItems) {
      const start = items.slice(0, 1); // Home sempre visível
      const end = items.slice(-2); // Últimos 2 sempre visíveis
      const middle = items.length > 3 ? [{ label: '...', href: undefined }] : [];
      
      finalItems = [...start, ...middle, ...end];
    }

    return {
      items: finalItems,
      currentPath,
      pathSegments,
      isHomePage,
    };
  }, [location.pathname, showHomeIcon, maxItems, basePath, customRoutes]);

  return breadcrumbData;
}

/**
 * Hook simplificado para breadcrumbs básicos
 */
export function useSimpleBreadcrumb(): Pick<UseBreadcrumbReturn, 'items' | 'currentPath'> {
  const { items, currentPath } = useBreadcrumb();
  return { items, currentPath };
}

/**
 * Hook para breadcrumbs contextuais baseado em filtros ou estado
 */
export function useContextualBreadcrumb(context: {
  section?: string;
  filters?: Record<string, any>;
  entityId?: string | number;
  entityType?: string;
}): UseBreadcrumbReturn {
  const baseBreadcrumb = useBreadcrumb();
  const { section, filters, entityId, entityType } = context;

  const contextualItems = useMemo(() => {
    let items = [...baseBreadcrumb.items];

    // Adicionar seção se especificada
    if (section) {
      const config = getRouteConfig(section);
      items.push({
        label: config.label,
        href: `/${section}`,
        icon: config.icon,
      });
    }

    // Adicionar filtros ativos como contexto
    if (filters && Object.keys(filters).length > 0) {
      const activeFilters = Object.entries(filters)
        .filter(([_, value]) => value && value !== '')
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
      
      if (activeFilters) {
        items.push({
          label: `Filtros: ${activeFilters}`,
          href: undefined,
        });
      }
    }

    // Adicionar entidade específica
    if (entityId && entityType) {
      const config = getRouteConfig(entityType);
      items.push({
        label: `${config.label} #${entityId}`,
        href: undefined,
        icon: config.icon,
      });
    }

    return items;
  }, [baseBreadcrumb.items, section, filters, entityId, entityType]);

  return {
    ...baseBreadcrumb,
    items: contextualItems,
  };
}