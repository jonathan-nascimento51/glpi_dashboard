import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Utilitarios de formatacao
export const formatters = {
  // Formatacao de data
  formatDate: (date: string | Date, format: 'short' | 'long' | 'relative' = 'short'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) {
      return 'Data invalida';
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
      case 'relative':
        const now = new Date();
        const diffMs = now.getTime() - dateObj.getTime();
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Hoje';
        if (diffDays === 1) return 'Ontem';
        if (diffDays < 7) return `${diffDays} dias atras`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} semanas atras`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} meses atras`;
        return `${Math.floor(diffDays / 365)} anos atras`;
      default:
        return dateObj.toLocaleDateString('pt-BR');
    }
  },
  
  // Formatacao de tempo
  formatTime: (date: string | Date): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) {
      return 'Hora invalida';
    }
    
    return dateObj.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  },
  
  // Formatacao de duracao
  formatDuration: (minutes: number): string => {
    if (minutes < 0) return '0 min';
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (hours === 0) {
      return `${remainingMinutes} min`;
    }
    
    if (remainingMinutes === 0) {
      return `${hours}h`;
    }
    
    return `${hours}h ${remainingMinutes}min`;
  },
  
  // Formatacao de numeros
  formatNumber: (num: number, decimals: number = 0): string => {
    return num.toLocaleString('pt-BR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  },
  
  // Formatacao de porcentagem
  formatPercentage: (value: number, total: number, decimals: number = 1): string => {
    if (total === 0) return '0%';
    const percentage = (value / total) * 100;
    return `${percentage.toFixed(decimals)}%`;
  },
  
  // Formatacao de tamanho de arquivo
  formatFileSize: (bytes: number): string => {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  }
};

// Utilitarios de validacao
export const validators = {
  // Validacao de email
  isValidEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },
  
  // Validacao de senha
  isValidPassword: (password: string): { valid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('Senha deve ter pelo menos 8 caracteres');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Senha deve conter pelo menos uma letra maiuscula');
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Senha deve conter pelo menos uma letra minuscula');
    }
    
    if (!/\d/.test(password)) {
      errors.push('Senha deve conter pelo menos um numero');
    }
    
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Senha deve conter pelo menos um caractere especial');
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  },
  
  // Validacao de CPF
  isValidCPF: (cpf: string): boolean => {
    const cleanCPF = cpf.replace(/\D/g, '');
    
    if (cleanCPF.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cleanCPF)) return false;
    
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cleanCPF.charAt(i)) * (10 - i);
    }
    
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cleanCPF.charAt(9))) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cleanCPF.charAt(i)) * (11 - i);
    }
    
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cleanCPF.charAt(10))) return false;
    
    return true;
  },
  
  // Validacao de telefone
  isValidPhone: (phone: string): boolean => {
    const cleanPhone = phone.replace(/\D/g, '');
    return cleanPhone.length === 10 || cleanPhone.length === 11;
  },
  
  // Validacao de URL
  isValidURL: (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
};

// Utilitarios de string
export const stringUtils = {
  // Capitalizar primeira letra
  capitalize: (str: string): string => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },
  
  // Capitalizar cada palavra
  capitalizeWords: (str: string): string => {
    if (!str) return '';
    return str.split(' ').map(word => stringUtils.capitalize(word)).join(' ');
  },
  
  // Truncar texto
  truncate: (str: string, length: number, suffix: string = '...'): string => {
    if (!str || str.length <= length) return str;
    return str.substring(0, length) + suffix;
  },
  
  // Remover acentos
  removeAccents: (str: string): string => {
    return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  },
  
  // Gerar slug
  generateSlug: (str: string): string => {
    return stringUtils.removeAccents(str)
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  },
  
  // Mascarar texto
  mask: (str: string, visibleChars: number = 4, maskChar: string = '*'): string => {
    if (!str || str.length <= visibleChars) return str;
    const visible = str.slice(-visibleChars);
    const masked = maskChar.repeat(str.length - visibleChars);
    return masked + visible;
  }
};

