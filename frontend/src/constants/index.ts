// ============================================================================
// CONSTANTES DO DASHBOARD GLPI
// Valores fixos e configurações estáticas da aplicação
// ============================================================================

// ============================================================================
// ROTAS DA APLICAÇÃO
// ============================================================================

export const ROUTES = {
  // Autenticação
  LOGIN: '/login',
  LOGOUT: '/logout',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  
  // Dashboard
  DASHBOARD: '/',
  OVERVIEW: '/overview',
  
  // Tickets
  TICKETS: '/tickets',
  TICKET_DETAIL: '/tickets/:id',
  TICKET_CREATE: '/tickets/create',
  TICKET_EDIT: '/tickets/:id/edit',
  
  // Usuários
  USERS: '/users',
  USER_DETAIL: '/users/:id',
  USER_CREATE: '/users/create',
  USER_EDIT: '/users/:id/edit',
  USER_PROFILE: '/profile',
  
  // Relatórios
  REPORTS: '/reports',
  REPORT_TICKETS: '/reports/tickets',
  REPORT_USERS: '/reports/users',
  REPORT_PERFORMANCE: '/reports/performance',
  
  // Configurações
  SETTINGS: '/settings',
  SETTINGS_GENERAL: '/settings/general',
  SETTINGS_NOTIFICATIONS: '/settings/notifications',
  SETTINGS_SECURITY: '/settings/security',
  
  // Sistema
  SYSTEM: '/system',
  SYSTEM_INFO: '/system/info',
  SYSTEM_LOGS: '/system/logs',
  SYSTEM_BACKUP: '/system/backup',
  
  // Ajuda
  HELP: '/help',
  DOCUMENTATION: '/help/docs',
  SUPPORT: '/help/support',
} as const;

// ============================================================================
// STATUS DE TICKETS
// ============================================================================

export const TICKET_STATUS = {
  OPEN: 'open',
  PENDING: 'pending',
  RESOLVED: 'resolved',
  CLOSED: 'closed',
  CANCELLED: 'cancelled',
} as const;

export const TICKET_STATUS_LABELS = {
  [TICKET_STATUS.OPEN]: 'Aberto',
  [TICKET_STATUS.PENDING]: 'Pendente',
  [TICKET_STATUS.RESOLVED]: 'Resolvido',
  [TICKET_STATUS.CLOSED]: 'Fechado',
  [TICKET_STATUS.CANCELLED]: 'Cancelado',
} as const;

export const TICKET_STATUS_COLORS = {
  [TICKET_STATUS.OPEN]: '#ef4444', // red-500
  [TICKET_STATUS.PENDING]: '#f59e0b', // amber-500
  [TICKET_STATUS.RESOLVED]: '#10b981', // emerald-500
  [TICKET_STATUS.CLOSED]: '#6b7280', // gray-500
  [TICKET_STATUS.CANCELLED]: '#8b5cf6', // violet-500
} as const;

// ============================================================================
// PRIORIDADES DE TICKETS
// ============================================================================

export const TICKET_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent',
  CRITICAL: 'critical',
} as const;

export const TICKET_PRIORITY_LABELS = {
  [TICKET_PRIORITY.LOW]: 'Baixa',
  [TICKET_PRIORITY.MEDIUM]: 'Média',
  [TICKET_PRIORITY.HIGH]: 'Alta',
  [TICKET_PRIORITY.URGENT]: 'Urgente',
  [TICKET_PRIORITY.CRITICAL]: 'Crítica',
} as const;

export const TICKET_PRIORITY_COLORS = {
  [TICKET_PRIORITY.LOW]: '#10b981', // emerald-500
  [TICKET_PRIORITY.MEDIUM]: '#3b82f6', // blue-500
  [TICKET_PRIORITY.HIGH]: '#f59e0b', // amber-500
  [TICKET_PRIORITY.URGENT]: '#ef4444', // red-500
  [TICKET_PRIORITY.CRITICAL]: '#dc2626', // red-600
} as const;

export const TICKET_PRIORITY_VALUES = {
  [TICKET_PRIORITY.LOW]: 1,
  [TICKET_PRIORITY.MEDIUM]: 2,
  [TICKET_PRIORITY.HIGH]: 3,
  [TICKET_PRIORITY.URGENT]: 4,
  [TICKET_PRIORITY.CRITICAL]: 5,
} as const;

