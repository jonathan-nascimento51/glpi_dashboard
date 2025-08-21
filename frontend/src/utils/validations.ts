// Validações centralizadas da aplicação

import { VALIDATION_CONFIG } from '../config/constants';
import type { DashboardMetrics, Filters, DateRange } from '../types';

/**
 * Resultado de validação
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings?: string[];
}

/**
 * Valida métricas do dashboard
 */
export const validateDashboardMetrics = (metrics: any): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!metrics) {
    errors.push('Métricas não fornecidas');
    return { isValid: false, errors, warnings };
  }

  // Validar estrutura básica
  if (typeof metrics.totalTickets !== 'number' || metrics.totalTickets < 0) {
    errors.push('Total de tickets deve ser um número não negativo');
  }

  if (typeof metrics.openTickets !== 'number' || metrics.openTickets < 0) {
    errors.push('Tickets abertos deve ser um número não negativo');
  }

  if (typeof metrics.closedTickets !== 'number' || metrics.closedTickets < 0) {
    errors.push('Tickets fechados deve ser um número não negativo');
  }

  if (typeof metrics.averageResolutionTime !== 'number' || metrics.averageResolutionTime < 0) {
    errors.push('Tempo médio de resolução deve ser um número não negativo');
  }

  // Validações de consistência
  if (metrics.totalTickets !== (metrics.openTickets + metrics.closedTickets)) {
    warnings.push('Total de tickets não corresponde à soma de abertos e fechados');
  }

  // Validar distribuição por status
  if (metrics.statusDistribution) {
    const statusTotal = Object.values(metrics.statusDistribution).reduce(
      (sum: number, count: any) => sum + (typeof count === 'number' ? count : 0),
      0
    );
    
    if (statusTotal !== metrics.totalTickets) {
      warnings.push('Distribuição por status não corresponde ao total de tickets');
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
};

/**
 * Valida filtros de busca
 */
export const validateFilters = (filters: Partial<Filters>): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Validar query de busca
  if (filters.searchQuery) {
    if (filters.searchQuery.length < VALIDATION_CONFIG.MIN_SEARCH_LENGTH) {
      errors.push(`Busca deve ter pelo menos ${VALIDATION_CONFIG.MIN_SEARCH_LENGTH} caracteres`);
    }
    
    if (filters.searchQuery.length > VALIDATION_CONFIG.MAX_SEARCH_LENGTH) {
      errors.push(`Busca deve ter no máximo ${VALIDATION_CONFIG.MAX_SEARCH_LENGTH} caracteres`);
    }
  }

  // Validar range de datas
  if (filters.dateRange) {
    const dateValidation = validateDateRange(filters.dateRange);
    if (!dateValidation.isValid) {
      errors.push(...dateValidation.errors);
    }
    if (dateValidation.warnings) {
      warnings.push(...dateValidation.warnings);
    }
  }

  // Validar status
  if (filters.status && !isValidTicketStatus(filters.status)) {
    errors.push('Status de ticket inválido');
  }

  // Validar prioridade
  if (filters.priority !== undefined) {
    if (!Number.isInteger(filters.priority) || filters.priority < 1 || filters.priority > 6) {
      errors.push('Prioridade deve ser um número inteiro entre 1 e 6');
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
};

/**
 * Valida range de datas
 */
export const validateDateRange = (dateRange: DateRange): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!dateRange.startDate || !dateRange.endDate) {
    errors.push('Data de início e fim são obrigatórias');
    return { isValid: false, errors };
  }

  const startDate = new Date(dateRange.startDate);
  const endDate = new Date(dateRange.endDate);
  const now = new Date();

  // Validar se as datas são válidas
  if (isNaN(startDate.getTime())) {
    errors.push('Data de início inválida');
  }

  if (isNaN(endDate.getTime())) {
    errors.push('Data de fim inválida');
  }

  if (errors.length > 0) {
    return { isValid: false, errors };
  }

  // Validar ordem das datas
  if (startDate >= endDate) {
    errors.push('Data de início deve ser anterior à data de fim');
  }

  // Validar se as datas não são futuras
  if (startDate > now) {
    warnings.push('Data de início é futura');
  }

  if (endDate > now) {
    warnings.push('Data de fim é futura');
  }

  // Validar range máximo (1 ano)
  const maxRange = 365 * 24 * 60 * 60 * 1000; // 1 ano em ms
  if (endDate.getTime() - startDate.getTime() > maxRange) {
    warnings.push('Range de datas muito amplo (máximo recomendado: 1 ano)');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
};

/**
 * Valida se um status de ticket é válido
 */
export const isValidTicketStatus = (status: string): boolean => {
  const validStatuses = ['new', 'assigned', 'planned', 'waiting', 'solved', 'closed'];
  return validStatuses.includes(status);
};

/**
 * Valida configurações de cache
 */
export const validateCacheConfig = (config: any): ValidationResult => {
  const errors: string[] = [];

  if (typeof config.ttl !== 'number' || config.ttl < 0) {
    errors.push('TTL do cache deve ser um número não negativo');
  }

  if (typeof config.maxSize !== 'number' || config.maxSize < 1) {
    errors.push('Tamanho máximo do cache deve ser um número positivo');
  }

  if (config.strategy && !['lru', 'fifo', 'lfu'].includes(config.strategy)) {
    errors.push('Estratégia de cache inválida');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Valida dados de performance
 */
export const validatePerformanceData = (data: any): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!data) {
    errors.push('Dados de performance não fornecidos');
    return { isValid: false, errors };
  }

  // Validar métricas básicas
  if (typeof data.responseTime !== 'number' || data.responseTime < 0) {
    errors.push('Tempo de resposta deve ser um número não negativo');
  }

  if (typeof data.memoryUsage !== 'number' || data.memoryUsage < 0) {
    errors.push('Uso de memória deve ser um número não negativo');
  }

  if (typeof data.cpuUsage !== 'number' || data.cpuUsage < 0 || data.cpuUsage > 100) {
    errors.push('Uso de CPU deve ser um número entre 0 e 100');
  }

  // Avisos para valores suspeitos
  if (data.responseTime > 5000) {
    warnings.push('Tempo de resposta muito alto (>5s)');
  }

  if (data.cpuUsage > 80) {
    warnings.push('Uso de CPU muito alto (>80%)');
  }

  if (data.memoryUsage > 1024 * 1024 * 1024) { // 1GB
    warnings.push('Uso de memória muito alto (>1GB)');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
};

/**
 * Valida dados de ranking de técnicos
 */
export const validateTechnicianRanking = (ranking: any[]): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!Array.isArray(ranking)) {
    errors.push('Ranking deve ser um array');
    return { isValid: false, errors };
  }

  ranking.forEach((technician, index) => {
    if (!technician.name || typeof technician.name !== 'string') {
      errors.push(`Técnico ${index + 1}: nome é obrigatório`);
    }

    if (typeof technician.ticketsResolved !== 'number' || technician.ticketsResolved < 0) {
      errors.push(`Técnico ${index + 1}: tickets resolvidos deve ser um número não negativo`);
    }

    if (typeof technician.averageTime !== 'number' || technician.averageTime < 0) {
      errors.push(`Técnico ${index + 1}: tempo médio deve ser um número não negativo`);
    }

    if (typeof technician.satisfaction !== 'number' || technician.satisfaction < 0 || technician.satisfaction > 100) {
      errors.push(`Técnico ${index + 1}: satisfação deve ser um número entre 0 e 100`);
    }
  });

  // Verificar duplicatas
  const names = ranking.map(t => t.name).filter(Boolean);
  const uniqueNames = new Set(names);
  if (names.length !== uniqueNames.size) {
    warnings.push('Existem técnicos duplicados no ranking');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
};

/**
 * Valida configurações de notificação
 */
export const validateNotificationConfig = (config: any): ValidationResult => {
  const errors: string[] = [];

  if (typeof config.enabled !== 'boolean') {
    errors.push('Configuração de notificação habilitada deve ser boolean');
  }

  if (config.duration && (typeof config.duration !== 'number' || config.duration < 1000)) {
    errors.push('Duração da notificação deve ser pelo menos 1000ms');
  }

  if (config.maxNotifications && (typeof config.maxNotifications !== 'number' || config.maxNotifications < 1)) {
    errors.push('Máximo de notificações deve ser um número positivo');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Sanitiza entrada de texto
 */
export const sanitizeInput = (input: string): string => {
  return input
    .trim()
    .replace(/[<>"'&]/g, '') // Remove caracteres perigosos
    .substring(0, VALIDATION_CONFIG.MAX_SEARCH_LENGTH); // Limita tamanho
};

/**
 * Valida e sanitiza filtros
 */
export const sanitizeFilters = (filters: any): Partial<Filters> => {
  const sanitized: Partial<Filters> = {};

  if (filters.searchQuery && typeof filters.searchQuery === 'string') {
    sanitized.searchQuery = sanitizeInput(filters.searchQuery);
  }

  if (filters.status && isValidTicketStatus(filters.status)) {
    sanitized.status = filters.status;
  }

  if (filters.priority && Number.isInteger(filters.priority) && filters.priority >= 1 && filters.priority <= 6) {
    sanitized.priority = filters.priority;
  }

  if (filters.dateRange) {
    const dateValidation = validateDateRange(filters.dateRange);
    if (dateValidation.isValid) {
      sanitized.dateRange = filters.dateRange;
    }
  }

  return sanitized;
};