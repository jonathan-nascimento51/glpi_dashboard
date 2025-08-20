/**
 * Sistema de validação automática para métricas do dashboard
 * Criado para garantir que as métricas estejam funcionando corretamente
 */

export interface MetricsValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  data?: any;
}

export class MetricsValidator {
  private static readonly API_BASE_URL = 'http://localhost:5000';

  /**
   * Valida se o endpoint /api/metrics está retornando dados válidos
   */
  static async validateMetricsEndpoint(): Promise<MetricsValidationResult> {
    const result: MetricsValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
    };

    try {
      console.log('🔍 MetricsValidator - Testando endpoint /api/metrics...');

      const response = await fetch(`${this.API_BASE_URL}/api/metrics`);

      if (!response.ok) {
        result.isValid = false;
        result.errors.push(`Endpoint retornou status ${response.status}: ${response.statusText}`);
        return result;
      }

      const data = await response.json();
      result.data = data;

      // Validar estrutura básica da resposta
      if (!data.success) {
        result.isValid = false;
        result.errors.push('Campo "success" não é true');
      }

      if (!data.data) {
        result.isValid = false;
        result.errors.push('Campo "data" não encontrado na resposta');
        return result;
      }

      const metricsData = data.data;

      // Validar métricas principais (totais gerais)
      const requiredMainMetrics = ['novos', 'pendentes', 'progresso', 'resolvidos'];
      for (const metric of requiredMainMetrics) {
        if (typeof metricsData[metric] !== 'number') {
          result.isValid = false;
          result.errors.push(`Métrica principal "${metric}" não é um número ou não existe`);
        } else if (metricsData[metric] < 0) {
          result.warnings.push(
            `Métrica principal "${metric}" tem valor negativo: ${metricsData[metric]}`
          );
        }
      }

      // Validar estrutura de níveis
      if (!metricsData.niveis) {
        result.isValid = false;
        result.errors.push('Campo "niveis" não encontrado nos dados');
      } else {
        const requiredLevels = ['n1', 'n2', 'n3', 'n4'];
        for (const level of requiredLevels) {
          if (!metricsData.niveis[level]) {
            result.isValid = false;
            result.errors.push(`Nível "${level}" não encontrado nos dados`);
          } else {
            // Validar métricas de cada nível
            for (const metric of requiredMainMetrics) {
              if (typeof metricsData.niveis[level][metric] !== 'number') {
                result.isValid = false;
                result.errors.push(`Métrica "${metric}" do nível "${level}" não é um número`);
              }
            }
          }
        }
      }

      // Validar tendências
      if (!metricsData.tendencias) {
        result.warnings.push('Campo "tendencias" não encontrado');
      } else {
        for (const metric of requiredMainMetrics) {
          if (!metricsData.tendencias[metric]) {
            result.warnings.push(`Tendência para "${metric}" não encontrada`);
          }
        }
      }

      // Validar timestamp
      if (!metricsData.timestamp) {
        result.warnings.push('Campo "timestamp" não encontrado');
      }

      console.log('✅ MetricsValidator - Validação concluída:', result);
      return result;
    } catch (error) {
      result.isValid = false;
      result.errors.push(
        `Erro ao conectar com a API: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
      );
      console.error('❌ MetricsValidator - Erro na validação:', error);
      return result;
    }
  }

  /**
   * Valida se os dados estão sendo processados corretamente no frontend
   */
  static validateFrontendDataProcessing(metrics: any): MetricsValidationResult {
    const result: MetricsValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
    };

    console.log('🔍 MetricsValidator - Validando processamento frontend:', metrics);

    if (!metrics) {
      result.isValid = false;
      result.errors.push('Objeto metrics é null ou undefined');
      return result;
    }

    // Validar se as métricas principais existem e são números
    const requiredMetrics = ['novos', 'pendentes', 'progresso', 'resolvidos'];
    for (const metric of requiredMetrics) {
      if (typeof metrics[metric] !== 'number') {
        result.isValid = false;
        result.errors.push(
          `Métrica "${metric}" não é um número: ${typeof metrics[metric]} = ${metrics[metric]}`
        );
      } else if (metrics[metric] === 0) {
        result.warnings.push(`Métrica "${metric}" tem valor zero`);
      }
    }

    console.log('✅ MetricsValidator - Validação frontend concluída:', result);
    return result;
  }

  /**
   * Executa validação completa do sistema de métricas
   */
  static async runCompleteValidation(): Promise<{
    api: MetricsValidationResult;
    frontend?: MetricsValidationResult;
  }> {
    console.log('🚀 MetricsValidator - Iniciando validação completa...');

    const apiValidation = await this.validateMetricsEndpoint();

    const results = {
      api: apiValidation,
      frontend: undefined as MetricsValidationResult | undefined,
    };

    // Se a API está funcionando, validar o processamento frontend
    if (apiValidation.isValid && apiValidation.data) {
      const frontendMetrics = {
        novos: apiValidation.data.data.novos,
        pendentes: apiValidation.data.data.pendentes,
        progresso: apiValidation.data.data.progresso,
        resolvidos: apiValidation.data.data.resolvidos,
      };
      results.frontend = this.validateFrontendDataProcessing(frontendMetrics);
    }

    console.log('🏁 MetricsValidator - Validação completa finalizada:', results);
    return results;
  }
}

// Função utilitária para executar validação no console do navegador
(window as any).validateMetrics = () => {
  MetricsValidator.runCompleteValidation().then(results => {
    console.log('📊 Resultados da Validação de Métricas:', results);

    if (results.api.isValid && results.frontend?.isValid) {
      console.log('✅ SUCESSO: Todas as validações passaram!');
    } else {
      console.log('❌ FALHA: Problemas encontrados nas validações');
      if (!results.api.isValid) {
        console.log('🔴 Problemas na API:', results.api.errors);
      }
      if (results.frontend && !results.frontend.isValid) {
        console.log('🔴 Problemas no Frontend:', results.frontend.errors);
      }
    }
  });
};

export default MetricsValidator;