// ============================================================================
// CATEGORIAS DE TICKETS
// ============================================================================

export const TICKET_CATEGORIES = {
  HARDWARE: 'hardware',
  SOFTWARE: 'software',
  NETWORK: 'network',
  SECURITY: 'security',
  ACCESS: 'access',
  EMAIL: 'email',
  PRINTER: 'printer',
  PHONE: 'phone',
  OTHER: 'other',
} as const;

export const TICKET_CATEGORY_LABELS = {
  [TICKET_CATEGORIES.HARDWARE]: 'Hardware',
  [TICKET_CATEGORIES.SOFTWARE]: 'Software',
  [TICKET_CATEGORIES.NETWORK]: 'Rede',
  [TICKET_CATEGORIES.SECURITY]: 'Segurança',
  [TICKET_CATEGORIES.ACCESS]: 'Acesso',
  [TICKET_CATEGORIES.EMAIL]: 'E-mail',
  [TICKET_CATEGORIES.PRINTER]: 'Impressora',
  [TICKET_CATEGORIES.PHONE]: 'Telefone',
  [TICKET_CATEGORIES.OTHER]: 'Outros',
} as const;

// ============================================================================
// TIPOS DE USUÁRIO
// ============================================================================

export const USER_ROLES = {
  ADMIN: 'admin',
  TECHNICIAN: 'technician',
  USER: 'user',
  OBSERVER: 'observer',
} as const;

export const USER_ROLE_LABELS = {
  [USER_ROLES.ADMIN]: 'Administrador',
  [USER_ROLES.TECHNICIAN]: 'Técnico',
  [USER_ROLES.USER]: 'Usuário',
  [USER_ROLES.OBSERVER]: 'Observador',
} as const;

export const USER_PERMISSIONS = {
  [USER_ROLES.ADMIN]: [
    'tickets.create',
    'tickets.read',
    'tickets.update',
    'tickets.delete',
    'users.create',
    'users.read',
    'users.update',
    'users.delete',
    'system.read',
    'system.update',
    'reports.read',
    'settings.update',
  ],
  [USER_ROLES.TECHNICIAN]: [
    'tickets.create',
    'tickets.read',
    'tickets.update',
    'users.read',
    'reports.read',
  ],
  [USER_ROLES.USER]: [
    'tickets.create',
    'tickets.read',
  ],
  [USER_ROLES.OBSERVER]: [
    'tickets.read',
    'reports.read',
  ],
} as const;

// ============================================================================
// TIPOS DE NOTIFICAÇÃO
// ============================================================================

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
} as const;

export const NOTIFICATION_TYPE_LABELS = {
  [NOTIFICATION_TYPES.SUCCESS]: 'Sucesso',
  [NOTIFICATION_TYPES.ERROR]: 'Erro',
  [NOTIFICATION_TYPES.WARNING]: 'Aviso',
  [NOTIFICATION_TYPES.INFO]: 'Informação',
} as const;

export const NOTIFICATION_TYPE_COLORS = {
  [NOTIFICATION_TYPES.SUCCESS]: '#10b981', // emerald-500
  [NOTIFICATION_TYPES.ERROR]: '#ef4444', // red-500
  [NOTIFICATION_TYPES.WARNING]: '#f59e0b', // amber-500
  [NOTIFICATION_TYPES.INFO]: '#3b82f6', // blue-500
} as const;

// ============================================================================
// PERÍODOS DE TEMPO
// ============================================================================

export const TIME_PERIODS = {
  LAST_HOUR: '1h',
  LAST_DAY: '1d',
  LAST_WEEK: '7d',
  LAST_MONTH: '30d',
  LAST_QUARTER: '90d',
  LAST_YEAR: '365d',
} as const;

export const TIME_PERIOD_LABELS = {
  [TIME_PERIODS.LAST_HOUR]: 'Última hora',
  [TIME_PERIODS.LAST_DAY]: 'Último dia',
  [TIME_PERIODS.LAST_WEEK]: 'Última semana',
  [TIME_PERIODS.LAST_MONTH]: 'Último mês',
  [TIME_PERIODS.LAST_QUARTER]: 'Último trimestre',
  [TIME_PERIODS.LAST_YEAR]: 'Último ano',
} as const;

