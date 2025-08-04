/**
 * Utilitários para validação e sanitização de dados do dashboard
 * Implementa verificações robustas para garantir consistência dos dados
 */

import { MetricsData, SystemStatus, TechnicianRanking, LevelMetrics } from '../types';

// Tipos para resultados de validação
export interface ValidationResult<T> {
  isValid: boolean;
  data: T;
  errors: string[];
  warnings: string[];
}

export interface DataIntegrityReport {
  metrics: ValidationResult<MetricsData>;
  systemStatus: ValidationResult<SystemStatus>;
  technicianRanking: ValidationResult<TechnicianRanking[]>;
  overallValid: boolean;
  timestamp: Date;
}

/**
 * Valida e sanitiza dados de métricas
 */
export function validateMetrics(data: any): ValidationResult<MetricsData> {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Estrutura padrão para fallback
  const defaultMetrics: MetricsData = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0,
    niveis: {
      n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
      n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
      n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
      n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 }
    },
    tendencias: {
      novos: '0',
      pendentes: '0',
      progresso: '0',
      resolvidos: '0'
    }
  };

  // Verificar se data existe
  if (!data) {
    errors.push('Dados de métricas não fornecidos');
    return {
      isValid: false,
      data: defaultMetrics,
      errors,
      warnings
    };
  }

  // Validar campos principais
  const sanitizedData: MetricsData = {
    novos: validateNumber(data.novos, 'novos', errors, warnings),
    pendentes: validateNumber(data.pendentes, 'pendentes', errors, warnings),
    progresso: validateNumber(data.progresso, 'progresso', errors, warnings),
    resolvidos: validateNumber(data.resolvidos, 'resolvidos', errors, warnings),
    total: validateNumber(data.total, 'total', errors, warnings),
    niveis: validateLevels(data.niveis, errors, warnings),
    tendencias: validateTrends(data.tendencias, errors, warnings)
  };

  // Validar consistência dos totais
  const calculatedTotal = sanitizedData.novos + sanitizedData.pendentes + 
                         sanitizedData.progresso + sanitizedData.resolvidos;
  
  if (sanitizedData.total !== calculatedTotal) {
    warnings.push(`Total inconsistente: declarado=${sanitizedData.total}, calculado=${calculatedTotal}`);
    // Usar o total calculado como mais confiável
    sanitizedData.total = calculatedTotal;
  }

  // Validar consistência dos níveis
  const levelTotals = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0
  };

  Object.values(sanitizedData.niveis).forEach(level => {
    levelTotals.novos += level.novos;
    levelTotals.pendentes += level.pendentes;
    levelTotals.progresso += level.progresso;
    levelTotals.resolvidos += level.resolvidos;
  });

  // Verificar se os totais dos níveis são consistentes com os totais gerais
  // (pode haver diferença se existem tickets fora dos grupos N1-N4)
  if (levelTotals.novos > sanitizedData.novos) {
    warnings.push(`Níveis têm mais 'novos' (${levelTotals.novos}) que o total geral (${sanitizedData.novos})`);
  }

  return {
    isValid: errors.length === 0,
    data: sanitizedData,
    errors,
    warnings
  };
}

/**
 * Valida dados de status do sistema
 */
export function validateSystemStatus(data: any): ValidationResult<SystemStatus> {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const defaultStatus: SystemStatus = {
    status: 'offline',
    sistema_ativo: false,
    ultima_atualizacao: ''
  };

  if (!data) {
    errors.push('Dados de status do sistema não fornecidos');
    return {
      isValid: false,
      data: defaultStatus,
      errors,
      warnings
    };
  }

  const validStatuses = ['online', 'offline', 'maintenance'];
  const status = validStatuses.includes(data.status) ? data.status : 'offline';
  
  if (data.status && !validStatuses.includes(data.status)) {
    warnings.push(`Status inválido '${data.status}', usando 'offline'`);
  }

  const sanitizedData: SystemStatus = {
    status: status as 'online' | 'offline' | 'maintenance',
    sistema_ativo: Boolean(data.sistema_ativo),
    ultima_atualizacao: String(data.ultima_atualizacao || '')
  };

  return {
    isValid: errors.length === 0,
    data: sanitizedData,
    errors,
    warnings
  };
}

/**
 * Valida dados de ranking de técnicos
 */
export function validateTechnicianRanking(data: any): ValidationResult<TechnicianRanking[]> {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  if (!Array.isArray(data)) {
    errors.push('Dados de ranking devem ser um array');
    return {
      isValid: false,
      data: [],
      errors,
      warnings
    };
  }

  const sanitizedData: TechnicianRanking[] = data
    .map((tech, index) => {
      if (!tech || typeof tech !== 'object') {
        warnings.push(`Técnico no índice ${index} é inválido`);
        return null;
      }

      return {
        id: String(tech.id || `unknown-${index}`),
        name: String(tech.name || tech.nome || 'Nome não informado'),
        level: String(tech.level || 'N1'),
        score: validateNumber(tech.score || tech.total, `score do técnico ${tech.name}`, [], warnings),
        total: validateNumber(tech.total || tech.score, `total do técnico ${tech.name}`, [], warnings),
        ticketsResolved: validateNumber(tech.ticketsResolved || tech.total || tech.score, `tickets resolvidos do técnico ${tech.name}`, [], warnings),
        ticketsInProgress: validateNumber(tech.ticketsInProgress, `tickets em progresso do técnico ${tech.name}`, [], warnings),
        averageResolutionTime: validateNumber(tech.averageResolutionTime, `tempo médio do técnico ${tech.name}`, [], warnings)
      };
    })
    .filter(tech => tech !== null) as TechnicianRanking[];

  return {
    isValid: errors.length === 0,
    data: sanitizedData,
    errors,
    warnings
  };
}

