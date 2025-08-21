// Configuração de tema da aplicação

import type { Theme } from '../types';

/**
 * Interface para cores do tema
 */
export interface ThemeColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    disabled: string;
    inverse: string;
  };
  border: string;
  shadow: string;
  overlay: string;
  accent: string;
}

/**
 * Interface para tipografia
 */
export interface ThemeTypography {
  fontFamily: {
    primary: string;
    secondary: string;
    mono: string;
  };
  fontSize: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
  };
  fontWeight: {
    light: number;
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
  lineHeight: {
    tight: number;
    normal: number;
    relaxed: number;
  };
}

/**
 * Interface para espaçamento
 */
export interface ThemeSpacing {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
}

/**
 * Interface para breakpoints
 */
export interface ThemeBreakpoints {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
}

/**
 * Interface para sombras
 */
export interface ThemeShadows {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  inner: string;
}

/**
 * Interface para bordas
 */
export interface ThemeBorders {
  radius: {
    none: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    full: string;
  };
  width: {
    thin: string;
    normal: string;
    thick: string;
  };
}

/**
 * Interface para transições
 */
export interface ThemeTransitions {
  duration: {
    fast: string;
    normal: string;
    slow: string;
  };
  easing: {
    linear: string;
    easeIn: string;
    easeOut: string;
    easeInOut: string;
  };
}

/**
 * Interface para z-index
 */
export interface ThemeZIndex {
  dropdown: number;
  sticky: number;
  fixed: number;
  modal: number;
  popover: number;
  tooltip: number;
  toast: number;
}

/**
 * Interface completa do tema
 */
export interface ThemeConfig {
  name: string;
  colors: ThemeColors;
  typography: ThemeTypography;
  spacing: ThemeSpacing;
  breakpoints: ThemeBreakpoints;
  shadows: ThemeShadows;
  borders: ThemeBorders;
  transitions: ThemeTransitions;
  zIndex: ThemeZIndex;
}

/**
 * Cores do tema claro
 */
const lightColors: ThemeColors = {
  primary: '#3b82f6', // blue-500
  secondary: '#6b7280', // gray-500
  success: '#10b981', // emerald-500
  warning: '#f59e0b', // amber-500
  error: '#ef4444', // red-500
  info: '#06b6d4', // cyan-500
  background: '#ffffff',
  surface: '#f8fafc', // gray-50
  text: {
    primary: '#111827', // gray-900
    secondary: '#6b7280', // gray-500
    disabled: '#9ca3af', // gray-400
    inverse: '#ffffff',
  },
  border: '#e5e7eb', // gray-200
  shadow: 'rgba(0, 0, 0, 0.1)',
  overlay: 'rgba(0, 0, 0, 0.5)',
  accent: '#8b5cf6', // violet-500
};

/**
 * Cores do tema escuro
 */
const darkColors: ThemeColors = {
  primary: '#60a5fa', // blue-400
  secondary: '#9ca3af', // gray-400
  success: '#34d399', // emerald-400
  warning: '#fbbf24', // amber-400
  error: '#f87171', // red-400
  info: '#22d3ee', // cyan-400
  background: '#111827', // gray-900
  surface: '#1f2937', // gray-800
  text: {
    primary: '#f9fafb', // gray-50
    secondary: '#d1d5db', // gray-300
    disabled: '#6b7280', // gray-500
    inverse: '#111827', // gray-900
  },
  border: '#374151', // gray-700
  shadow: 'rgba(0, 0, 0, 0.3)',
  overlay: 'rgba(0, 0, 0, 0.7)',
  accent: '#a78bfa', // violet-400
};

/**
 * Tipografia comum
 */