// ============================================================================
// FORMATOS DE DATA
// ============================================================================

export const DATE_FORMATS = {
  SHORT: 'dd/MM/yyyy',
  MEDIUM: 'dd/MM/yyyy HH:mm',
  LONG: 'dd/MM/yyyy HH:mm:ss',
  ISO: 'yyyy-MM-dd',
  TIME: 'HH:mm',
  TIME_SECONDS: 'HH:mm:ss',
} as const;

// ============================================================================
// TAMANHOS DE PÁGINA
// ============================================================================

export const PAGE_SIZES = [10, 20, 50, 100] as const;

export const DEFAULT_PAGE_SIZE = 20;

// ============================================================================
// CORES DO TEMA
// ============================================================================

export const THEME_COLORS = {
  PRIMARY: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  GRAY: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  SUCCESS: {
    50: '#ecfdf5',
    100: '#d1fae5',
    200: '#a7f3d0',
    300: '#6ee7b7',
    400: '#34d399',
    500: '#10b981',
    600: '#059669',
    700: '#047857',
    800: '#065f46',
    900: '#064e3b',
  },
  ERROR: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
  WARNING: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },
} as const;

// ============================================================================
// BREAKPOINTS RESPONSIVOS
// ============================================================================

export const BREAKPOINTS = {
  XS: '480px',
  SM: '640px',
  MD: '768px',
  LG: '1024px',
  XL: '1280px',
  '2XL': '1536px',
} as const;

// ============================================================================
// Z-INDEX
// ============================================================================

export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
  TOAST: 1080,
} as const;

// ============================================================================
// ANIMAÇÕES
// ============================================================================

