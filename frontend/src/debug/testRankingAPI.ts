// Script para testar diretamente a API do ranking e identificar problemas

interface APITestResult {
  step: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: number;
  duration?: number;
}

class RankingAPITester {
  private results: APITestResult[] = [];

  async runFullAPITest(): Promise<APITestResult[]> {
    console.log('🧪 TESTE COMPLETO DA API DO RANKING');
    console.log('=' .repeat(50));
    
    this.results = [];
    
    // 1. Testar endpoint básico
    await this.testBasicEndpoint();
    
    // 2. Testar com diferentes parâmetros
    await this.testWithParameters();
    
    // 3. Testar headers e cache
    await this.testCacheHeaders();
    
    // 4. Testar resposta completa
    await this.testFullResponse();
    
    // 5. Comparar com dados esperados
    await this.validateResponseStructure();
    
    this.generateAPIReport();
    return this.results;
  }

  private async testBasicEndpoint() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando endpoint básico...');
      
      const response = await fetch('/api/technicians/ranking');
      const duration = Date.now() - startTime;
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      this.results.push({
        step: 'basic_endpoint',
        success: true,
        data: {
          status: response.status,
          dataLength: data?.data?.length || 0,
          hasData: !!(data?.data && data.data.length > 0),
          structure: data?.success ? 'valid' : 'invalid'
        },
        timestamp: Date.now(),
        duration
      });
      
