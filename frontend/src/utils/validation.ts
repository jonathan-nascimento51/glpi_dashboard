import type {
  DashboardMetrics,
  LevelMetrics,
  NiveisMetrics,
  TendenciasMetrics,
  FilterParams,
  ApiError,
  ValidationResult
} from '../types/api';

/**
 * Utilitários de validação para dados da API
 */

// Validação de métricas de nível
export const validateLevelMetrics = (data: any): ValidationResult<LevelMetrics> => {
  const errors: string[] = [];
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, errors: ['Dados de nível devem ser um objeto'] };
  }
  
  const requiredFields = ['abertos', 'fechados', 'pendentes', 'atrasados'];
  
  for (const field of requiredFields) {
    if (typeof data[field] !== 'number' || data[field] < 0) {
      errors.push(`Campo '${field}' deve ser um número não negativo`);
    }
  }
  
  // Validação opcional de tendências
  const trendFields = ['tendencia_abertos', 'tendencia_fechados', 'tendencia_pendentes', 'tendencia_atrasados'];
  
  for (const field of trendFields) {
    if (data[field] !== undefined && typeof data[field] !== 'number') {
      errors.push(`Campo '${field}' deve ser um número`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data as LevelMetrics : undefined
  };
};

// Validação de métricas de níveis
export const validateNiveisMetrics = (data: any): ValidationResult<NiveisMetrics> => {
  const errors: string[] = [];
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, errors: ['Dados de níveis devem ser um objeto'] };
  }
  
  const validLevels = ['N1', 'N2', 'N3', 'N4'];
  
  for (const level of validLevels) {
    if (data[level]) {
      const levelValidation = validateLevelMetrics(data[level]);
      if (!levelValidation.isValid) {
        errors.push(`Nível ${level}: ${levelValidation.errors.join(', ')}`);
      }
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data as NiveisMetrics : undefined
  };
};

// Validação de tendências
export const validateTendenciasMetrics = (data: any): ValidationResult<TendenciasMetrics> => {
  const errors: string[] = [];
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, errors: ['Dados de tendências devem ser um objeto'] };
  }
  
  const numericFields = [
    'novos_tickets',
    'tickets_resolvidos', 
    'tempo_medio_resolucao',
    'taxa_satisfacao'
  ];
  
  for (const field of numericFields) {
    if (data[field] !== undefined && (typeof data[field] !== 'number' || data[field] < 0)) {
      errors.push(`Campo '${field}' deve ser um número não negativo`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data as TendenciasMetrics : undefined
  };
};

// Validação completa de métricas do dashboard
export const validateDashboardMetrics = (data: any): ValidationResult<DashboardMetrics> => {
  const errors: string[] = [];
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, errors: ['Dados do dashboard devem ser um objeto'] };
  }
  
  // Validar níveis se presente
  if (data.niveis) {
    const niveisValidation = validateNiveisMetrics(data.niveis);
    if (!niveisValidation.isValid) {
      errors.push(`Níveis: ${niveisValidation.errors.join(', ')}`);
    }
  }
  
  // Validar tendências se presente
  if (data.tendencias) {
    const tendenciasValidation = validateTendenciasMetrics(data.tendencias);
    if (!tendenciasValidation.isValid) {
      errors.push(`Tendências: ${tendenciasValidation.errors.join(', ')}`);
    }
  }
  
  // Validar timestamp se presente
  if (data.timestamp && !(data.timestamp instanceof Date) && typeof data.timestamp !== 'string') {
    errors.push('Timestamp deve ser uma data ou string');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data as DashboardMetrics : undefined
  };
};