export const ANIMATIONS = {
  DURATION: {
    FAST: '150ms',
    NORMAL: '300ms',
    SLOW: '500ms',
  },
  EASING: {
    EASE_IN: 'cubic-bezier(0.4, 0, 1, 1)',
    EASE_OUT: 'cubic-bezier(0, 0, 0.2, 1)',
    EASE_IN_OUT: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

// ============================================================================
// ÍCONES
// ============================================================================

export const ICONS = {
  // Navegação
  HOME: 'home',
  DASHBOARD: 'dashboard',
  MENU: 'menu',
  CLOSE: 'close',
  BACK: 'arrow-left',
  FORWARD: 'arrow-right',
  
  // Ações
  ADD: 'plus',
  EDIT: 'edit',
  DELETE: 'trash',
  SAVE: 'save',
  CANCEL: 'x',
  SEARCH: 'search',
  FILTER: 'filter',
  REFRESH: 'refresh',
  DOWNLOAD: 'download',
  UPLOAD: 'upload',
  
  // Status
  SUCCESS: 'check-circle',
  ERROR: 'x-circle',
  WARNING: 'alert-triangle',
  INFO: 'info',
  LOADING: 'loader',
  
  // Tickets
  TICKET: 'ticket',
  PRIORITY_HIGH: 'alert-circle',
  PRIORITY_LOW: 'circle',
  ASSIGN: 'user-plus',
  COMMENT: 'message-circle',
  
  // Usuários
  USER: 'user',
  USERS: 'users',
  PROFILE: 'user-circle',
  SETTINGS: 'settings',
  
  // Sistema
  SYSTEM: 'server',
  LOGS: 'file-text',
  BACKUP: 'archive',
  SECURITY: 'shield',
  
  // UI
  EXPAND: 'chevron-down',
  COLLAPSE: 'chevron-up',
  SORT_ASC: 'chevron-up',
  SORT_DESC: 'chevron-down',
  CALENDAR: 'calendar',
  CLOCK: 'clock',
  BELL: 'bell',
  MAIL: 'mail',
  PHONE: 'phone',
  
  // Tema
  LIGHT_MODE: 'sun',
  DARK_MODE: 'moon',
} as const;

// ============================================================================
// MENSAGENS PADRÃO
// ============================================================================

export const MESSAGES = {
  // Sucesso
  SUCCESS: {
    SAVE: 'Dados salvos com sucesso!',
    CREATE: 'Item criado com sucesso!',
    UPDATE: 'Item atualizado com sucesso!',
    DELETE: 'Item excluído com sucesso!',
    LOGIN: 'Login realizado com sucesso!',
    LOGOUT: 'Logout realizado com sucesso!',
  },
  
  // Erro
  ERROR: {
    GENERIC: 'Ocorreu um erro inesperado. Tente novamente.',
    NETWORK: 'Erro de conexão. Verifique sua internet.',
    UNAUTHORIZED: 'Você não tem permissão para esta ação.',
    NOT_FOUND: 'Item não encontrado.',
    VALIDATION: 'Dados inválidos. Verifique os campos.',
    SERVER: 'Erro interno do servidor.',
  },
  
  // Confirmação
  CONFIRM: {
    DELETE: 'Tem certeza que deseja excluir este item?',
    LOGOUT: 'Tem certeza que deseja sair?',
    DISCARD: 'Tem certeza que deseja descartar as alterações?',
  },
  
  // Loading
  LOADING: {
    DEFAULT: 'Carregando...',
    SAVING: 'Salvando...',
    DELETING: 'Excluindo...',
    LOADING_DATA: 'Carregando dados...',
  },
  
  // Validação
  VALIDATION: {
    REQUIRED: 'Este campo é obrigatório',
    EMAIL: 'Digite um e-mail válido',
    MIN_LENGTH: 'Mínimo de {min} caracteres',
    MAX_LENGTH: 'Máximo de {max} caracteres',
    PASSWORD_WEAK: 'Senha muito fraca',
    PASSWORDS_DONT_MATCH: 'Senhas não coincidem',
  },
} as const;

// ============================================================================
// REGEX PATTERNS
// ============================================================================

export const REGEX = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\(?\d{2}\)?[\s-]?\d{4,5}[\s-]?\d{4}$/,
  CPF: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
  CNPJ: /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/,
} as const;

// ============================================================================
// LIMITES
// ============================================================================

export const LIMITS = {
  // Texto
  TITLE_MAX_LENGTH: 100,
  DESCRIPTION_MAX_LENGTH: 1000,
  COMMENT_MAX_LENGTH: 500,
  
  // Upload
  FILE_MAX_SIZE: 10 * 1024 * 1024, // 10MB
  IMAGE_MAX_SIZE: 5 * 1024 * 1024, // 5MB
  
  // Paginação
  MAX_PAGE_SIZE: 100,
  
  // Cache
  CACHE_MAX_ITEMS: 100,
  
  // Notificações
  MAX_NOTIFICATIONS: 50,
} as const;

// ============================================================================
// TIPOS DE ARQUIVO
// ============================================================================

export const FILE_TYPES = {
  IMAGES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  DOCUMENTS: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ],
  ARCHIVES: [
    'application/zip',
    'application/x-rar-compressed',
    'application/x-7z-compressed',
  ],
} as const;

// ============================================================================
// EXPORTAÇÃO CONSOLIDADA
// ============================================================================
export const constants = {
  ROUTES,
  TICKET_STATUS,
  TICKET_STATUS_LABELS,
  TICKET_STATUS_COLORS,
  TICKET_PRIORITY,
  TICKET_PRIORITY_LABELS,
  TICKET_PRIORITY_COLORS,
  TICKET_PRIORITY_VALUES,
  TICKET_CATEGORIES,
  TICKET_CATEGORY_LABELS,
  USER_ROLES,
  USER_ROLE_LABELS,
  USER_PERMISSIONS,
  NOTIFICATION_TYPES,
  NOTIFICATION_TYPE_LABELS,
  NOTIFICATION_TYPE_COLORS,
  TIME_PERIODS,
  TIME_PERIOD_LABELS,
  DATE_FORMATS,
  PAGE_SIZES,
  DEFAULT_PAGE_SIZE,
  THEME_COLORS,
  BREAKPOINTS,
  Z_INDEX,
  ANIMATIONS,
  ICONS,
  MESSAGES,
  REGEX,
  LIMITS,
  FILE_TYPES,
};

export default constants;