/**
 * Valida um número, retornando 0 se inválido
 */
function validateNumber(value: any, fieldName: string, errors: string[], warnings: string[]): number {
  if (value === null || value === undefined) {
    warnings.push(`Campo '${fieldName}' é null/undefined, usando 0`);
    return 0;
  }
  
  const num = Number(value);
  if (isNaN(num)) {
    warnings.push(`Campo '${fieldName}' não é um número válido (${value}), usando 0`);
    return 0;
  }
  
  if (num < 0) {
    warnings.push(`Campo '${fieldName}' é negativo (${num}), usando 0`);
    return 0;
  }
  
  return Math.floor(num); // Garantir que seja inteiro
}

/**
 * Valida dados de níveis
 */
function validateLevels(data: any, errors: string[], warnings: string[]): MetricsData['niveis'] {
  const defaultLevel: LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0
  };

  const defaultLevels = {
    n1: { ...defaultLevel },
    n2: { ...defaultLevel },
    n3: { ...defaultLevel },
    n4: { ...defaultLevel }
  };

  if (!data || typeof data !== 'object') {
    warnings.push('Dados de níveis inválidos, usando valores padrão');
    return defaultLevels;
  }

  return {
    n1: validateLevel(data.n1, 'n1', warnings),
    n2: validateLevel(data.n2, 'n2', warnings),
    n3: validateLevel(data.n3, 'n3', warnings),
    n4: validateLevel(data.n4, 'n4', warnings)
  };
}

/**
 * Valida dados de um nível específico
 */
function validateLevel(data: any, levelName: string, warnings: string[]): LevelMetrics {
  const defaultLevel: LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0
  };

  if (!data || typeof data !== 'object') {
    warnings.push(`Dados do nível ${levelName} inválidos, usando valores padrão`);
    return defaultLevel;
  }

  return {
    novos: validateNumber(data.novos, `${levelName}.novos`, [], warnings),
    pendentes: validateNumber(data.pendentes, `${levelName}.pendentes`, [], warnings),
    progresso: validateNumber(data.progresso, `${levelName}.progresso`, [], warnings),
    resolvidos: validateNumber(data.resolvidos, `${levelName}.resolvidos`, [], warnings)
  };
}

/**
 * Valida dados de tendências
 */
function validateTrends(data: any, errors: string[], warnings: string[]): MetricsData['tendencias'] {
  const defaultTrends = {
    novos: '0',
    pendentes: '0',
    progresso: '0',
    resolvidos: '0'
  };

  if (!data || typeof data !== 'object') {
    warnings.push('Dados de tendências inválidos, usando valores padrão');
    return defaultTrends;
  }

  return {
    novos: String(data.novos || '0'),
    pendentes: String(data.pendentes || '0'),
    progresso: String(data.progresso || '0'),
    resolvidos: String(data.resolvidos || '0')
  };
}

/**
 * Executa validação completa de todos os dados
 */
export function validateAllData(
  metrics: any,
  systemStatus: any,
  technicianRanking: any
): DataIntegrityReport {
  const metricsValidation = validateMetrics(metrics);
  const systemStatusValidation = validateSystemStatus(systemStatus);
  const technicianRankingValidation = validateTechnicianRanking(technicianRanking);

  const overallValid = metricsValidation.isValid && 
                      systemStatusValidation.isValid && 
                      technicianRankingValidation.isValid;

  return {
    metrics: metricsValidation,
    systemStatus: systemStatusValidation,
    technicianRanking: technicianRankingValidation,
    overallValid,
    timestamp: new Date()
  };
}

/**
 * Gera relatório de integridade dos dados
 */
export function generateIntegrityReport(report: DataIntegrityReport): string {
  const lines: string[] = [];
  
  lines.push(`=== RELATÓRIO DE INTEGRIDADE DOS DADOS ===`);
  lines.push(`Timestamp: ${report.timestamp.toISOString()}`);
  lines.push(`Status Geral: ${report.overallValid ? 'VÁLIDO' : 'INVÁLIDO'}`);
  lines.push('');
  
  // Métricas
  lines.push(`MÉTRICAS:`);
  lines.push(`  Status: ${report.metrics.isValid ? 'VÁLIDO' : 'INVÁLIDO'}`);
  if (report.metrics.errors.length > 0) {
    lines.push(`  Erros: ${report.metrics.errors.join(', ')}`);
  }
  if (report.metrics.warnings.length > 0) {
    lines.push(`  Avisos: ${report.metrics.warnings.join(', ')}`);
  }
  lines.push('');
  
  // Status do Sistema
  lines.push(`STATUS DO SISTEMA:`);
  lines.push(`  Status: ${report.systemStatus.isValid ? 'VÁLIDO' : 'INVÁLIDO'}`);
  if (report.systemStatus.errors.length > 0) {
    lines.push(`  Erros: ${report.systemStatus.errors.join(', ')}`);
  }
  if (report.systemStatus.warnings.length > 0) {
    lines.push(`  Avisos: ${report.systemStatus.warnings.join(', ')}`);
  }
  lines.push('');
  
  // Ranking de Técnicos
  lines.push(`RANKING DE TÉCNICOS:`);
  lines.push(`  Status: ${report.technicianRanking.isValid ? 'VÁLIDO' : 'INVÁLIDO'}`);
  lines.push(`  Técnicos válidos: ${report.technicianRanking.data.length}`);
  if (report.technicianRanking.errors.length > 0) {
    lines.push(`  Erros: ${report.technicianRanking.errors.join(', ')}`);
  }
  if (report.technicianRanking.warnings.length > 0) {
    lines.push(`  Avisos: ${report.technicianRanking.warnings.join(', ')}`);
  }
  
  return lines.join('\n');
}