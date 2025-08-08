import type {
  LevelMetrics,
  PerformanceMetrics
} from '../types/api';

/**
 * Utilitários de formatação para exibição de dados
 */

// Formatação de números
export const formatNumber = (value: number, options?: Intl.NumberFormatOptions): string => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...options
  }).format(value);
};

// Formatação de porcentagem
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value / 100);
};

// Formatação de moeda
export const formatCurrency = (value: number, currency: string = 'BRL'): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency
  }).format(value);
};

// Formatação de data
export const formatDate = (date: Date | string, format: 'short' | 'long' | 'time' = 'short'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Data inválida';
  }
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('pt-BR');
    case 'long':
      return dateObj.toLocaleDateString('pt-BR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    case 'time':
      return dateObj.toLocaleString('pt-BR');
    default:
      return dateObj.toLocaleDateString('pt-BR');
  }
};

// Formatação de tempo relativo
export const formatRelativeTime = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'Agora mesmo';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minuto${diffInMinutes > 1 ? 's' : ''} atrás`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hora${diffInHours > 1 ? 's' : ''} atrás`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} dia${diffInDays > 1 ? 's' : ''} atrás`;
  }
  
  return formatDate(dateObj);
};

// Formatação de duração em milissegundos
export const formatDuration = (milliseconds: number): string => {
  if (milliseconds < 1000) {
    return `${Math.round(milliseconds)}ms`;
  }
  
  const seconds = milliseconds / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return `${hours}h ${remainingMinutes}m`;
};

// Formatação de tamanho de arquivo
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

// Formatação de status com cores
export const formatStatus = (status: string): { text: string; color: string; bgColor: string } => {
  const statusMap: Record<string, { text: string; color: string; bgColor: string }> = {
    aberto: { text: 'Aberto', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    fechado: { text: 'Fechado', color: 'text-green-700', bgColor: 'bg-green-100' },
    pendente: { text: 'Pendente', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    atrasado: { text: 'Atrasado', color: 'text-red-700', bgColor: 'bg-red-100' }
  };
  
  return statusMap[status.toLowerCase()] || { text: status, color: 'text-gray-700', bgColor: 'bg-gray-100' };
};

// Formatação de prioridade com cores
export const formatPriority = (priority: string): { text: string; color: string; bgColor: string } => {
  const priorityMap: Record<string, { text: string; color: string; bgColor: string }> = {
    baixa: { text: 'Baixa', color: 'text-green-700', bgColor: 'bg-green-100' },
    media: { text: 'Média', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    alta: { text: 'Alta', color: 'text-orange-700', bgColor: 'bg-orange-100' },
    critica: { text: 'Crítica', color: 'text-red-700', bgColor: 'bg-red-100' }
  };
  
  return priorityMap[priority.toLowerCase()] || { text: priority, color: 'text-gray-700', bgColor: 'bg-gray-100' };
};

// Formatação de nível
export const formatLevel = (level: string): string => {
  const levelMap: Record<string, string> = {
    N1: 'Nível 1',
    N2: 'Nível 2',
    N3: 'Nível 3',
    N4: 'Nível 4'
  };
  
  return levelMap[level.toUpperCase()] || level;
};

// Formatação de tendência
export const formatTrend = (value: number): { text: string; icon: string; color: string } => {
  if (value > 0) {
    return {
      text: `+${formatPercentage(Math.abs(value))}`,
      icon: '↗',
      color: 'text-green-600'
    };
  } else if (value < 0) {
    return {
      text: `-${formatPercentage(Math.abs(value))}`,
      icon: '↘',
      color: 'text-red-600'
    };
  } else {
    return {
      text: '0%',
      icon: '→',
      color: 'text-gray-600'
    };
  }
};

// Formatação de métricas de performance
export const formatPerformanceMetrics = (metrics: PerformanceMetrics): Record<string, string> => {
  return {
    responseTime: formatDuration(metrics.responseTime),
    cacheHit: metrics.cacheHit ? 'Sim' : 'Não',
    timestamp: formatDate(metrics.timestamp, 'time'),
    endpoint: metrics.endpoint
  };
};

// Formatação de métricas de nível para exibição
export const formatLevelMetricsForDisplay = (metrics: LevelMetrics) => {
  return {
    abertos: {
      value: formatNumber(metrics.abertos || 0),
      trend: metrics.tendencia_abertos ? formatTrend(metrics.tendencia_abertos) : null
    },
    fechados: {
      value: formatNumber(metrics.fechados || 0),
      trend: metrics.tendencia_fechados ? formatTrend(metrics.tendencia_fechados) : null
    },
    pendentes: {
      value: formatNumber(metrics.pendentes || 0),
      trend: metrics.tendencia_pendentes ? formatTrend(metrics.tendencia_pendentes) : null
    },
    atrasados: {
      value: formatNumber(metrics.atrasados || 0),
      trend: metrics.tendencia_atrasados ? formatTrend(metrics.tendencia_atrasados) : null
    }
  };
};

// Formatação de texto truncado
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength - 3) + '...';
};

// Formatação de nome de usuário
export const formatUserName = (firstName?: string, lastName?: string, username?: string): string => {
  if (firstName && lastName) {
    return `${firstName} ${lastName}`;
  }
  
  if (firstName) {
    return firstName;
  }
  
  if (username) {
    return username;
  }
  
  return 'Usuário desconhecido';
};

// Formatação de lista com separadores
export const formatList = (items: string[], separator: string = ', ', lastSeparator: string = ' e '): string => {
  if (items.length === 0) {
    return '';
  }
  
  if (items.length === 1) {
    return items[0];
  }
  
  if (items.length === 2) {
    return items.join(lastSeparator);
  }
  
  const allButLast = items.slice(0, -1);
  const last = items[items.length - 1];
  
  return allButLast.join(separator) + lastSeparator + last;
};

// Formatação de URL amigável
export const formatFriendlyUrl = (text: string): string => {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .replace(/[^a-z0-9\s-]/g, '') // Remove caracteres especiais
    .replace(/\s+/g, '-') // Substitui espaços por hífens
    .replace(/-+/g, '-') // Remove hífens duplicados
    .trim()
    .replace(/^-+|-+$/g, ''); // Remove hífens do início e fim
};

// Formatação de placeholder para campos vazios
export const formatPlaceholder = (value: any, placeholder: string = 'N/A'): string => {
  if (value === null || value === undefined || value === '') {
    return placeholder;
  }
  
  if (typeof value === 'number' && isNaN(value)) {
    return placeholder;
  }
  
  return String(value);
};

// Formatação de classe CSS condicional
export const formatConditionalClass = (
  baseClass: string,
  condition: boolean,
  conditionalClass: string
): string => {
  return condition ? `${baseClass} ${conditionalClass}` : baseClass;
};

// Formatação de atributos de acessibilidade
export const formatAriaLabel = (label: string, value?: string | number): string => {
  if (value !== undefined) {
    return `${label}: ${value}`;
  }
  return label;
};

export default {
  formatNumber,
  formatPercentage,
  formatCurrency,
  formatDate,
  formatRelativeTime,
  formatDuration,
  formatFileSize,
  formatStatus,
  formatPriority,
  formatLevel,
  formatTrend,
  formatPerformanceMetrics,
  formatLevelMetricsForDisplay,
  truncateText,
  formatUserName,
  formatList,
  formatFriendlyUrl,
  formatPlaceholder,
  formatConditionalClass,
  formatAriaLabel
};