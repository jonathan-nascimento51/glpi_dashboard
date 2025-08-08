import type {
  DashboardMetrics,
  LevelMetrics,
  NiveisMetrics,
  TendenciasMetrics,
  FilterParams,
  ApiError
} from '../types/api';
import { ValidationResult } from './dataValidation';

/**
 * Utilitários de validação para dados da API
 */

// Validação de métricas de nível
export const validateLevelMetrics = (data: any): ValidationResult<LevelMetrics> => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultData: LevelMetrics = {
    novos: 0,
    progresso: 0,
    pendentes: 0,
    resolvidos: 0,
    total: 0
  };
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, data: defaultData, errors: ['Dados de nível devem ser um objeto'], warnings };
  }
  
  const requiredFields = ['novos', 'progresso', 'pendentes', 'resolvidos', 'total'];
  
  for (const field of requiredFields) {
    if (typeof data[field] !== 'number' || data[field] < 0) {
      errors.push(`Campo '${field}' deve ser um número não negativo`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    data: errors.length === 0 ? data as LevelMetrics : defaultData,
    errors,
    warnings
  };
};

// Validação de métricas de níveis
export const validateNiveisMetrics = (data: any): ValidationResult<NiveisMetrics> => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultData: NiveisMetrics = {
    'Manutenção Geral': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
    'Patrimônio': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
    'Atendimento': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
    'Mecanografia': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 }
  };
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, data: defaultData, errors: ['Dados de níveis devem ser um objeto'], warnings };
  }
  
  const validLevels = ['Manutenção Geral', 'Patrimônio', 'Atendimento', 'Mecanografia'];
  
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
    data: errors.length === 0 ? data as NiveisMetrics : defaultData,
    errors,
    warnings
  };
};

// Validação de tendências
export const validateTendenciasMetrics = (data: any): ValidationResult<TendenciasMetrics> => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultData: TendenciasMetrics = {
    novos: '0',
    pendentes: '0',
    progresso: '0',
    resolvidos: '0'
  };
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, data: defaultData, errors: ['Dados de tendências devem ser um objeto'], warnings };
  }
  
  const stringFields = [
    'novos',
    'pendentes', 
    'progresso',
    'resolvidos'
  ];
  
  for (const field of stringFields) {
    if (data[field] !== undefined && typeof data[field] !== 'string') {
      errors.push(`Campo '${field}' deve ser uma string`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    data: errors.length === 0 ? data as TendenciasMetrics : defaultData,
    errors,
    warnings
  };
};

// Validação completa de métricas do dashboard
export const validateDashboardMetrics = (data: any): ValidationResult<DashboardMetrics> => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultData: DashboardMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0,
    niveis: {
      'Manutenção Geral': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
      'Patrimônio': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
      'Atendimento': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 },
      'Mecanografia': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, total: 0 }
    },
    tendencias: {
      novos: '0',
      pendentes: '0',
      progresso: '0',
      resolvidos: '0'
    },
    timestamp: new Date().toISOString()
  };
  
  if (typeof data !== 'object' || data === null) {
    return { isValid: false, data: defaultData, errors: ['Dados do dashboard devem ser um objeto'], warnings };
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
    data: errors.length === 0 ? data as DashboardMetrics : defaultData,
    errors,
    warnings
  };
};

// Validação de parâmetros de filtro
export const validateFilterParams = (params: any): ValidationResult<FilterParams> => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultData: FilterParams = {};
  
  if (typeof params !== 'object' || params === null) {
    return { isValid: false, data: defaultData, errors: ['Parâmetros de filtro devem ser um objeto'], warnings };
  }
  
  // Validar período se presente
  const validPeriods = ['today', 'week', 'month'];
  if (params.period && !validPeriods.includes(params.period)) {
    errors.push(`Período deve ser um dos valores: ${validPeriods.join(', ')}`);
  }
  
  // Validar dateRange se presente
  if (params.dateRange) {
    if (typeof params.dateRange !== 'object' || params.dateRange === null) {
      errors.push('dateRange deve ser um objeto');
    } else {
      if (params.dateRange.startDate && typeof params.dateRange.startDate !== 'string') {
        errors.push('startDate deve ser uma string');
      }
      
      if (params.dateRange.endDate && typeof params.dateRange.endDate !== 'string') {
        errors.push('endDate deve ser uma string');
      }
      
      // Validar se data de início é anterior à data de fim
      if (params.dateRange.startDate && params.dateRange.endDate) {
        const start = new Date(params.dateRange.startDate);
        const end = new Date(params.dateRange.endDate);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
          errors.push('Datas devem estar em formato válido');
        } else if (start > end) {
          errors.push('Data de início deve ser anterior à data de fim');
        }
      }
    }
  }
  
  // Validar arrays se presentes
  if (params.levels && !Array.isArray(params.levels)) {
    errors.push('levels deve ser um array');
  }
  
  if (params.status && !Array.isArray(params.status)) {
    errors.push('status deve ser um array');
  }
  
  if (params.priority && !Array.isArray(params.priority)) {
    errors.push('priority deve ser um array');
  }
  
  return {
    isValid: errors.length === 0,
    data: errors.length === 0 ? params as FilterParams : defaultData,
    errors,
    warnings
  };
};

// Sanitização de dados de entrada
export const sanitizeFilterParams = (params: any): FilterParams => {
  const sanitized: FilterParams = {};
  
  if (params.period && typeof params.period === 'string') {
    const validPeriods = ['today', 'week', 'month'];
    const period = params.period.trim().toLowerCase();
    if (validPeriods.includes(period)) {
      sanitized.period = period as 'today' | 'week' | 'month';
    }
  }
  
  if (params.dateRange && typeof params.dateRange === 'object') {
    sanitized.dateRange = {
      startDate: params.dateRange.startDate?.trim() || '',
      endDate: params.dateRange.endDate?.trim() || ''
    };
  }
  
  if (params.levels && Array.isArray(params.levels)) {
    sanitized.levels = params.levels.map((level: any) => 
      typeof level === 'string' ? level.trim() : String(level)
    );
  }
  
  if (params.status && Array.isArray(params.status)) {
    sanitized.status = params.status.map((status: any) => 
      typeof status === 'string' ? status.trim() : String(status)
    );
  }
  
  if (params.priority && Array.isArray(params.priority)) {
    sanitized.priority = params.priority.map((priority: any) => 
      typeof priority === 'string' ? priority.trim() : String(priority)
    );
  }
  
  return sanitized;
};

// Validação de erro da API
export const validateApiError = (error: any): ValidationResult<ApiError> => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultData: ApiError = {
    success: false,
    error: {
      message: 'Erro desconhecido',
      code: 'UNKNOWN_ERROR'
    },
    timestamp: new Date().toISOString()
  };
  
  if (typeof error !== 'object' || error === null) {
    return { isValid: false, data: defaultData, errors: ['Erro da API deve ser um objeto'], warnings };
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
    data: errors.length === 0 ? error as ApiError : defaultData,
    errors,
    warnings
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
  requiredFields: string[] = [],
  defaultData?: T
) => {
  return (data: any): ValidationResult<T> => {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    if (typeof data !== 'object' || data === null) {
      return { 
        isValid: false, 
        data: defaultData || ({} as T), 
        errors: ['Dados devem ser um objeto'], 
        warnings 
      };
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
      data: errors.length === 0 ? data as T : (defaultData || ({} as T)),
      errors,
      warnings
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