// Utilitarios de array
export const arrayUtils = {
  // Remover duplicatas
  unique: <T>(arr: T[]): T[] => {
    return [...new Set(arr)];
  },
  
  // Agrupar por propriedade
  groupBy: <T, K extends keyof T>(arr: T[], key: K): Record<string, T[]> => {
    return arr.reduce((groups, item) => {
      const groupKey = String(item[key]);
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(item);
      return groups;
    }, {} as Record<string, T[]>);
  },
  
  // Ordenar por propriedade
  sortBy: <T, K extends keyof T>(arr: T[], key: K, direction: 'asc' | 'desc' = 'asc'): T[] => {
    return [...arr].sort((a, b) => {
      const aVal = a[key];
      const bVal = b[key];
      
      if (aVal < bVal) return direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      return 0;
    });
  },
  
  // Paginar array
  paginate: <T>(arr: T[], page: number, limit: number): { data: T[]; pagination: any } => {
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const data = arr.slice(startIndex, endIndex);
    
    return {
      data,
      pagination: {
        page,
        limit,
        total: arr.length,
        totalPages: Math.ceil(arr.length / limit),
        hasNext: endIndex < arr.length,
        hasPrev: page > 1
      }
    };
  },
  
  // Buscar em array
  search: <T>(arr: T[], query: string, keys: (keyof T)[]): T[] => {
    const lowerQuery = query.toLowerCase();
    return arr.filter(item => 
      keys.some(key => 
        String(item[key]).toLowerCase().includes(lowerQuery)
      )
    );
  }
};

// Utilitarios de objeto
export const objectUtils = {
  // Deep clone
  deepClone: <T>(obj: T): T => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
    if (obj instanceof Array) return obj.map(item => objectUtils.deepClone(item)) as unknown as T;
    
    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = objectUtils.deepClone(obj[key]);
      }
    }
    return cloned;
  },
  
  // Verificar se objeto esta vazio
  isEmpty: (obj: any): boolean => {
    if (obj === null || obj === undefined) return true;
    if (typeof obj === 'string' || Array.isArray(obj)) return obj.length === 0;
    if (typeof obj === 'object') return Object.keys(obj).length === 0;
    return false;
  },
  
  // Pegar valor aninhado
  get: (obj: any, path: string, defaultValue?: any): any => {
    const keys = path.split('.');
    let result = obj;
    
    for (const key of keys) {
      if (result === null || result === undefined || !(key in result)) {
        return defaultValue;
      }
      result = result[key];
    }
    
    return result;
  },
  
  // Definir valor aninhado
  set: (obj: any, path: string, value: any): void => {
    const keys = path.split('.');
    let current = obj;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }
    
    current[keys[keys.length - 1]] = value;
  },
  
  // Omitir propriedades
  omit: <T, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> => {
    const result = { ...obj };
    keys.forEach(key => delete result[key]);
    return result;
  },
  
  // Pegar apenas propriedades especificas
  pick: <T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> => {
    const result = {} as Pick<T, K>;
    keys.forEach(key => {
      if (key in obj) {
        result[key] = obj[key];
      }
    });
    return result;
  }
};

// Utilitarios de localStorage
export const storageUtils = {
  // Salvar no localStorage
  set: (key: string, value: any): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Erro ao salvar no localStorage:', error);
    }
  },
  
  // Buscar do localStorage
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error('Erro ao buscar do localStorage:', error);
      return defaultValue || null;
    }
  },
  
  // Remover do localStorage
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Erro ao remover do localStorage:', error);
    }
  },
  
  // Limpar localStorage
  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Erro ao limpar localStorage:', error);
    }
  }
};

// Utilitarios de debounce e throttle
export const performanceUtils = {
  // Debounce
  debounce: <T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void => {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  },
  
  // Throttle
  throttle: <T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void => {
    let lastCall = 0;
    
    return (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        func(...args);
      }
    };
  }
};

