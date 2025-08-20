/**
 * Sistema Avançado de Validação Visual do Dashboard
 *
 * Este sistema garante que os dados estão sendo renderizados corretamente
 * através de verificações programáticas e visuais automatizadas.
 */

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  metrics: {
    novos: number;
    pendentes: number;
    progresso: number;
    resolvidos: number;
  };
  timestamp: string;
  screenshot?: string; // Base64 da captura de tela
}

export interface VisualValidationConfig {
  enableScreenshots: boolean;
  enableDOMValidation: boolean;
  enableAPIComparison: boolean;
  toleranceThreshold: number; // Tolerância para diferenças de valores
  retryAttempts: number;
  retryDelay: number; // ms
}

class VisualValidator {
  private config: VisualValidationConfig = {
    enableScreenshots: true,
    enableDOMValidation: true,
    enableAPIComparison: true,
    toleranceThreshold: 0, // Zero tolerância para inconsistências
    retryAttempts: 3,
    retryDelay: 1000,
  };

  /**
   * Executa validação visual completa do dashboard
   */
  async validateDashboardRendering(): Promise<ValidationResult> {
    console.log('🔍 Iniciando validação visual completa do dashboard...');

    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      metrics: { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 },
      timestamp: new Date().toISOString(),
    };

    try {
      // 1. Aguardar carregamento completo
      await this.waitForDashboardLoad();

      // 2. Validação do DOM
      if (this.config.enableDOMValidation) {
        const domValidation = await this.validateDOMElements();
        result.metrics = domValidation.metrics;
        result.errors.push(...domValidation.errors);
        result.warnings.push(...domValidation.warnings);
      }

      // 3. Comparação com API
      if (this.config.enableAPIComparison) {
        const apiValidation = await this.validateAgainstAPI(result.metrics);
        result.errors.push(...apiValidation.errors);
        result.warnings.push(...apiValidation.warnings);
      }

      // 4. Captura de tela para evidência
      if (this.config.enableScreenshots) {
        result.screenshot = await this.captureScreenshot();
      }

      // 5. Validação de consistência visual
      const visualConsistency = await this.validateVisualConsistency();
      result.errors.push(...visualConsistency.errors);
      result.warnings.push(...visualConsistency.warnings);

      result.isValid = result.errors.length === 0;

      // Log do resultado
      if (result.isValid) {
        console.log('✅ VALIDAÇÃO VISUAL PASSOU - Dashboard renderizado corretamente');
        console.log('📊 Métricas validadas:', result.metrics);
      } else {
        console.error('❌ VALIDAÇÃO VISUAL FALHOU');
        console.error('🚨 Erros encontrados:', result.errors);
        if (result.warnings.length > 0) {
          console.warn('⚠️ Avisos:', result.warnings);
        }
      }

      return result;
    } catch (error) {
      result.isValid = false;
      result.errors.push(`Erro durante validação visual: ${error}`);
      console.error('💥 Erro crítico na validação visual:', error);
      return result;
    }
  }

  /**
   * Aguarda o carregamento completo do dashboard
   */
  private async waitForDashboardLoad(): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Timeout: Dashboard não carregou em 10 segundos'));
      }, 10000);

      const checkLoad = () => {
        // Verificar se os cards principais estão presentes
        const cards = document.querySelectorAll(
          '[data-testid="metric-card"], .metric-card, [class*="card"]'
        );
        const hasMetrics = cards.length >= 4; // Esperamos pelo menos 4 cards

        // Verificar se não há spinners ou loading
        const loadingElements = document.querySelectorAll(
          '[data-testid="loading"], .loading, .spinner'
        );
        const isLoading = loadingElements.length > 0;

        if (hasMetrics && !isLoading) {
          clearTimeout(timeout);
          resolve();
        } else {
          setTimeout(checkLoad, 500);
        }
      };

      checkLoad();
    });
  }

  /**
   * Valida elementos do DOM e extrai métricas
   */
  private async validateDOMElements(): Promise<{
    metrics: ValidationResult['metrics'];
    errors: string[];
    warnings: string[];
  }> {
    const errors: string[] = [];
    const warnings: string[] = [];
    const metrics = { novos: 0, pendentes: 0, progresso: 0, resolvidos: 0 };

    try {
      // Estratégias múltiplas para encontrar os cards de métricas
      const cardSelectors = [
        '[data-testid="metric-card"]',
        '.metric-card',
        '[class*="card"]',
        '[class*="Card"]',
        'div:has(h3:contains("NOVOS"))',
        'div:has(h3:contains("PENDENTES"))',
        'div:has(h3:contains("PROGRESSO"))',
        'div:has(h3:contains("RESOLVIDOS"))',
      ];

      let cards: NodeListOf<Element> | null = null;

      for (const selector of cardSelectors) {
        try {
          cards = document.querySelectorAll(selector);
          if (cards.length >= 4) break;
        } catch (e) {
          // Selector inválido, continuar
        }
      }

      if (!cards || cards.length < 4) {
        errors.push('Cards de métricas não encontrados no DOM');
        return { metrics, errors, warnings };
      }

      // Extrair valores dos cards
      const metricTypes = ['novos', 'pendentes', 'progresso', 'resolvidos'];
      const metricKeywords = {
        novos: ['NOVOS', 'NEW', 'NOVO'],
        pendentes: ['PENDENTES', 'PENDING', 'PENDENTE'],
        progresso: ['PROGRESSO', 'PROGRESS', 'EM PROGRESSO'],
        resolvidos: ['RESOLVIDOS', 'RESOLVED', 'RESOLVIDO'],
      };

      cards.forEach((card, index) => {
        try {
          const cardText = card.textContent || '';
          const cardHTML = card.innerHTML;

          // Identificar tipo de métrica
          let metricType: keyof typeof metrics | null = null;
          for (const [type, keywords] of Object.entries(metricKeywords)) {
            if (keywords.some(keyword => cardText.toUpperCase().includes(keyword))) {
              metricType = type as keyof typeof metrics;
              break;
            }
          }

          if (!metricType) {
            warnings.push(`Card ${index + 1}: Tipo de métrica não identificado`);
            return;
          }

          // Extrair valor numérico (considerando formatação brasileira com pontos)
          // Primeiro tenta encontrar números formatados (ex: 1.234, 9.778)
          const formattedNumberMatches = cardText.match(/\b\d{1,3}(?:\.\d{3})*\b/g);
          // Depois tenta números simples
          const simpleNumberMatches = cardText.match(/\b\d+\b/g);

          const numberMatches = formattedNumberMatches || simpleNumberMatches;

          if (!numberMatches || numberMatches.length === 0) {
            errors.push(`Card ${metricType}: Valor numérico não encontrado`);
            return;
          }

          // Pegar o primeiro número encontrado e remover pontos para parsing
          const rawValue = numberMatches[0].replace(/\./g, '');
          const value = parseInt(rawValue, 10);

          if (isNaN(value)) {
            errors.push(`Card ${metricType}: Valor não é um número válido`);
            return;
          }

          metrics[metricType] = value;

          // Validar se o valor faz sentido
          if (value < 0) {
            errors.push(`Card ${metricType}: Valor negativo (${value})`);
          }

          console.log(`📊 Card ${metricType}: ${value}`);
        } catch (error) {
          errors.push(`Erro ao processar card ${index + 1}: ${error}`);
        }
      });

      // Validações adicionais
      const totalMetrics = Object.values(metrics).reduce((sum, val) => sum + val, 0);
      if (totalMetrics === 0) {
        errors.push('Todas as métricas estão zeradas - possível problema de renderização');
      }

      return { metrics, errors, warnings };
    } catch (error) {
      errors.push(`Erro durante validação do DOM: ${error}`);
      return { metrics, errors, warnings };
    }
  }

  /**
   * Compara métricas do DOM com dados da API
   */
  private async validateAgainstAPI(domMetrics: ValidationResult['metrics']): Promise<{
    errors: string[];
    warnings: string[];
  }> {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      const response = await fetch('/api/metrics');
      if (!response.ok) {
        errors.push(`API não acessível: ${response.status}`);
        return { errors, warnings };
      }

      const apiData = await response.json();
      if (!apiData.success || !apiData.data) {
        errors.push('API retornou dados inválidos');
        return { errors, warnings };
      }

      const apiMetrics = {
        novos: apiData.data.novos || 0,
        pendentes: apiData.data.pendentes || 0,
        progresso: apiData.data.progresso || 0,
        resolvidos: apiData.data.resolvidos || 0,
      };

      // Comparar cada métrica
      for (const [key, domValue] of Object.entries(domMetrics)) {
        const apiValue = apiMetrics[key as keyof typeof apiMetrics];
        const difference = Math.abs(domValue - apiValue);

        if (difference > this.config.toleranceThreshold) {
          errors.push(
            `Inconsistência em ${key}: DOM=${domValue}, API=${apiValue} (diferença: ${difference})`
          );
        }
      }

      console.log('🔄 Comparação API vs DOM:', {
        api: apiMetrics,
        dom: domMetrics,
      });
    } catch (error) {
      errors.push(`Erro ao validar contra API: ${error}`);
    }

    return { errors, warnings };
  }

  /**
   * Captura screenshot do dashboard para evidência
   */
  private async captureScreenshot(): Promise<string> {
    try {
      // Usar html2canvas se disponível
      if (typeof (window as any).html2canvas !== 'undefined') {
        const canvas = await (window as any).html2canvas(document.body);
        return canvas.toDataURL('image/png');
      }

      // Fallback: usar Canvas API nativo
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('Canvas context não disponível');

      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      // Captura básica (limitada)
      ctx.fillStyle = '#f0f0f0';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#333';
      ctx.font = '16px Arial';
      ctx.fillText('Screenshot capturada em ' + new Date().toLocaleString(), 10, 30);

      return canvas.toDataURL('image/png');
    } catch (error) {
      console.warn('⚠️ Não foi possível capturar screenshot:', error);
      return '';
    }
  }

  /**
   * Valida consistência visual (layout, cores, etc.)
   */
  private async validateVisualConsistency(): Promise<{
    errors: string[];
    warnings: string[];
  }> {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      // Verificar se cards estão visíveis
      const cards = document.querySelectorAll(
        '[data-testid="metric-card"], .metric-card, [class*="card"]'
      );

      cards.forEach((card, index) => {
        const rect = card.getBoundingClientRect();

        // Verificar se o card está visível
        if (rect.width === 0 || rect.height === 0) {
          warnings.push(`Card ${index + 1}: Dimensões zero (possivelmente oculto)`);
        }

        // Verificar se está na viewport
        if (
          rect.top < 0 ||
          rect.left < 0 ||
          rect.bottom > window.innerHeight ||
          rect.right > window.innerWidth
        ) {
          warnings.push(`Card ${index + 1}: Fora da viewport`);
        }

        // Verificar estilos computados
        const styles = window.getComputedStyle(card);
        if (styles.display === 'none' || styles.visibility === 'hidden') {
          errors.push(`Card ${index + 1}: Oculto via CSS`);
        }
      });

      // Verificar se há elementos de erro visíveis
      const errorElements = document.querySelectorAll(
        '.error, [class*="error"], [data-testid="error"]'
      );
      if (errorElements.length > 0) {
        errors.push(`${errorElements.length} elemento(s) de erro encontrado(s) na página`);
      }
    } catch (error) {
      warnings.push(`Erro durante validação visual: ${error}`);
    }

    return { errors, warnings };
  }

  /**
   * Executa validação com retry automático
   */
  async validateWithRetry(): Promise<ValidationResult> {
    let lastResult: ValidationResult | null = null;

    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      console.log(`🔄 Tentativa ${attempt}/${this.config.retryAttempts} de validação visual`);

      lastResult = await this.validateDashboardRendering();

      if (lastResult.isValid) {
        console.log(`✅ Validação passou na tentativa ${attempt}`);
        return lastResult;
      }

      if (attempt < this.config.retryAttempts) {
        console.log(`⏳ Aguardando ${this.config.retryDelay}ms antes da próxima tentativa...`);
        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));
      }
    }

    console.error(`❌ Validação falhou após ${this.config.retryAttempts} tentativas`);
    return lastResult!;
  }

  /**
   * Configura o validador
   */
  configure(config: Partial<VisualValidationConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// Instância global do validador
export const visualValidator = new VisualValidator();

// Função utilitária para uso no console
(window as any).validateVisual = () => visualValidator.validateWithRetry();
(window as any).validateVisualQuick = () => visualValidator.validateDashboardRendering();

// Auto-execução em desenvolvimento (DESABILITADO TEMPORARIAMENTE)
// if (process.env.NODE_ENV === 'development') {
//   // Executar validação automática após carregamento
//   window.addEventListener('load', () => {
//     setTimeout(() => {
//       visualValidator.validateWithRetry().then(result => {
//         if (!result.isValid) {
//           console.error('🚨 VALIDAÇÃO VISUAL AUTOMÁTICA FALHOU:', result.errors);
//         }
//       });
//     }, 2000); // Aguardar 2s após load
//   });
// }

export default VisualValidator;