      console.log('✅ Endpoint básico OK:', {
        status: response.status,
        dataItems: data?.data?.length || 0,
        duration: `${duration}ms`
      });
      
    } catch (error) {
      this.results.push({
        step: 'basic_endpoint',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.error('❌ Erro no endpoint básico:', error);
    }
  }

  private async testWithParameters() {
    const testCases = [
      { params: '?limit=5', name: 'com_limite' },
      { params: '?level=N1', name: 'filtro_nivel' },
      { params: '?startDate=2024-01-01&endDate=2024-12-31', name: 'filtro_data' },
      { params: '?limit=10&level=N2', name: 'multiplos_filtros' }
    ];
    
    for (const testCase of testCases) {
      const startTime = Date.now();
      
      try {
        console.log(`🔍 Testando ${testCase.name}...`);
        
        const response = await fetch(`/api/technicians/ranking${testCase.params}`);
        const duration = Date.now() - startTime;
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        this.results.push({
          step: testCase.name,
          success: true,
          data: {
            params: testCase.params,
            dataLength: data?.data?.length || 0,
            hasData: !!(data?.data && data.data.length > 0)
          },
          timestamp: Date.now(),
          duration
        });
        
        console.log(`✅ ${testCase.name} OK:`, {
          dataItems: data?.data?.length || 0,
          duration: `${duration}ms`
        });
        
      } catch (error) {
        this.results.push({
          step: testCase.name,
          success: false,
          error: error instanceof Error ? error.message : 'Erro desconhecido',
          timestamp: Date.now(),
          duration: Date.now() - startTime
        });
        
        console.error(`❌ Erro em ${testCase.name}:`, error);
      }
    }
  }

  private async testCacheHeaders() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando headers de cache...');
      
      const response = await fetch('/api/technicians/ranking', {
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      const duration = Date.now() - startTime;
      
      const headers = {
        etag: response.headers.get('etag'),
        cacheControl: response.headers.get('cache-control'),
        lastModified: response.headers.get('last-modified'),
        contentType: response.headers.get('content-type')
      };
      
      this.results.push({
        step: 'cache_headers',
        success: true,
        data: {
          status: response.status,
          headers
        },
        timestamp: Date.now(),
        duration
      });
      
      console.log('✅ Headers de cache:', headers);
      
    } catch (error) {
      this.results.push({
        step: 'cache_headers',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.error('❌ Erro nos headers:', error);
    }
  }

  private async testFullResponse() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando resposta completa...');
      
      const response = await fetch('/api/technicians/ranking?limit=3');
      const duration = Date.now() - startTime;
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Validar estrutura da resposta
      const isValidStructure = this.validateStructure(data);
      
      this.results.push({
        step: 'full_response',
        success: isValidStructure,
        data: {
          fullResponse: data,
          structure: isValidStructure ? 'valid' : 'invalid',
          sampleTechnician: data?.data?.[0]
        },
        timestamp: Date.now(),
        duration
      });
      
      console.log('✅ Resposta completa:', {
        success: data?.success,
        dataLength: data?.data?.length,
        structure: isValidStructure ? 'válida' : 'inválida',
        sampleData: data?.data?.[0]
      });
      
    } catch (error) {
      this.results.push({
        step: 'full_response',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.error('❌ Erro na resposta completa:', error);
    }
  }

  private validateStructure(data: any): boolean {
    // Verificar estrutura esperada da resposta
    if (!data || typeof data !== 'object') return false;
    if (!data.success || !Array.isArray(data.data)) return false;
    
    // Verificar estrutura de cada técnico
    if (data.data.length > 0) {
      const technician = data.data[0];
      const requiredFields = ['id', 'name', 'level', 'total', 'rank'];
      
      for (const field of requiredFields) {
        if (!(field in technician)) {
          console.warn(`Campo obrigatório ausente: ${field}`);
          return false;
        }
      }
    }
    
    return true;
  }

  private async validateResponseStructure() {
    try {
      console.log('🔍 Validando estrutura da resposta...');
      
      const response = await fetch('/api/technicians/ranking?limit=1');
      const data = await response.json();
      
      if (!data?.data || !Array.isArray(data.data) || data.data.length === 0) {
        throw new Error('Resposta não contém dados válidos');
      }
      
      const technician = data.data[0];
      const expectedFields = {
        id: 'number',
        name: 'string',
        level: 'string',
        total: 'number',
        rank: 'number',
        score: 'number'
      };
      
      const validation: any = {};
      
      for (const [field, expectedType] of Object.entries(expectedFields)) {
        const actualType = typeof technician[field];
        validation[field] = {
          present: field in technician,
          expectedType,
          actualType,
          valid: actualType === expectedType
        };
      }
      
      const allValid = Object.values(validation).every((v: any) => v.valid);
      
      this.results.push({
        step: 'structure_validation',
        success: allValid,
        data: {
          validation,
          sampleTechnician: technician
        },
        timestamp: Date.now()
      });
      
      console.log('✅ Validação de estrutura:', validation);
      
    } catch (error) {
      this.results.push({
        step: 'structure_validation',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now()
      });
      
      console.error('❌ Erro na validação:', error);
    }
  }

  private generateAPIReport() {
    console.log('\n📊 RELATÓRIO DO TESTE DA API');
    console.log('=' .repeat(50));
    
    const totalTests = this.results.length;
    const successfulTests = this.results.filter(r => r.success).length;
    const failedTests = totalTests - successfulTests;
    
    console.log(`📈 Total de testes: ${totalTests}`);
    console.log(`✅ Testes bem-sucedidos: ${successfulTests}`);
    console.log(`❌ Testes falharam: ${failedTests}`);
    
    if (failedTests > 0) {
      console.log('\n❌ TESTES QUE FALHARAM:');
      this.results.filter(r => !r.success).forEach(result => {
        console.log(`- ${result.step}: ${result.error}`);
      });
    }
    
    // Calcular tempo médio de resposta
    const responseTimes = this.results
      .filter(r => r.duration)
      .map(r => r.duration!);
    
    if (responseTimes.length > 0) {
      const avgTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      const maxTime = Math.max(...responseTimes);
      const minTime = Math.min(...responseTimes);
      
      console.log('\n⏱️ PERFORMANCE:');
      console.log(`- Tempo médio: ${avgTime.toFixed(2)}ms`);
      console.log(`- Tempo máximo: ${maxTime}ms`);
      console.log(`- Tempo mínimo: ${minTime}ms`);
    }
    
    // Diagnóstico específico
    console.log('\n🔍 DIAGNÓSTICO:');
    
    const basicEndpointResult = this.results.find(r => r.step === 'basic_endpoint');
    if (basicEndpointResult?.success) {
      const hasData = basicEndpointResult.data?.hasData;
      if (hasData) {
        console.log('✅ API está retornando dados corretamente');
        console.log('💡 O problema pode estar no frontend (cache, renderização, estado)');
      } else {
        console.log('⚠️ API responde mas não retorna dados');
        console.log('💡 Verificar filtros de data ou configuração do backend');
      }
    } else {
      console.log('❌ API não está respondendo corretamente');
      console.log('💡 Verificar se o backend está rodando e configurado');
    }
  }

  getResults(): APITestResult[] {
    return this.results;
  }

  clearResults() {
    this.results = [];
  }
}

// Instância global
const rankingAPITester = new RankingAPITester();

// Expor no window para uso no console
if (typeof window !== 'undefined') {
  (window as any).rankingAPITester = rankingAPITester;
  (window as any).testRankingAPI = () => rankingAPITester.runFullAPITest();
  (window as any).apiTest = () => rankingAPITester.runFullAPITest();
}

export { RankingAPITester, rankingAPITester };
export default rankingAPITester;