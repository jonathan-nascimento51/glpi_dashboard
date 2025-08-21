import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Tipos de dados que podem ser clicados nos gráficos
 */
export interface ChartDataPoint {
  type: 'ticket' | 'technician' | 'category' | 'status' | 'priority' | 'level' | 'general';
  id?: string | number;
  value?: number;
  name?: string;
  filters?: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * Hook para navegação em gráficos com drill-down
 * Permite navegar para páginas de detalhe baseado no tipo de dados clicados
 */
export const useChartNavigation = () => {
  const navigate = useNavigate();

  /**
   * Manipula cliques em elementos de gráfico
   * @param dataPoint - Dados do ponto clicado no gráfico
   */
  const handleChartClick = useCallback(
    (dataPoint: ChartDataPoint) => {
      const { type, id, filters, name, value } = dataPoint;

      // Log para debug
      console.log('Chart click:', { type, id, name, value, filters });

      switch (type) {
        case 'ticket':
          if (id) {
            navigate(`/tickets/${id}`);
          }
          break;

        case 'technician':
          if (id) {
            navigate(`/technicians/${id}`);
          } else if (name) {
            // Navegar para dashboard filtrado por técnico
            navigate(`/dashboard?technician=${encodeURIComponent(name)}`);
          }
          break;

        case 'category':
          if (id) {
            navigate(`/dashboard?category=${id}`);
          } else if (name) {
            navigate(`/dashboard?category=${encodeURIComponent(name)}`);
          }
          break;

        case 'status':
          if (name) {
            navigate(`/dashboard?status=${encodeURIComponent(name)}`);
          }
          break;

        case 'priority':
          if (name) {
            navigate(`/dashboard?priority=${encodeURIComponent(name)}`);
          }
          break;

        case 'level':
          if (name) {
            navigate(`/dashboard?level=${encodeURIComponent(name)}`);
          }
          break;

        case 'general':
        default:
          // Para casos gerais, navegar com filtros customizados
          if (filters && Object.keys(filters).length > 0) {
            const searchParams = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
              if (value !== null && value !== undefined && value !== '') {
                searchParams.append(key, String(value));
              }
            });
            navigate(`/dashboard?${searchParams.toString()}`);
          } else {
            // Fallback: navegar para página de detalhes gerais
            navigate('/dashboard/details');
          }
          break;
      }
    },
    [navigate]
  );

  /**
   * Cria um handler de clique para um tipo específico de dados
   * @param type - Tipo de dados
   * @param additionalData - Dados adicionais para o clique
   */
  const createClickHandler = useCallback(
    (type: ChartDataPoint['type'], additionalData: Partial<ChartDataPoint> = {}) => {
      return (event: any, activeElements?: any[]) => {
        // Para gráficos do Recharts
        if (event && event.activePayload && event.activePayload.length > 0) {
          const payload = event.activePayload[0].payload;
          handleChartClick({
            type,
            name: payload.name || payload.label,
            value: payload.value,
            ...additionalData,
            ...payload,
          });
        }
        // Para gráficos do Chart.js
        else if (activeElements && activeElements.length > 0) {
          const element = activeElements[0];
          const datasetIndex = element.datasetIndex;
          const index = element.index;
          
          handleChartClick({
            type,
            id: index,
            ...additionalData,
          });
        }
        // Fallback para cliques diretos
        else {
          handleChartClick({
            type,
            ...additionalData,
          });
        }
      };
    },
    [handleChartClick]
  );

  /**
   * Verifica se um elemento de gráfico é clicável
   * @param dataPoint - Dados do ponto
   */
  const isClickable = useCallback((dataPoint: Partial<ChartDataPoint>) => {
    const { type, id, name, filters } = dataPoint;
    
    // Elementos são clicáveis se têm ID, nome ou filtros
    return Boolean(
      id ||
      name ||
      (filters && Object.keys(filters).length > 0) ||
      ['ticket', 'technician', 'category', 'status', 'priority', 'level'].includes(type as string)
    );
  }, []);

  return {
    handleChartClick,
    createClickHandler,
    isClickable,
  };
};

/**
 * Utilitário para criar dados de drill-down para diferentes tipos de gráfico
 */
export const createDrillDownData = {
  /**
   * Para gráficos de status de tickets
   */
  ticketStatus: (statusName: string): ChartDataPoint => ({
    type: 'status',
    name: statusName,
    filters: { status: statusName },
  }),

  /**
   * Para gráficos de técnicos
   */
  technician: (technicianName: string, technicianId?: string): ChartDataPoint => ({
    type: 'technician',
    id: technicianId,
    name: technicianName,
    filters: { technician: technicianName },
  }),

  /**
   * Para gráficos de categorias
   */
  category: (categoryName: string, categoryId?: string): ChartDataPoint => ({
    type: 'category',
    id: categoryId,
    name: categoryName,
    filters: { category: categoryName },
  }),

  /**
   * Para gráficos de prioridade
   */
  priority: (priorityName: string): ChartDataPoint => ({
    type: 'priority',
    name: priorityName,
    filters: { priority: priorityName },
  }),

  /**
   * Para gráficos de nível
   */
  level: (levelName: string): ChartDataPoint => ({
    type: 'level',
    name: levelName,
    filters: { level: levelName },
  }),

  /**
   * Para dados gerais com filtros customizados
   */
  general: (filters: Record<string, any>): ChartDataPoint => ({
    type: 'general',
    filters,
  }),
};