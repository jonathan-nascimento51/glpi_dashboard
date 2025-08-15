/**
 * Utilitarios para validacao e sanitizacao de dados do dashboard
 * Implementa verificacoes robustas para garantir consistencia dos dados
 */

import { SystemStatus, TechnicianRanking } from '../types';
import { DashboardMetrics, NiveisMetrics } from '../types/api';

// Tipos para resultados de validacao
export interface ValidationResult<T> {
  isValid: boolean;
  data: T;
  errors: string[];
  warnings: string[];
}

export interface DataIntegrityReport {
  metrics: ValidationResult<DashboardMetrics>;
  systemStatus: ValidationResult<SystemStatus>;
  technicianRanking: ValidationResult<TechnicianRanking[]>;
  overallValid: boolean;
  timestamp: Date;
}

/**
 * Valida e sanitiza dados de metricas
 */
export function validateMetrics(data: any): ValidationResult<DashboardMetrics> {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Estrutura padrao para fallback
  const defaultMetrics: DashboardMetrics = {
    niveis: {
      geral: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n1: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n2: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n3: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 },
      n4: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0, total: 0 }
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
    errors.push('Dados de metricas nao fornecidos');
    return {
      isValid: false,
      data: defaultMetrics,
      errors,
      warnings
    };
  }

  // Validar campos principais
  const sanitizedData: DashboardMetrics = {
    niveis: validateNiveisMetrics(data.niveis || data, errors, warnings),
    tendencias: validateTrends(data.tendencias, errors, warnings),
    filtros_aplicados: data.filtros_aplicados,
    tempo_execucao: data.tempo_execucao,
    timestamp: data.timestamp,
    systemStatus: data.systemStatus,
    technicianRanking: data.technicianRanking
  };

  // Validar consistencia dos niveis internamente
  const { geral, ...specificLevels } = sanitizedData.niveis;
  const levelTotals = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0
  };

  Object.values(specificLevels).forEach(level => {
    levelTotals.novos += level.novos;
    levelTotals.pendentes += level.pendentes;
    levelTotals.progresso += level.progresso;
    levelTotals.resolvidos += level.resolvidos;
  });

  // Verificar se o geral esta consistente com a soma dos niveis especificos
  if (geral.novos !== levelTotals.novos) {
    warnings.push(`Total geral de 'novos' (${geral.novos}) nao corresponde a soma dos niveis (${levelTotals.novos})`);
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
    errors.push('Dados de status do sistema nao fornecidos');
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
    warnings.push(`Status invalido '${data.status}', usando 'offline'`);
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
 * Valida dados de ranking de tecnicos
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
        warnings.push(`Tecnico no indice ${index} e invalido`);
        return null;
      }

      return {
        id: String(tech.id || `unknown-${index}`),
        name: String(tech.name || tech.nome || 'Nome nao informado'),
        level: String(tech.level || 'N1'),
        score: validateNumber(tech.score || tech.total, `score do tecnico ${tech.name}`, [], warnings),
        total: validateNumber(tech.total || tech.score, `total do tecnico ${tech.name}`, [], warnings),
        ticketsResolved: validateNumber(tech.ticketsResolved || tech.total || tech.score, `tickets resolvidos do tecnico ${tech.name}`, [], warnings),
        ticketsInProgress: validateNumber(tech.ticketsInProgress, `tickets em progresso do tecnico ${tech.name}`, [], warnings),
        averageResolutionTime: validateNumber(tech.averageResolutionTime, `tempo medio do tecnico ${tech.name}`, [], warnings)
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
 * Valida um numero, retornando 0 se invalido
 */
function validateNumber(value: any, fieldName: string, _errors: string[], warnings: string[]): number {
  if (value === null || value === undefined) {
    warnings.push(`Campo '${fieldName}' e null/undefined, usando 0`);
    return 0;
  }
  
  const num = Number(value);
  if (isNaN(num)) {
    warnings.push(`Campo '${fieldName}' nao e um numero valido (${value}), usando 0`);
    return 0;
  }
  
  if (num < 0) {
    warnings.push(`Campo '${fieldName}' e negativo (${num}), usando 0`);
    return 0;
  }
  
  return Math.floor(num); // Garantir que seja inteiro
}

/**
 * Valida dados de um nivel especifico para API
 */
function validateLevel(data: any, levelName: string, warnings: string[]): import('../types/api').LevelMetrics {
  const defaultLevel: import('../types/api').LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0
  };

  if (!data || typeof data !== 'object') {
    warnings.push(`Dados do nivel ${levelName} invalidos, usando valores padrao`);
    return defaultLevel;
  }

  const novos = validateNumber(data.novos, `${levelName}.novos`, [], warnings);
  const pendentes = validateNumber(data.pendentes, `${levelName}.pendentes`, [], warnings);
  const progresso = validateNumber(data.progresso, `${levelName}.progresso`, [], warnings);
  const resolvidos = validateNumber(data.resolvidos, `${levelName}.resolvidos`, [], warnings);
  const total = novos + pendentes + progresso + resolvidos;

  return {
    novos,
    pendentes,
    progresso,
    resolvidos,
    total
  };
}

