import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

// Interfaces para os dados de manutenção
export interface MaintenanceMetrics {
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  total: number;
  niveis: {
    n1: { novos: number; pendentes: number; progresso: number; resolvidos: number };
    n2: { novos: number; pendentes: number; progresso: number; resolvidos: number };
    n3: { novos: number; pendentes: number; progresso: number; resolvidos: number };
    n4: { novos: number; pendentes: number; progresso: number; resolvidos: number };
  };
  tendencias: {
    novos: string;
    pendentes: string;
    progresso: string;
    resolvidos: string;
  };
  maintenance_context: {
    total_categories: number;
    critical_categories: number;
    avg_resolution_time: number;
  };
  technical_groups_summary: {
    total_groups: number;
    avg_efficiency_target: number;
  };
}

export interface MaintenanceCategory {
  id: string;
  name: string;
  completeName: string;
  ticketCount: number;
  avgResolutionTime: number;
  priority: 'Alta' | 'Média' | 'Baixa';
  status: 'Crítico' | 'Normal' | 'Baixo';
  subcategories: string[];
}

export interface TechnicalGroup {
  id: string;
  name: string;
  activeTickets: number;
  resolvedTickets: number;
  totalTickets: number;
  efficiency: number;
  category: string;
}

export interface MaintenanceCategoriesData {
  categories: MaintenanceCategory[];
  summary: {
    totalTickets: number;
    avgResolutionTime: number;
    criticalCategories: number;
    highPriorityCategories: number;
  };
}

export interface TechnicalGroupsData {
  groups: TechnicalGroup[];
  summary: {
    totalGroups: number;
    totalActiveTickets: number;
    totalResolvedTickets: number;
    avgEfficiency: number;
  };
}

export interface DashboardSummary {
  overview: {
    total_tickets: number;
    active_tickets: number;
    resolved_tickets: number;
    categories_count: number;
    groups_count: number;
  };
  performance_indicators: {
    avg_resolution_time: number;
    avg_group_efficiency: number;
    critical_categories: number;
    high_priority_categories: number;
  };
  alerts: Array<{
    type: 'warning' | 'info' | 'error';
    message: string;
    priority: 'Alta' | 'Média' | 'Baixa';
  }>;
  recommendations: string[];
  timestamp: string;
}

export interface DateRange {
  startDate?: string;
  endDate?: string;
}

// Hook principal para o dashboard de manutenção
export const useMaintenanceDashboard = (dateRange?: DateRange) => {
  const [metrics, setMetrics] = useState<MaintenanceMetrics | null>(null);
  const [categories, setCategories] = useState<MaintenanceCategoriesData | null>(null);
  const [groups, setGroups] = useState<TechnicalGroupsData | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMaintenanceMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (dateRange?.startDate) params.append('start_date', dateRange.startDate);
      if (dateRange?.endDate) params.append('end_date', dateRange.endDate);

      const response = await api.get(`/maintenance/metrics?${params.toString()}`);
      
      if (response.data.success) {
        setMetrics(response.data.data);
      } else {
        throw new Error(response.data.message || 'Erro ao carregar métricas de manutenção');
      }
    } catch (err) {
      console.error('Erro ao buscar métricas de manutenção:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  }, [dateRange]);

  const fetchMaintenanceCategories = useCallback(async () => {
    try {
      const response = await api.get('/maintenance/categories');
      
      if (response.data.success) {
        setCategories(response.data.data);
      } else {
        throw new Error(response.data.message || 'Erro ao carregar categorias de manutenção');
      }
    } catch (err) {
      console.error('Erro ao buscar categorias de manutenção:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  }, []);

  const fetchTechnicalGroups = useCallback(async () => {
    try {
      const response = await api.get('/maintenance/groups');
      
      if (response.data.success) {
        setGroups(response.data.data);
      } else {
        throw new Error(response.data.message || 'Erro ao carregar grupos técnicos');
      }
    } catch (err) {
      console.error('Erro ao buscar grupos técnicos:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  }, []);

  const fetchDashboardSummary = useCallback(async () => {
    try {
      const response = await api.get('/maintenance/dashboard/summary');
      
      if (response.data.success) {
        setSummary(response.data.data);
      } else {
        throw new Error(response.data.message || 'Erro ao carregar resumo do dashboard');
      }
    } catch (err) {
      console.error('Erro ao buscar resumo do dashboard:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    }
  }, []);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await Promise.all([
        fetchMaintenanceMetrics(),
        fetchMaintenanceCategories(),
        fetchTechnicalGroups(),
        fetchDashboardSummary()
      ]);
    } catch (err) {
      console.error('Erro ao carregar dados do dashboard:', err);
      setError('Erro ao carregar dados do dashboard de manutenção');
    } finally {
      setLoading(false);
    }
  }, [fetchMaintenanceMetrics, fetchMaintenanceCategories, fetchTechnicalGroups, fetchDashboardSummary]);

  const refreshData = useCallback(() => {
    fetchAllData();
  }, [fetchAllData]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  return {
    // Dados
    metrics,
    categories,
    groups,
    summary,
    
    // Estados
    loading,
    error,
    
    // Ações
    refreshData,
    fetchMaintenanceMetrics,
    fetchMaintenanceCategories,
    fetchTechnicalGroups,
    fetchDashboardSummary
  };
};

// Hook específico para detalhes de categoria
export const useCategoryDetails = (categoryId: string) => {
  const [categoryDetails, setCategoryDetails] = useState<MaintenanceCategory & {
    trends: {
      last_week: string;
      last_month: string;
      resolution_trend: string;
    };
    recommendations: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCategoryDetails = useCallback(async () => {
    if (!categoryId) return;

    try {
      setLoading(true);
      setError(null);

      const response = await api.get(`/maintenance/categories/${categoryId}/details`);
      
      if (response.data.success) {
        setCategoryDetails(response.data.data);
      } else {
        throw new Error(response.data.message || 'Erro ao carregar detalhes da categoria');
      }
    } catch (err) {
      console.error('Erro ao buscar detalhes da categoria:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [categoryId]);

  useEffect(() => {
    fetchCategoryDetails();
  }, [fetchCategoryDetails]);

  return {
    categoryDetails,
    loading,
    error,
    refetch: fetchCategoryDetails
  };
};

// Hook específico para detalhes de grupo técnico
export const useGroupPerformance = (groupId: string) => {
  const [groupPerformance, setGroupPerformance] = useState<TechnicalGroup & {
    detailed_metrics: {
      avg_response_time: string;
      avg_resolution_time: string;
      customer_satisfaction: string;
      sla_compliance: string;
    };
    recent_activity: Array<{
      date: string;
      action: string;
      category: string;
    }>;
    performance_trends: {
      efficiency_trend: string;
      workload_trend: string;
      quality_trend: string;
    };
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGroupPerformance = useCallback(async () => {
    if (!groupId) return;

    try {
      setLoading(true);
      setError(null);

      const response = await api.get(`/maintenance/groups/${groupId}/performance`);
      
      if (response.data.success) {
        setGroupPerformance(response.data.data);
      } else {
        throw new Error(response.data.message || 'Erro ao carregar performance do grupo');
      }
    } catch (err) {
      console.error('Erro ao buscar performance do grupo:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    fetchGroupPerformance();
  }, [fetchGroupPerformance]);

  return {
    groupPerformance,
    loading,
    error,
    refetch: fetchGroupPerformance
  };
};

export default useMaintenanceDashboard;