describe('Testes Unitarios de Utilitarios', () => {
  describe('Formatters', () => {
    describe('formatDate', () => {
      it('deve formatar data no formato curto', () => {
        const date = new Date('2024-01-15T10:30:00Z');
        const formatted = formatters.formatDate(date, 'short');
        expect(formatted).toMatch(/\d{2}\/\d{2}\/\d{4}/);
      });
      
      it('deve formatar data no formato longo', () => {
        const date = new Date('2024-01-15T10:30:00Z');
        const formatted = formatters.formatDate(date, 'long');
        expect(formatted).toContain('2024');
        expect(formatted).toContain('janeiro');
      });
      
      it('deve formatar data relativa', () => {
        const today = new Date();
        const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
        
        expect(formatters.formatDate(today, 'relative')).toBe('Hoje');
        expect(formatters.formatDate(yesterday, 'relative')).toBe('Ontem');
      });
      
      it('deve lidar com datas invalidas', () => {
        expect(formatters.formatDate('invalid-date')).toBe('Data invalida');
      });
      
      it('deve aceitar string como entrada', () => {
        const formatted = formatters.formatDate('2024-01-15', 'short');
        expect(formatted).toMatch(/\d{2}\/\d{2}\/\d{4}/);
      });
    });
    
    describe('formatTime', () => {
      it('deve formatar hora corretamente', () => {
        const date = new Date('2024-01-15T14:30:00Z');
        const formatted = formatters.formatTime(date);
        expect(formatted).toMatch(/\d{2}:\d{2}/);
      });
      
      it('deve lidar com horas invalidas', () => {
        expect(formatters.formatTime('invalid-time')).toBe('Hora invalida');
      });
    });
    
    describe('formatDuration', () => {
      it('deve formatar minutos', () => {
        expect(formatters.formatDuration(30)).toBe('30 min');
        expect(formatters.formatDuration(0)).toBe('0 min');
      });
      
      it('deve formatar horas', () => {
        expect(formatters.formatDuration(60)).toBe('1h');
        expect(formatters.formatDuration(120)).toBe('2h');
      });
      
      it('deve formatar horas e minutos', () => {
        expect(formatters.formatDuration(90)).toBe('1h 30min');
        expect(formatters.formatDuration(150)).toBe('2h 30min');
      });
      
      it('deve lidar com valores negativos', () => {
        expect(formatters.formatDuration(-30)).toBe('0 min');
      });
    });
    
    describe('formatNumber', () => {
      it('deve formatar numeros inteiros', () => {
        expect(formatters.formatNumber(1234)).toBe('1.234');
        expect(formatters.formatNumber(1000000)).toBe('1.000.000');
      });
      
      it('deve formatar numeros com decimais', () => {
        expect(formatters.formatNumber(1234.56, 2)).toBe('1.234,56');
        expect(formatters.formatNumber(1234.5, 2)).toBe('1.234,50');
      });
    });
    
    describe('formatPercentage', () => {
      it('deve calcular porcentagem corretamente', () => {
        expect(formatters.formatPercentage(25, 100)).toBe('25.0%');
        expect(formatters.formatPercentage(1, 3, 2)).toBe('33.33%');
      });
      
      it('deve lidar com divisao por zero', () => {
        expect(formatters.formatPercentage(10, 0)).toBe('0%');
      });
    });
    
    describe('formatFileSize', () => {
      it('deve formatar bytes', () => {
        expect(formatters.formatFileSize(0)).toBe('0 B');
        expect(formatters.formatFileSize(512)).toBe('512 B');
      });
      
      it('deve formatar KB', () => {
        expect(formatters.formatFileSize(1024)).toBe('1 KB');
        expect(formatters.formatFileSize(1536)).toBe('1.5 KB');
      });
      
      it('deve formatar MB', () => {
        expect(formatters.formatFileSize(1048576)).toBe('1 MB');
        expect(formatters.formatFileSize(1572864)).toBe('1.5 MB');
      });
      
      it('deve formatar GB', () => {
        expect(formatters.formatFileSize(1073741824)).toBe('1 GB');
      });
    });
  });
  
  describe('Validators', () => {
    describe('isValidEmail', () => {
      it('deve validar emails validos', () => {
        expect(validators.isValidEmail('test@example.com')).toBe(true);
        expect(validators.isValidEmail('user.name@domain.co.uk')).toBe(true);
        expect(validators.isValidEmail('user+tag@example.org')).toBe(true);
      });
      
      it('deve rejeitar emails invalidos', () => {
        expect(validators.isValidEmail('invalid-email')).toBe(false);
        expect(validators.isValidEmail('test@')).toBe(false);
        expect(validators.isValidEmail('@example.com')).toBe(false);
        expect(validators.isValidEmail('test..test@example.com')).toBe(false);
      });
    });
    
    describe('isValidPassword', () => {
      it('deve validar senhas fortes', () => {
        const result = validators.isValidPassword('StrongPass123!');
        expect(result.valid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
      
      it('deve rejeitar senhas fracas', () => {
        const result = validators.isValidPassword('weak');
        expect(result.valid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
      
      it('deve identificar problemas especificos', () => {
        const result = validators.isValidPassword('lowercase123');
        expect(result.errors).toContain('Senha deve conter pelo menos uma letra maiuscula');
        expect(result.errors).toContain('Senha deve conter pelo menos um caractere especial');
      });
    });
    
    describe('isValidCPF', () => {
      it('deve validar CPFs validos', () => {
        expect(validators.isValidCPF('11144477735')).toBe(true);
        expect(validators.isValidCPF('111.444.777-35')).toBe(true);
      });
      
      it('deve rejeitar CPFs invalidos', () => {
        expect(validators.isValidCPF('11111111111')).toBe(false);
        expect(validators.isValidCPF('123456789')).toBe(false);
        expect(validators.isValidCPF('11144477736')).toBe(false);
      });
    });
    
    describe('isValidPhone', () => {
      it('deve validar telefones validos', () => {
        expect(validators.isValidPhone('1234567890')).toBe(true);
        expect(validators.isValidPhone('12345678901')).toBe(true);
        expect(validators.isValidPhone('(12) 3456-7890')).toBe(true);
        expect(validators.isValidPhone('(12) 99999-9999')).toBe(true);
      });
      
      it('deve rejeitar telefones invalidos', () => {
        expect(validators.isValidPhone('123456789')).toBe(false);
        expect(validators.isValidPhone('123456789012')).toBe(false);
      });
    });
    
    describe('isValidURL', () => {
      it('deve validar URLs validas', () => {
        expect(validators.isValidURL('https://example.com')).toBe(true);
        expect(validators.isValidURL('http://localhost:3000')).toBe(true);
        expect(validators.isValidURL('ftp://files.example.com')).toBe(true);
      });
      
      it('deve rejeitar URLs invalidas', () => {
        expect(validators.isValidURL('not-a-url')).toBe(false);
        expect(validators.isValidURL('http://')).toBe(false);
        expect(validators.isValidURL('')).toBe(false);
      });
    });
  });
  
  describe('String Utils', () => {
    describe('capitalize', () => {
      it('deve capitalizar primeira letra', () => {
        expect(stringUtils.capitalize('hello')).toBe('Hello');
        expect(stringUtils.capitalize('WORLD')).toBe('World');
        expect(stringUtils.capitalize('')).toBe('');
      });
    });
    
    describe('capitalizeWords', () => {
      it('deve capitalizar cada palavra', () => {
        expect(stringUtils.capitalizeWords('hello world')).toBe('Hello World');
        expect(stringUtils.capitalizeWords('HELLO WORLD')).toBe('Hello World');
        expect(stringUtils.capitalizeWords('hello  world')).toBe('Hello  World');
      });
    });
    
    describe('truncate', () => {
      it('deve truncar texto longo', () => {
        expect(stringUtils.truncate('Hello World', 5)).toBe('Hello...');
        expect(stringUtils.truncate('Hello World', 5, '***')).toBe('Hello***');
      });
      
      it('deve manter texto curto', () => {
        expect(stringUtils.truncate('Hi', 5)).toBe('Hi');
        expect(stringUtils.truncate('Hello', 5)).toBe('Hello');
      });
    });
    
    describe('removeAccents', () => {
      it('deve remover acentos', () => {
        expect(stringUtils.removeAccents('cafe')).toBe('cafe');
        expect(stringUtils.removeAccents('acucar')).toBe('acucar');
        expect(stringUtils.removeAccents('coracao')).toBe('coracao');
      });
    });
    
    describe('generateSlug', () => {
      it('deve gerar slug valido', () => {
        expect(stringUtils.generateSlug('Hello World')).toBe('hello-world');
        expect(stringUtils.generateSlug('Cafe com Acucar')).toBe('cafe-com-acucar');
        expect(stringUtils.generateSlug('Test!@#$%^&*()')).toBe('test');
      });
    });
    
    describe('mask', () => {
      it('deve mascarar texto', () => {
        expect(stringUtils.mask('1234567890', 4)).toBe('******7890');
        expect(stringUtils.mask('password', 2, '#')).toBe('######rd');
      });
      
      it('deve manter texto curto', () => {
        expect(stringUtils.mask('123', 4)).toBe('123');
      });
    });
  });
  
  describe('Array Utils', () => {
    describe('unique', () => {
      it('deve remover duplicatas', () => {
        expect(arrayUtils.unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3]);
        expect(arrayUtils.unique(['a', 'b', 'a', 'c'])).toEqual(['a', 'b', 'c']);
      });
    });
    
    describe('groupBy', () => {
      it('deve agrupar por propriedade', () => {
        const data = [
          { name: 'John', age: 25, city: 'NY' },
          { name: 'Jane', age: 30, city: 'NY' },
          { name: 'Bob', age: 25, city: 'LA' }
        ];
        
        const grouped = arrayUtils.groupBy(data, 'city');
        expect(grouped['NY']).toHaveLength(2);
        expect(grouped['LA']).toHaveLength(1);
      });
    });
    
    describe('sortBy', () => {
      it('deve ordenar por propriedade', () => {
        const data = [
          { name: 'John', age: 30 },
          { name: 'Jane', age: 25 },
          { name: 'Bob', age: 35 }
        ];
        
        const sorted = arrayUtils.sortBy(data, 'age');
        expect(sorted[0].age).toBe(25);
        expect(sorted[2].age).toBe(35);
        
        const sortedDesc = arrayUtils.sortBy(data, 'age', 'desc');
        expect(sortedDesc[0].age).toBe(35);
        expect(sortedDesc[2].age).toBe(25);
      });
    });
    
    describe('paginate', () => {
      it('deve paginar array', () => {
        const data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        const result = arrayUtils.paginate(data, 2, 3);
        
        expect(result.data).toEqual([4, 5, 6]);
        expect(result.pagination.page).toBe(2);
        expect(result.pagination.totalPages).toBe(4);
        expect(result.pagination.hasNext).toBe(true);
        expect(result.pagination.hasPrev).toBe(true);
      });
    });
    
    describe('search', () => {
      it('deve buscar em array', () => {
        const data = [
          { name: 'John Doe', email: 'john@example.com' },
          { name: 'Jane Smith', email: 'jane@example.com' },
          { name: 'Bob Johnson', email: 'bob@test.com' }
        ];
        
        const results = arrayUtils.search(data, 'john', ['name', 'email']);
        expect(results).toHaveLength(2);
        expect(results[0].name).toBe('John Doe');
        expect(results[1].name).toBe('Bob Johnson');
      });
    });
  });
  
  describe('Object Utils', () => {
    describe('deepClone', () => {
      it('deve clonar objeto profundamente', () => {
        const original = {
          name: 'John',
          address: {
            street: '123 Main St',
            city: 'NY'
          },
          hobbies: ['reading', 'coding']
        };
        
        const cloned = objectUtils.deepClone(original);
        cloned.address.city = 'LA';
        cloned.hobbies.push('gaming');
        
        expect(original.address.city).toBe('NY');
        expect(original.hobbies).toHaveLength(2);
        expect(cloned.address.city).toBe('LA');
        expect(cloned.hobbies).toHaveLength(3);
      });
      
      it('deve clonar datas', () => {
        const date = new Date('2024-01-15');
        const cloned = objectUtils.deepClone(date);
        
        expect(cloned).toBeInstanceOf(Date);
        expect(cloned.getTime()).toBe(date.getTime());
        expect(cloned).not.toBe(date);
      });
    });
    
    describe('isEmpty', () => {
      it('deve detectar objetos vazios', () => {
        expect(objectUtils.isEmpty({})).toBe(true);
        expect(objectUtils.isEmpty([])).toBe(true);
        expect(objectUtils.isEmpty('')).toBe(true);
        expect(objectUtils.isEmpty(null)).toBe(true);
        expect(objectUtils.isEmpty(undefined)).toBe(true);
        
        expect(objectUtils.isEmpty({ a: 1 })).toBe(false);
        expect(objectUtils.isEmpty([1])).toBe(false);
        expect(objectUtils.isEmpty('text')).toBe(false);
      });
    });
    
    describe('get', () => {
      it('deve buscar valor aninhado', () => {
        const obj = {
          user: {
            profile: {
              name: 'John'
            }
          }
        };
        
        expect(objectUtils.get(obj, 'user.profile.name')).toBe('John');
        expect(objectUtils.get(obj, 'user.profile.age', 25)).toBe(25);
        expect(objectUtils.get(obj, 'invalid.path')).toBeUndefined();
      });
    });
    
    describe('set', () => {
      it('deve definir valor aninhado', () => {
        const obj = {};
        objectUtils.set(obj, 'user.profile.name', 'John');
        
        expect(obj).toEqual({
          user: {
            profile: {
              name: 'John'
            }
          }
        });
      });
    });
    
    describe('omit', () => {
      it('deve omitir propriedades', () => {
        const obj = { a: 1, b: 2, c: 3 };
        const result = objectUtils.omit(obj, ['b', 'c']);
        
        expect(result).toEqual({ a: 1 });
        expect(obj).toEqual({ a: 1, b: 2, c: 3 }); // Original nao modificado
      });
    });
    
    describe('pick', () => {
      it('deve pegar apenas propriedades especificas', () => {
        const obj = { a: 1, b: 2, c: 3 };
        const result = objectUtils.pick(obj, ['a', 'c']);
        
        expect(result).toEqual({ a: 1, c: 3 });
      });
    });
  });
  
  describe('Storage Utils', () => {
    beforeEach(() => {
      localStorage.clear();
    });
    
    describe('set e get', () => {
      it('deve salvar e recuperar dados', () => {
        const data = { name: 'John', age: 30 };
        storageUtils.set('user', data);
        
        const retrieved = storageUtils.get('user');
        expect(retrieved).toEqual(data);
      });
      
      it('deve retornar valor padrao para chave inexistente', () => {
        const defaultValue = { name: 'Default' };
        const result = storageUtils.get('nonexistent', defaultValue);
        
        expect(result).toEqual(defaultValue);
      });
    });
    
    describe('remove', () => {
      it('deve remover item', () => {
        storageUtils.set('test', 'value');
        expect(storageUtils.get('test')).toBe('value');
        
        storageUtils.remove('test');
        expect(storageUtils.get('test')).toBeNull();
      });
    });
    
    describe('clear', () => {
      it('deve limpar todo o storage', () => {
        storageUtils.set('item1', 'value1');
        storageUtils.set('item2', 'value2');
        
        storageUtils.clear();
        
        expect(storageUtils.get('item1')).toBeNull();
        expect(storageUtils.get('item2')).toBeNull();
      });
    });
  });
  
  describe('Performance Utils', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });
    
    afterEach(() => {
      vi.useRealTimers();
    });
    
    describe('debounce', () => {
      it('deve atrasar execucao da funcao', () => {
        const mockFn = vi.fn();
        const debouncedFn = performanceUtils.debounce(mockFn, 100);
        
        debouncedFn('arg1');
        debouncedFn('arg2');
        debouncedFn('arg3');
        
        expect(mockFn).not.toHaveBeenCalled();
        
        vi.advanceTimersByTime(100);
        
        expect(mockFn).toHaveBeenCalledTimes(1);
        expect(mockFn).toHaveBeenCalledWith('arg3');
      });
    });
    
    describe('throttle', () => {
      it('deve limitar execucao da funcao', () => {
        const mockFn = vi.fn();
        const throttledFn = performanceUtils.throttle(mockFn, 100);
        
        throttledFn('arg1');
        throttledFn('arg2');
        throttledFn('arg3');
        
        expect(mockFn).toHaveBeenCalledTimes(1);
        expect(mockFn).toHaveBeenCalledWith('arg1');
        
        vi.advanceTimersByTime(100);
        
        throttledFn('arg4');
        expect(mockFn).toHaveBeenCalledTimes(2);
        expect(mockFn).toHaveBeenCalledWith('arg4');
      });
    });
  });
});