const typography: ThemeTypography = {
  fontFamily: {
    primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    secondary: 'Georgia, "Times New Roman", Times, serif',
    mono: '"SF Mono", Monaco, Inconsolata, "Roboto Mono", "Source Code Pro", monospace',
  },
  fontSize: {
    xs: '0.75rem', // 12px
    sm: '0.875rem', // 14px
    md: '1rem', // 16px
    lg: '1.125rem', // 18px
    xl: '1.25rem', // 20px
    '2xl': '1.5rem', // 24px
    '3xl': '1.875rem', // 30px
  },
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

/**
 * Espaçamento comum
 */
const spacing: ThemeSpacing = {
  xs: '0.25rem', // 4px
  sm: '0.5rem', // 8px
  md: '1rem', // 16px
  lg: '1.5rem', // 24px
  xl: '2rem', // 32px
  '2xl': '3rem', // 48px
  '3xl': '4rem', // 64px
};

/**
 * Breakpoints responsivos
 */
const breakpoints: ThemeBreakpoints = {
  xs: '480px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

/**
 * Sombras comuns
 */
const shadows: ThemeShadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
};

/**
 * Bordas comuns
 */
const borders: ThemeBorders = {
  radius: {
    none: '0',
    sm: '0.125rem', // 2px
    md: '0.375rem', // 6px
    lg: '0.5rem', // 8px
    xl: '0.75rem', // 12px
    full: '9999px',
  },
  width: {
    thin: '1px',
    normal: '2px',
    thick: '4px',
  },
};

/**
 * Transições comuns
 */
const transitions: ThemeTransitions = {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

/**
 * Z-index comum
 */
const zIndex: ThemeZIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
  toast: 1070,
};

/**
 * Tema claro
 */
export const lightTheme: ThemeConfig = {
  name: 'light',
  colors: lightColors,
  typography,
  spacing,
  breakpoints,
  shadows,
  borders,
  transitions,
  zIndex,
};

/**
 * Tema escuro
 */
export const darkTheme: ThemeConfig = {
  name: 'dark',
  colors: darkColors,
  typography,
  spacing,
  breakpoints,
  shadows,
  borders,
  transitions,
  zIndex,
};

/**
 * Mapa de temas
 */
export const themes: Record<Theme, ThemeConfig> = {
  light: lightTheme,
  dark: darkTheme,
};

/**
 * Função para obter tema
 */
export const getTheme = (themeName: Theme): ThemeConfig => {
  return themes[themeName] || lightTheme;
};

/**
 * Função para gerar variáveis CSS
 */
export const generateCSSVariables = (theme: ThemeConfig): Record<string, string> => {
  const variables: Record<string, string> = {};

  // Cores
  Object.entries(theme.colors).forEach(([key, value]) => {
    if (typeof value === 'string') {
      variables[`--color-${key}`] = value;
    } else if (typeof value === 'object') {
      Object.entries(value).forEach(([subKey, subValue]) => {
        variables[`--color-${key}-${subKey}`] = subValue;
      });
    }
  });

  // Tipografia
  Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
    variables[`--font-size-${key}`] = value;
  });

  Object.entries(theme.typography.fontWeight).forEach(([key, value]) => {
    variables[`--font-weight-${key}`] = value.toString();
  });

  Object.entries(theme.typography.fontFamily).forEach(([key, value]) => {
    variables[`--font-family-${key}`] = value;
  });

  // Espaçamento
  Object.entries(theme.spacing).forEach(([key, value]) => {
    variables[`--spacing-${key}`] = value;
  });

  // Sombras
  Object.entries(theme.shadows).forEach(([key, value]) => {
    variables[`--shadow-${key}`] = value;
  });

  // Bordas
  Object.entries(theme.borders.radius).forEach(([key, value]) => {
    variables[`--border-radius-${key}`] = value;
  });

  Object.entries(theme.borders.width).forEach(([key, value]) => {
    variables[`--border-width-${key}`] = value;
  });

  // Transições
  Object.entries(theme.transitions.duration).forEach(([key, value]) => {
    variables[`--transition-duration-${key}`] = value;
  });

  Object.entries(theme.transitions.easing).forEach(([key, value]) => {
    variables[`--transition-easing-${key}`] = value;
  });

  // Z-index
  Object.entries(theme.zIndex).forEach(([key, value]) => {
    variables[`--z-index-${key}`] = value.toString();
  });

  return variables;
};

/**
 * Função para aplicar tema
 */
export const applyTheme = (themeName: Theme): void => {
  const theme = getTheme(themeName);
  const variables = generateCSSVariables(theme);
  const root = document.documentElement;

  // Aplicar variáveis CSS
  Object.entries(variables).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });

  // Adicionar classe do tema
  root.classList.remove('theme-light', 'theme-dark');
  root.classList.add(`theme-${themeName}`);

  // Salvar preferência
  localStorage.setItem('theme', themeName);
};

/**
 * Função para detectar preferência do sistema
 */
export const getSystemTheme = (): Theme => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
};

/**
 * Função para obter tema salvo ou do sistema
 */
export const getSavedTheme = (): Theme => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('theme') as Theme;
    if (saved && themes[saved]) {
      return saved;
    }
  }
  return getSystemTheme();
};

/**
 * Função para alternar tema
 */
export const toggleTheme = (currentTheme: Theme): Theme => {
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  applyTheme(newTheme);
  return newTheme;
};

/**
 * Hook para escutar mudanças na preferência do sistema
 */
export const watchSystemTheme = (callback: (theme: Theme) => void): (() => void) => {
  if (typeof window === 'undefined' || !window.matchMedia) {
    return () => {};
  }

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handler = (e: MediaQueryListEvent) => {
    callback(e.matches ? 'dark' : 'light');
  };

  mediaQuery.addEventListener('change', handler);

  return () => {
    mediaQuery.removeEventListener('change', handler);
  };
};

/**
 * Utilitários para cores
 */
export const colorUtils = {
  /**
   * Converter hex para rgba
   */
  hexToRgba: (hex: string, alpha: number = 1): string => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  },

  /**
   * Escurecer cor
   */
  darken: (hex: string, amount: number): string => {
    const num = parseInt(hex.slice(1), 16);
    const amt = Math.round(2.55 * amount);
    const R = (num >> 16) - amt;
    const G = (num >> 8 & 0x00FF) - amt;
    const B = (num & 0x0000FF) - amt;
    return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
      (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
      (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
  },

  /**
   * Clarear cor
   */
  lighten: (hex: string, amount: number): string => {
    const num = parseInt(hex.slice(1), 16);
    const amt = Math.round(2.55 * amount);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
      (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
      (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
  },

  /**
   * Obter cor de contraste
   */
  getContrastColor: (hex: string): string => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 128 ? '#000000' : '#ffffff';
  },
};

/**
 * Constantes de cores para status
 */
export const statusColors = {
  new: '#3b82f6', // blue
  progress: '#f59e0b', // amber
  pending: '#ef4444', // red
  resolved: '#10b981', // emerald
  closed: '#6b7280', // gray
} as const;

/**
 * Constantes de cores para prioridade
 */
export const priorityColors = {
  1: '#6b7280', // gray - muito baixa
  2: '#3b82f6', // blue - baixa
  3: '#f59e0b', // amber - média
  4: '#f97316', // orange - alta
  5: '#ef4444', // red - muito alta
} as const;

/**
 * Constantes de cores para níveis
 */
export const levelColors = {
  n1: '#10b981', // emerald
  n2: '#3b82f6', // blue
  n3: '#f59e0b', // amber
  n4: '#ef4444', // red
} as const;