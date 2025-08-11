// Script para testar diretamente a API e identificar onde está o problema

interface DirectAPITestResult {
  step: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: number;
  duration?: number;
}

class DirectAPITester {
  private results: DirectAPITestResult[] = [];

  async runDirectAPITest(): Promise<DirectAPITestResult[]> {
    console.log('🧪 TESTE DIRETO DA API DO RANKING');
    console.log('=' .repeat(50));
    
    this.results = [];
    
    // 1. Testar endpoint básico
    await this.testBasicEndpoint();
    
    // 2. Testar com diferentes URLs
    await this.testDifferentEndpoints();
    
    // 3. Testar resposta do backend Python
    await this.testBackendResponse();
    
    // 4. Verificar se o backend está rodando
    await this.testBackendHealth();
    
    // 5. Testar dados específicos
    await this.testDataStructure();
    
    this.generateDirectAPIReport();
    return this.results;
  }

  private async testBasicEndpoint() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando endpoint básico /api/technicians/ranking...');
      
      const response = await fetch('http://localhost:5000/api/technicians/ranking');
      const duration = Date.now() - startTime;
      
      console.log('📡 Status da resposta:', response.status);
      console.log('📡 Headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      this.results.push({
        step: 'basic_endpoint_direct',
        success: true,
        data: {
          status: response.status,
          headers: Object.fromEntries(response.headers.entries()),
          responseData: data,
          dataLength: data?.data?.length || 0,
          hasData: !!(data?.data && data.data.length > 0),
          structure: data?.success ? 'valid' : 'invalid'
        },
        timestamp: Date.now(),
        duration
      });
      
      console.log('✅ Endpoint básico OK:', {
        status: response.status,
        success: data?.success,
        dataItems: data?.data?.length || 0,
        duration: `${duration}ms`,
        sampleData: data?.data?.[0]
      });
      
    } catch (error) {
      this.results.push({
        step: 'basic_endpoint_direct',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.error('❌ Erro no endpoint básico:', error);
    }
  }

  private async testDifferentEndpoints() {
    const endpoints = [
      { url: 'http://localhost:5000/api/technicians/ranking', name: 'ranking_completo' },
      { url: 'http://localhost:5000/api/technicians/ranking?limit=5', name: 'ranking_limitado' },
      { url: 'http://localhost:5000/api/technicians', name: 'tecnicos_base' },
      { url: 'http://localhost:5000/api/dashboard/metrics', name: 'metricas_dashboard' }
    ];
    
    for (const endpoint of endpoints) {
      const startTime = Date.now();
      
      try {
        console.log(`🔍 Testando ${endpoint.name}: ${endpoint.url}`);
        
        const response = await fetch(endpoint.url);
        const duration = Date.now() - startTime;
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        this.results.push({
          step: endpoint.name,
          success: true,
          data: {
            url: endpoint.url,
            status: response.status,
            dataLength: data?.data?.length || 0,
            hasData: !!(data?.data && data.data.length > 0),
            responseStructure: {
              hasSuccess: 'success' in data,
              hasData: 'data' in data,
              hasMessage: 'message' in data
            }
          },
          timestamp: Date.now(),
          duration
        });
        
        console.log(`✅ ${endpoint.name} OK:`, {
          status: response.status,
          dataItems: data?.data?.length || 0,
          duration: `${duration}ms`
        });
        
      } catch (error) {
        this.results.push({
          step: endpoint.name,
          success: false,
          error: error instanceof Error ? error.message : 'Erro desconhecido',
          timestamp: Date.now(),
          duration: Date.now() - startTime
        });
        
        console.error(`❌ Erro em ${endpoint.name}:`, error);
      }
    }
  }

  private async testBackendResponse() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando resposta detalhada do backend...');
      
      const response = await fetch('http://localhost:5000/api/technicians/ranking', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      const duration = Date.now() - startTime;
      const responseText = await response.text();
      
      console.log('📡 Resposta bruta do backend:', responseText);
      
      let parsedData;
      try {
        parsedData = JSON.parse(responseText);
      } catch (parseError) {
        throw new Error(`Erro ao fazer parse da resposta: ${parseError}`);
      }
      
      this.results.push({
        step: 'backend_response_detailed',
        success: true,
        data: {
          status: response.status,
          rawResponse: responseText,
          parsedData: parsedData,
          responseSize: responseText.length,
          contentType: response.headers.get('content-type')
        },
        timestamp: Date.now(),
        duration
      });
      
      console.log('✅ Resposta do backend analisada:', {
        status: response.status,
        contentType: response.headers.get('content-type'),
        responseSize: `${responseText.length} chars`,
        hasValidJSON: !!parsedData,
        duration: `${duration}ms`
      });
      
    } catch (error) {
      this.results.push({
        step: 'backend_response_detailed',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.error('❌ Erro na resposta do backend:', error);
    }
  }

  private async testBackendHealth() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando saúde do backend...');
      
      // Testar endpoint de health se existir
      const healthResponse = await fetch('http://localhost:5000/api/health', {
        method: 'GET'
      });
      
      const duration = Date.now() - startTime;
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        
        this.results.push({
          step: 'backend_health',
          success: true,
          data: {
            status: healthResponse.status,
            healthData: healthData
          },
          timestamp: Date.now(),
          duration
        });
        
        console.log('✅ Backend health OK:', healthData);
      } else {
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }
      
    } catch (error) {
      // Se não há endpoint de health, testar conectividade básica
      try {
        const basicResponse = await fetch('http://localhost:5000/', {
          method: 'GET'
        });
        
        this.results.push({
          step: 'backend_health',
          success: basicResponse.ok,
          data: {
            status: basicResponse.status,
            message: 'Backend respondendo na porta 5000'
          },
          timestamp: Date.now(),
          duration: Date.now() - startTime
        });
        
        console.log('✅ Backend básico respondendo:', basicResponse.status);
        
      } catch (basicError) {
        this.results.push({
          step: 'backend_health',
          success: false,
          error: `Backend não está respondendo: ${basicError}`,
          timestamp: Date.now(),
          duration: Date.now() - startTime
        });
        
        console.error('❌ Backend não está respondendo:', basicError);
      }
    }
  }

  private async testDataStructure() {
    const startTime = Date.now();
    
    try {
      console.log('🔍 Testando estrutura dos dados...');
      
      const response = await fetch('http://localhost:5000/api/technicians/ranking?limit=1');
      const data = await response.json();
      
      if (!data?.data || !Array.isArray(data.data) || data.data.length === 0) {
        throw new Error('Resposta não contém dados válidos');
      }
      
      const technician = data.data[0];
      const expectedFields = {
        id: 'number',
        nome: 'string', // Campo do backend
        nivel: 'string', // Campo do backend
        total: 'number'
      };
      
      const validation: any = {};
      
      for (const [field, expectedType] of Object.entries(expectedFields)) {
        const actualType = typeof technician[field];
        validation[field] = {
          present: field in technician,
          expectedType,
          actualType,
          valid: actualType === expectedType || (field === 'id' && actualType === 'string') // ID pode ser string
        };
      }
      
      const allValid = Object.values(validation).every((v: any) => v.valid);
      
      this.results.push({
        step: 'data_structure_validation',
        success: allValid,
        data: {
          validation,
          sampleTechnician: technician,
          allFieldsPresent: Object.values(validation).every((v: any) => v.present),
          allTypesCorrect: allValid
        },
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.log('✅ Validação de estrutura:', {
        allValid,
        validation,
        sampleData: technician
      });
      
    } catch (error) {
      this.results.push({
        step: 'data_structure_validation',
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
      
      console.error('❌ Erro na validação de estrutura:', error);
    }
  }

  private generateDirectAPIReport() {
    console.log('\n📊 RELATÓRIO DO TESTE DIRETO DA API');
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
    
    // Diagnóstico específico
    console.log('\n🔍 DIAGNÓSTICO ESPECÍFICO:');
    
    const basicEndpointResult = this.results.find(r => r.step === 'basic_endpoint_direct');
    const backendHealthResult = this.results.find(r => r.step === 'backend_health');
    const dataStructureResult = this.results.find(r => r.step === 'data_structure_validation');
    
    if (!backendHealthResult?.success) {
      console.log('❌ PROBLEMA: Backend não está respondendo');
      console.log('💡 SOLUÇÃO: Verificar se o backend Python está rodando na porta 5000');
      console.log('💡 COMANDO: python app.py');
    } else if (!basicEndpointResult?.success) {
      console.log('❌ PROBLEMA: Endpoint do ranking não está funcionando');
      console.log('💡 SOLUÇÃO: Verificar implementação do endpoint /api/technicians/ranking no backend');
    } else if (basicEndpointResult?.success && basicEndpointResult?.data?.dataLength === 0) {
      console.log('⚠️ PROBLEMA: API responde mas não retorna dados');
      console.log('💡 SOLUÇÃO: Verificar se há dados de técnicos no banco de dados');
      console.log('💡 SOLUÇÃO: Verificar filtros de data ou configuração do backend');
    } else if (!dataStructureResult?.success) {
      console.log('⚠️ PROBLEMA: Estrutura dos dados está incorreta');
      console.log('💡 SOLUÇÃO: Verificar mapeamento de campos no backend (nome/nome, nivel/level)');
    } else {
      console.log('✅ API está funcionando corretamente');
      console.log('💡 O problema pode estar no frontend (cache, renderização, estado)');
      console.log('💡 Verificar console do navegador para erros de React');
    }
    
    // Mostrar dados de exemplo se disponíveis
    const sampleData = basicEndpointResult?.data?.responseData?.data?.[0];
    if (sampleData) {
      console.log('\n📋 DADOS DE EXEMPLO DO BACKEND:');
      console.log(JSON.stringify(sampleData, null, 2));
    }
  }

  getResults(): DirectAPITestResult[] {
    return this.results;
  }

  clearResults() {
    this.results = [];
  }
}

// Instância global
const directAPITester = new DirectAPITester();

// Expor no window para uso no console
if (typeof window !== 'undefined') {
  (window as any).directAPITester = directAPITester;
  (window as any).testDirectAPI = () => directAPITester.runDirectAPITest();
  (window as any).directAPITest = () => directAPITester.runDirectAPITest();
}

export { DirectAPITester, directAPITester };
export default directAPITester;