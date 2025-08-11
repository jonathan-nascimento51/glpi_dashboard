import { z } from 'zod';

// Schema base para validação de dados
export const TicketStatusSchema = z.enum(['new', 'progress', 'pending', 'resolved']);
export const ThemeSchema = z.enum(['light', 'dark']);
export const PrioritySchema = z.enum(['high', 'medium', 'low']);
export const PeriodSchema = z.enum(['today', 'week', 'month']);

// Schema para métricas de nível
export const LevelMetricsSchema = z.object({
  novos: z.number().min(0).default(0),
  progresso: z.number().min(0).default(0),
  pendentes: z.number().min(0).default(0),
  resolvidos: z.number().min(0).default(0),
  tendencia_novos: z.number().default(0),
  tendencia_progresso: z.number().default(0),
  tendencia_pendentes: z.number().default(0),
  tendencia_resolvidos: z.number().default(0),
});

// Schema para dados de métricas completos
export const MetricsDataSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  timestamp: z.string(),
  tempo_execucao: z.number().min(0),
  data: z.object({
    niveis: z.object({
      N1: LevelMetricsSchema,
      N2: LevelMetricsSchema,
      N3: LevelMetricsSchema,
      N4: LevelMetricsSchema,
    }),
  }).optional(),
  niveis: z.object({
    N1: LevelMetricsSchema,
    N2: LevelMetricsSchema,
    N3: LevelMetricsSchema,
    N4: LevelMetricsSchema,
  }).optional(),
}).refine(data => data.niveis || (data.data && data.data.niveis), {
  message: "Either 'niveis' or 'data.niveis' must be provided",
});

// Schema para ranking de técnicos
export const TechnicianRankingSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  nome: z.string().optional(),
  level: z.string(),
  rank: z.number().min(1),
  total: z.number().min(0),
  score: z.number().min(0).optional(),
  ticketsResolved: z.number().min(0).optional(),
  ticketsInProgress: z.number().min(0).optional(),
  averageResolutionTime: z.number().min(0).optional(),
}).refine(data => data.name || data.nome, {
  message: "Either 'name' or 'nome' must be provided",
});

// Schema para novos tickets
export const NewTicketSchema = z.object({
  id: z.string(),
  title: z.string().min(1, "Title is required"),
  description: z.string(),
  date: z.string(),
  requester: z.string().min(1, "Requester is required"),
  priority: z.string(),
  status: z.string(),
});

// Schema para status do sistema
export const SystemStatusSchema = z.object({
  api_status: z.string(),
  database_status: z.string(),
  glpi_connection: z.boolean(),
  ultima_atualizacao: z.string().optional(),
});

// Schema para filtros
export const FilterStateSchema = z.object({
  period: PeriodSchema,
  levels: z.array(z.string()),
  status: z.array(TicketStatusSchema),
  priority: z.array(PrioritySchema),
  dateRange: z.object({
    startDate: z.string(),
    endDate: z.string(),
    label: z.string(),
    start: z.date().optional(),
    end: z.date().optional(),
  }).optional(),
});

// Schema para notificações
export const NotificationDataSchema = z.object({
  id: z.string(),
  title: z.string().min(1, "Title is required"),
  message: z.string().min(1, "Message is required"),
  type: z.enum(['success', 'error', 'warning', 'info']),
  timestamp: z.date(),
  duration: z.number().min(0).optional(),
});

// Funções de validação com fallbacks seguros
export const validateMetricsData = (data: unknown): MetricsData => {
  try {
    const parsed = MetricsDataSchema.parse(data);
    // Normalizar dados - priorizar niveis direto sobre data.niveis
    const normalizedData = {
      ...parsed,
      niveis: parsed.niveis || (parsed.data?.niveis) || getDefaultNiveis(),
    };
    return normalizedData as MetricsData;
  } catch (error) {
    console.error('Validation error for MetricsData:', error);
    // Fallback seguro
    return {
      success: false,
      message: 'Invalid data received',
      timestamp: new Date().toISOString(),
      tempo_execucao: 0,
      niveis: getDefaultNiveis(),
    };
  }
};

const getDefaultNiveis = () => ({
  N1: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
  N2: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
  N3: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
  N4: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
});

export const validateTechnicianRanking = (data: unknown[]): TechnicianRanking[] => {
  try {
    return z.array(TechnicianRankingSchema).parse(data);
  } catch (error) {
    console.error('Validation error for TechnicianRanking:', error);
    return [];
  }
};

export const validateSystemStatus = (data: unknown): SystemStatus => {
  try {
    return SystemStatusSchema.parse(data);
  } catch (error) {
    console.error('Validation error for SystemStatus:', error);
    return {
      api_status: 'unknown',
      database_status: 'unknown',
      glpi_connection: false,
    };
  }
};

// Type guards para verificação de tipos em runtime
export const isValidMetricsData = (data: unknown): data is MetricsData => {
  return MetricsDataSchema.safeParse(data).success;
};

export const isValidTechnicianRanking = (data: unknown): data is TechnicianRanking[] => {
  return z.array(TechnicianRankingSchema).safeParse(data).success;
};

export const isValidSystemStatus = (data: unknown): data is SystemStatus => {
  return SystemStatusSchema.safeParse(data).success;
};

// Importar tipos existentes
import type {
  MetricsData,
  TechnicianRanking,
  SystemStatus,
  TicketStatus,
  Theme,
  FilterState,
  NotificationData,
} from './index';
