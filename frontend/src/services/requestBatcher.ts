/**
 * Sistema de batching de requisições para agrupar múltiplas chamadas
 * em uma única requisição, reduzindo a carga no servidor
 */

interface BatchRequest {
  id: string;
  endpoint: string;
  params: any;
  resolve: (data: any) => void;
  reject: (error: any) => void;
  timestamp: number;
}

interface BatchConfig {
  maxBatchSize: number;
  maxWaitTime: number;
  endpoints: string[];
}

class RequestBatcher {
  private pendingRequests = new Map<string, BatchRequest[]>();
  private batchTimers = new Map<string, NodeJS.Timeout>();
  private config: BatchConfig;

  constructor(config: Partial<BatchConfig> = {}) {
    this.config = {
      maxBatchSize: 10,
      maxWaitTime: 100, // 100ms
      endpoints: ['metrics', 'tickets', 'users'],
      ...config,
    };
  }

  /**
   * Adiciona uma requisição ao batch ou executa imediatamente se não for batchável
   */
  async batchRequest<T>(
    endpoint: string,
    params: any = {},
    fetchFn: (batchedParams: any[]) => Promise<T[]>
  ): Promise<T> {
    // Verificar se o endpoint suporta batching
    if (!this.config.endpoints.includes(endpoint)) {
      // Executar requisição individual
      const result = await fetchFn([params]);
      return result[0];
    }

    return new Promise<T>((resolve, reject) => {
      const requestId = this.generateRequestId();
      const batchKey = this.getBatchKey(endpoint);

      const request: BatchRequest = {
        id: requestId,
        endpoint,
        params,
        resolve,
        reject,
        timestamp: Date.now(),
      };

      // Adicionar à lista de requisições pendentes
      if (!this.pendingRequests.has(batchKey)) {
        this.pendingRequests.set(batchKey, []);
      }

      const requests = this.pendingRequests.get(batchKey)!;
      requests.push(request);

      console.log(
        `📦 Batcher: Adicionada requisição ${requestId} ao batch ${batchKey} (${requests.length}/${this.config.maxBatchSize})`
      );

      // Verificar se deve executar o batch imediatamente
      if (requests.length >= this.config.maxBatchSize) {
        this.executeBatch(batchKey, fetchFn);
      } else {
        // Configurar timer se não existir
        if (!this.batchTimers.has(batchKey)) {
          const timer = setTimeout(() => {
            this.executeBatch(batchKey, fetchFn);
          }, this.config.maxWaitTime);

          this.batchTimers.set(batchKey, timer);
        }
      }
    });
  }

  /**
   * Executa um batch de requisições
   */
  private async executeBatch<T>(
    batchKey: string,
    fetchFn: (batchedParams: any[]) => Promise<T[]>
  ): Promise<void> {
    const requests = this.pendingRequests.get(batchKey);
    if (!requests || requests.length === 0) {
      return;
    }

    // Limpar timer e requisições pendentes
    const timer = this.batchTimers.get(batchKey);
    if (timer) {
      clearTimeout(timer);
      this.batchTimers.delete(batchKey);
    }

    this.pendingRequests.delete(batchKey);

    console.log(`🚀 Batcher: Executando batch ${batchKey} com ${requests.length} requisições`);

    try {
      // Extrair parâmetros de todas as requisições
      const batchedParams = requests.map(req => req.params);

      // Executar requisição em batch
      const startTime = Date.now();
      const results = await fetchFn(batchedParams);
      const duration = Date.now() - startTime;

      console.log(`✅ Batcher: Batch ${batchKey} concluído em ${duration}ms`);

      // Resolver cada requisição individual com seu resultado correspondente
      requests.forEach((request, index) => {
        if (results[index] !== undefined) {
          request.resolve(results[index]);
        } else {
          request.reject(new Error(`Resultado não encontrado para índice ${index}`));
        }
      });
    } catch (error) {
      console.error(`❌ Batcher: Erro no batch ${batchKey}:`, error);

      // Rejeitar todas as requisições do batch
      requests.forEach(request => {
        request.reject(error);
      });
    }
  }

  /**
   * Gera uma chave única para agrupar requisições similares
   */
  private getBatchKey(endpoint: string): string {
    return `batch-${endpoint}`;
  }

  /**
   * Gera um ID único para cada requisição
   */
  private generateRequestId(): string {
    return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Força a execução de todos os batches pendentes
   */
  async flushAll(): Promise<void> {
    const batchKeys = Array.from(this.pendingRequests.keys());

    for (const batchKey of batchKeys) {
      // Para flush, precisamos de uma função fetch genérica
      // Isso será implementado quando integrarmos com o sistema de API
      console.log(`🔄 Batcher: Flushing batch ${batchKey}`);
    }
  }

  /**
   * Obtém estatísticas do batcher
   */
  getStats() {
    const totalPending = Array.from(this.pendingRequests.values()).reduce(
      (sum, requests) => sum + requests.length,
      0
    );

    const batchInfo = Array.from(this.pendingRequests.entries()).map(([key, requests]) => ({
      batchKey: key,
      pendingCount: requests.length,
      oldestRequest: Math.min(...requests.map(r => r.timestamp)),
    }));

    return {
      totalPendingRequests: totalPending,
      activeBatches: this.pendingRequests.size,
      activeTimers: this.batchTimers.size,
      batchDetails: batchInfo,
      config: this.config,
    };
  }

  /**
   * Limpa todos os batches pendentes
   */
  clear(): void {
    // Limpar timers
    for (const timer of this.batchTimers.values()) {
      clearTimeout(timer);
    }
    this.batchTimers.clear();

    // Rejeitar todas as requisições pendentes
    for (const requests of this.pendingRequests.values()) {
      requests.forEach(request => {
        request.reject(new Error('Batch cancelado'));
      });
    }
    this.pendingRequests.clear();

    console.log('🧹 Batcher: Todos os batches foram limpos');
  }
}

// Instância singleton do batcher
export const requestBatcher = new RequestBatcher({
  maxBatchSize: 5,
  maxWaitTime: 150, // 150ms para dar tempo de agrupar requisições
  endpoints: ['metrics', 'tickets', 'users', 'ranking'],
});

/**
 * Função auxiliar para criar requisições em batch para métricas
 */
export const batchMetricsRequest = async (params: any) => {
  return requestBatcher.batchRequest('metrics', params, async (batchedParams: any[]) => {
    // Implementar lógica de requisição em batch para métricas
    // Por enquanto, fazemos requisições individuais
    const results = [];
    for (const param of batchedParams) {
      try {
        const response = await fetch(`/api/metrics?${new URLSearchParams(param)}`);
        const data = await response.json();
        results.push(data);
      } catch (error) {
        results.push(null);
      }
    }
    return results;
  });
};

/**
 * Função auxiliar para criar requisições em batch para tickets
 */
export const batchTicketsRequest = async (params: any) => {
  return requestBatcher.batchRequest('tickets', params, async (batchedParams: any[]) => {
    // Implementar lógica de requisição em batch para tickets
    const results = [];
    for (const param of batchedParams) {
      try {
        const response = await fetch(`/api/tickets?${new URLSearchParams(param)}`);
        const data = await response.json();
        results.push(data);
      } catch (error) {
        results.push(null);
      }
    }
    return results;
  });
};

// Configurar limpeza automática em caso de erro
window.addEventListener('beforeunload', () => {
  requestBatcher.clear();
});
