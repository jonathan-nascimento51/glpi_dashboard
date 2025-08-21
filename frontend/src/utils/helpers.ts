// Funções auxiliares e utilitários comuns

import { VALIDATION_CONFIG, UI_CONFIG } from '../config/constants';
import type { TicketStatus, Theme } from '../types';

/**
 * Formata números com separadores de milhares
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('pt-BR').format(num);
};

/**
 * Formata porcentagens
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

/**
 * Formata datas para exibição
 */
export const formatDate = (date: string | Date, format: 'short' | 'long' = 'short'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (format === 'long') {
    return dateObj.toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
  
  return dateObj.toLocaleDateString('pt-BR');
};

/**
 * Formata tempo relativo (ex: "há 2 horas")
 */
export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'agora mesmo';
  if (diffInSeconds < 3600) return `há ${Math.floor(diffInSeconds / 60)} min`;
  if (diffInSeconds < 86400) return `há ${Math.floor(diffInSeconds / 3600)} h`;
  if (diffInSeconds < 2592000) return `há ${Math.floor(diffInSeconds / 86400)} dias`;
  
  return formatDate(dateObj);
};

/**
 * Trunca texto com reticências
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

/**
 * Valida se uma string é um email válido
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Valida se uma string de busca é válida
 */
export const isValidSearchQuery = (query: string): boolean => {
  return query.length >= VALIDATION_CONFIG.MIN_SEARCH_LENGTH && 
         query.length <= VALIDATION_CONFIG.MAX_SEARCH_LENGTH;
};

/**
 * Gera um ID único
 */
export const generateId = (): string => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

/**
 * Debounce function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Throttle function
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
};

/**
 * Converte status do ticket para cor
 */
export const getStatusColor = (status: TicketStatus): string => {
  const statusColors = {
    new: 'bg-blue-100 text-blue-800',
    assigned: 'bg-yellow-100 text-yellow-800',
    planned: 'bg-purple-100 text-purple-800',
    waiting: 'bg-orange-100 text-orange-800',
    solved: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800',
  };
  
  return statusColors[status] || 'bg-gray-100 text-gray-800';
};

/**
 * Converte status do ticket para label em português
 */
export const getStatusLabel = (status: TicketStatus): string => {
  const statusLabels = {
    new: 'Novo',
    assigned: 'Atribuído',
    planned: 'Planejado',
    waiting: 'Aguardando',
    solved: 'Resolvido',
    closed: 'Fechado',
  };
  
  return statusLabels[status] || status;
};

/**
 * Converte prioridade para cor
 */
export const getPriorityColor = (priority: number): string => {
  if (priority <= 2) return 'text-green-600';
  if (priority <= 3) return 'text-yellow-600';
  if (priority <= 4) return 'text-orange-600';
  return 'text-red-600';
};

/**
 * Converte prioridade para label
 */
export const getPriorityLabel = (priority: number): string => {
  const labels = {
    1: 'Muito Baixa',
    2: 'Baixa',
    3: 'Média',
    4: 'Alta',
    5: 'Muito Alta',
    6: 'Crítica',
  };
  
  return labels[priority as keyof typeof labels] || 'Desconhecida';
};

/**
 * Calcula a diferença em dias entre duas datas
 */
export const daysDifference = (date1: Date, date2: Date): number => {
  const diffTime = Math.abs(date2.getTime() - date1.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

/**
 * Converte bytes para formato legível
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Verifica se o dispositivo é mobile
 */
export const isMobile = (): boolean => {
  return window.innerWidth < 768;
};

/**
 * Copia texto para a área de transferência
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Erro ao copiar para área de transferência:', error);
    return false;
  }
};

/**
 * Converte tema para classes CSS
 */
export const getThemeClasses = (theme: Theme): string => {
  return theme === 'dark' ? 'dark' : '';
};

/**
 * Valida se um objeto está vazio
 */
export const isEmpty = (obj: any): boolean => {
  if (obj == null) return true;
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  if (typeof obj === 'string') return obj.trim().length === 0;
  return false;
};

/**
 * Remove propriedades undefined de um objeto
 */
export const removeUndefined = <T extends Record<string, any>>(obj: T): Partial<T> => {
  const result: Partial<T> = {};
  
  Object.keys(obj).forEach(key => {
    if (obj[key] !== undefined) {
      result[key as keyof T] = obj[key];
    }
  });
  
  return result;
};

/**
 * Converte string para slug (URL-friendly)
 */
export const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .replace(/[^a-z0-9 -]/g, '') // Remove caracteres especiais
    .replace(/\s+/g, '-') // Substitui espaços por hífens
    .replace(/-+/g, '-') // Remove hífens duplicados
    .trim();
};