// Validação de parâmetros de filtro
export const validateFilterParams = (params: any): ValidationResult<FilterParams> => {
  const errors: string[] = [];
  
  if (typeof params !== 'object' || params === null) {
    return { isValid: false, errors: ['Parâmetros de filtro devem ser um objeto'] };
  }
  
  // Validar datas se presentes
  if (params.startDate && typeof params.startDate !== 'string') {
    errors.push('startDate deve ser uma string');
  }
  
  if (params.endDate && typeof params.endDate !== 'string') {
    errors.push('endDate deve ser uma string');
  }
  
  // Validar se data de início é anterior à data de fim
  if (params.startDate && params.endDate) {
    const start = new Date(params.startDate);
    const end = new Date(params.endDate);
    
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      errors.push('Datas devem estar em formato válido');
    } else if (start > end) {
      errors.push('Data de início deve ser anterior à data de fim');
    }
  }
  
  // Validar valores de enum se presentes
  const validStatuses = ['aberto', 'fechado', 'pendente', 'atrasado'];
  if (params.status && !validStatuses.includes(params.status)) {
    errors.push(`Status deve ser um dos valores: ${validStatuses.join(', ')}`);
  }
  
  const validPriorities = ['baixa', 'media', 'alta', 'critica'];
  if (params.priority && !validPriorities.includes(params.priority)) {
    errors.push(`Prioridade deve ser um dos valores: ${validPriorities.join(', ')}`);
  }
  
  const validLevels = ['N1', 'N2', 'N3', 'N4'];
  if (params.level && !validLevels.includes(params.level)) {
    errors.push(`Nível deve ser um dos valores: ${validLevels.join(', ')}`);
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? params as FilterParams : undefined
  };
};

// Sanitização de dados de entrada
export const sanitizeFilterParams = (params: any): FilterParams => {
  const sanitized: FilterParams = {};
  
  if (params.startDate && typeof params.startDate === 'string') {
    sanitized.startDate = params.startDate.trim();
  }
  
  if (params.endDate && typeof params.endDate === 'string') {
    sanitized.endDate = params.endDate.trim();
  }
  
  if (params.status && typeof params.status === 'string') {
    sanitized.status = params.status.trim().toLowerCase();
  }
  
  if (params.priority && typeof params.priority === 'string') {
    sanitized.priority = params.priority.trim().toLowerCase();
  }
  
  if (params.level && typeof params.level === 'string') {
    sanitized.level = params.level.trim().toUpperCase();
  }
  
  if (params.technician && typeof params.technician === 'string') {
    sanitized.technician = params.technician.trim();
  }
  
  if (params.category && typeof params.category === 'string') {
    sanitized.category = params.category.trim();
  }
  
  return sanitized;
};

// Validação de erro da API
export const validateApiError = (error: any): ValidationResult<ApiError> => {
  const errors: string[] = [];
  
  if (typeof error !== 'object' || error === null) {
    return { isValid: false, errors: ['Erro da API deve ser um objeto'] };
  }
  
  if (!error.success || error.success !== false) {
    errors.push('Campo success deve ser false para erros');
  }
  
  if (!error.error || typeof error.error !== 'object') {
    errors.push('Campo error deve ser um objeto');
  } else {
    if (!error.error.message || typeof error.error.message !== 'string') {
      errors.push('Mensagem de erro deve ser uma string');
    }
    
    if (error.error.code && typeof error.error.code !== 'string') {
      errors.push('Código de erro deve ser uma string');
    }
  }
  
  if (!error.timestamp) {
    errors.push('Timestamp é obrigatório');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? error as ApiError : undefined
  };
};

// Utilitário para validação em lote
export const validateBatch = <T>(
  items: any[],
  validator: (item: any) => ValidationResult<T>
): { valid: T[], invalid: { item: any, errors: string[] }[] } => {
  const valid: T[] = [];
  const invalid: { item: any, errors: string[] }[] = [];
  
  for (const item of items) {
    const result = validator(item);
    if (result.isValid && result.data) {
      valid.push(result.data);
    } else {
      invalid.push({ item, errors: result.errors });
    }
  }
  
  return { valid, invalid };
};

// Validação de schema genérica
export const createValidator = <T>(
  schema: Record<string, (value: any) => boolean>,
  requiredFields: string[] = []
) => {
  return (data: any): ValidationResult<T> => {
    const errors: string[] = [];
    
    if (typeof data !== 'object' || data === null) {
      return { isValid: false, errors: ['Dados devem ser um objeto'] };
    }
    
    // Verificar campos obrigatórios
    for (const field of requiredFields) {
      if (!(field in data)) {
        errors.push(`Campo obrigatório '${field}' está ausente`);
      }
    }
    
    // Validar campos presentes
    for (const [field, validator] of Object.entries(schema)) {
      if (field in data && !validator(data[field])) {
        errors.push(`Campo '${field}' é inválido`);
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      data: errors.length === 0 ? data as T : undefined
    };
  };
};

export default {
  validateLevelMetrics,
  validateNiveisMetrics,
  validateTendenciasMetrics,
  validateDashboardMetrics,
  validateFilterParams,
  validateApiError,
  sanitizeFilterParams,
  validateBatch,
  createValidator
};