/**
 * Valida dados de niveis para DashboardMetrics (com propriedade geral)
 */
function validateNiveisMetrics(data: any, _errors: string[], warnings: string[]): NiveisMetrics {
  const defaultLevel: import('../types/api').LevelMetrics = {
    novos: 0,
    pendentes: 0,
    progresso: 0,
    resolvidos: 0,
    total: 0
  };

  const defaultNiveis: NiveisMetrics = {
    geral: { ...defaultLevel },
    n1: { ...defaultLevel },
    n2: { ...defaultLevel },
    n3: { ...defaultLevel },
    n4: { ...defaultLevel }
  };

  if (!data || typeof data !== 'object') {
    warnings.push('Dados de niveis invalidos, usando valores padrao');
    return defaultNiveis;
  }

  return {
    geral: validateLevel(data.geral, 'geral', warnings),
    n1: validateLevel(data.n1, 'n1', warnings),
    n2: validateLevel(data.n2, 'n2', warnings),
    n3: validateLevel(data.n3, 'n3', warnings),
    n4: validateLevel(data.n4, 'n4', warnings)
  };
}

/**
 * Valida dados de tendencias
 */
function validateTrends(data: any, _errors: string[], warnings: string[]): DashboardMetrics['tendencias'] {
  const defaultTrends = {
    novos: '0',
    pendentes: '0',
    progresso: '0',
    resolvidos: '0'
  };

  if (!data || typeof data !== 'object') {
    warnings.push('Dados de tendencias invalidos, usando valores padrao');
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
 * Executa validacao completa de todos os dados
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
 * Gera relatorio de integridade dos dados
 */
export function generateIntegrityReport(report: DataIntegrityReport): string {
  const lines: string[] = [];
  
  lines.push(`=== RELAToRIO DE INTEGRIDADE DOS DADOS ===`);
  lines.push(`Timestamp: ${report.timestamp.toISOString()}`);
  lines.push(`Status Geral: ${report.overallValid ? 'VaLIDO' : 'INVaLIDO'}`);
  lines.push('');
  
  // Metricas
  lines.push(`MeTRICAS:`);
  lines.push(`  Status: ${report.metrics.isValid ? 'VaLIDO' : 'INVaLIDO'}`);
  if (report.metrics.errors.length > 0) {
    lines.push(`  Erros: ${report.metrics.errors.join(', ')}`);
  }
  if (report.metrics.warnings.length > 0) {
    lines.push(`  Avisos: ${report.metrics.warnings.join(', ')}`);
  }
  lines.push('');
  
  // Status do Sistema
  lines.push(`STATUS DO SISTEMA:`);
  lines.push(`  Status: ${report.systemStatus.isValid ? 'VaLIDO' : 'INVaLIDO'}`);
  if (report.systemStatus.errors.length > 0) {
    lines.push(`  Erros: ${report.systemStatus.errors.join(', ')}`);
  }
  if (report.systemStatus.warnings.length > 0) {
    lines.push(`  Avisos: ${report.systemStatus.warnings.join(', ')}`);
  }
  lines.push('');
  
  // Ranking de Tecnicos
  lines.push(`RANKING DE TeCNICOS:`);
  lines.push(`  Status: ${report.technicianRanking.isValid ? 'VaLIDO' : 'INVaLIDO'}`);
  lines.push(`  Tecnicos validos: ${report.technicianRanking.data.length}`);
  if (report.technicianRanking.errors.length > 0) {
    lines.push(`  Erros: ${report.technicianRanking.errors.join(', ')}`);
  }
  if (report.technicianRanking.warnings.length > 0) {
    lines.push(`  Avisos: ${report.technicianRanking.warnings.join(', ')}`);
  }
  
  return lines.join('\n');
}