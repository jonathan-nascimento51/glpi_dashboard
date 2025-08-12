/**
 * Teste E2E Anti-Zero Guard v2 - Integrado com Data Quality Service
 * 
 * Este teste valida:
 * 1. Endpoint /api/v1/health/data responde corretamente
 * 2. Detecção de dados all-zero via API
 * 3. Integração com dashboard visual
 * 4. Falha quando all-zero=true
 */

import { test, expect } from '@playwright/test';

interface DataHealthResponse {
  status: 'ok' | 'error';
  quality_level: string;
  all_zero: boolean;
  anomalies: boolean;
  issues_count: number;
  critical_issues: boolean;
  timestamp: string;
  metrics: any;
  issues: Array<{
    type: string;
    severity: string;
    message: string;
    field?: string;
  }>;
}

test.describe('Anti-Zero Guard v2 - Data Quality Integration', () => {
  const API_BASE = 'http://localhost:8000';
  const FRONTEND_BASE = 'http://localhost:3000';

  test.beforeEach(async ({ page }) => {
    // Configurar interceptação de requests para debug
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`API Request: ${request.method()} ${request.url()}`);
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/')) {
        console.log(`API Response: ${response.status()} ${response.url()}`);
      }
    });
  });

  test('deve validar endpoint /api/v1/health/data com dados normais', async ({ page }) => {
    // Testar endpoint de health diretamente
    const response = await page.request.get(`${API_BASE}/api/v1/health/data`);
    expect(response.status()).toBe(200);

    const healthData: DataHealthResponse = await response.json();
    
    // Validações básicas
    expect(healthData).toHaveProperty('status');
    expect(healthData).toHaveProperty('all_zero');
    expect(healthData).toHaveProperty('quality_level');
    expect(healthData).toHaveProperty('timestamp');
    
    console.log('Health Data:', JSON.stringify(healthData, null, 2));
    
    // Se não há dados all-zero, status deve ser ok
    if (!healthData.all_zero) {
      expect(healthData.status).toBe('ok');
    }
  });

  test('deve detectar dados all-zero via API', async ({ page }) => {
    // Primeiro verificar se há dados all-zero
    const healthResponse = await page.request.get(`${API_BASE}/api/v1/health/data`);
    const healthData: DataHealthResponse = await healthResponse.json();
    
    if (healthData.all_zero) {
      // Se detectou all-zero, deve ter issues críticos
      expect(healthData.status).toBe('error');
      expect(healthData.critical_issues).toBe(true);
      expect(healthData.issues_count).toBeGreaterThan(0);
      
      // Deve ter pelo menos um issue do tipo 'all_zero'
      const allZeroIssues = healthData.issues.filter(issue => issue.type === 'all_zero');
      expect(allZeroIssues.length).toBeGreaterThan(0);
      
      console.log('All-zero detected:', allZeroIssues);
    } else {
      console.log('No all-zero data detected - test passed');
    }
  });

  test('deve validar dashboard visual com dados reais', async ({ page }) => {
    // Navegar para o dashboard
    await page.goto(FRONTEND_BASE);
    
    // Aguardar carregamento
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Verificar se elementos principais estão presentes
    const dashboardTitle = page.locator('h1, h2, [data-testid="dashboard-title"]').first();
    await expect(dashboardTitle).toBeVisible({ timeout: 10000 });
    
    // Buscar cards de métricas
    const metricCards = page.locator('[data-testid*="metric"], .metric-card, .card').all();
    const cards = await metricCards;
    
    if (cards.length > 0) {
      console.log(`Found ${cards.length} metric cards`);
      
      // Verificar se pelo menos um card tem dados não-zero
      let hasNonZeroData = false;
      
      for (const card of cards) {
        const text = await card.textContent();
        if (text) {
          // Procurar por números maiores que 0
          const numbers = text.match(/\d+/g);
          if (numbers) {
            const hasPositiveNumber = numbers.some(num => parseInt(num) > 0);
            if (hasPositiveNumber) {
              hasNonZeroData = true;
              console.log(`Card with non-zero data: ${text.substring(0, 100)}`);
              break;
            }
          }
        }
      }
      
      // Verificar consistência com API health
      const healthResponse = await page.request.get(`${API_BASE}/api/v1/health/data`);
      const healthData: DataHealthResponse = await healthResponse.json();
      
      if (healthData.all_zero && hasNonZeroData) {
        throw new Error('Inconsistência: API reporta all-zero mas dashboard mostra dados não-zero');
      }
      
      if (!healthData.all_zero && !hasNonZeroData) {
        console.warn('Aviso: API reporta dados válidos mas dashboard mostra zeros');
      }
    }
    
    // Capturar screenshot para evidência
    await page.screenshot({ 
      path: '../artifacts/e2e/dashboard-data-quality-check.png',
      fullPage: true 
    });
  });

  test('deve falhar quando all-zero=true (comportamento esperado)', async ({ page }) => {
    // Verificar status de health
    const healthResponse = await page.request.get(`${API_BASE}/api/v1/health/data`);
    const healthData: DataHealthResponse = await healthResponse.json();
    
    // Se detectou all-zero, este teste deve "falhar" intencionalmente
    // para alertar sobre problemas de qualidade de dados
    if (healthData.all_zero) {
      console.error(' ALERTA: Dados all-zero detectados!');
      console.error('Issues encontrados:', healthData.issues);
      console.error('Qualidade dos dados:', healthData.quality_level);
      
      // Capturar evidência
      await page.goto(FRONTEND_BASE);
      await page.waitForLoadState('networkidle');
      await page.screenshot({ 
        path: '../artifacts/e2e/all-zero-alert.png',
        fullPage: true 
      });
      
      // Falhar o teste intencionalmente
      throw new Error(`Anti-Zero Guard ativado: ${healthData.issues_count} problemas detectados. Qualidade: ${healthData.quality_level}`);
    } else {
      console.log(' Nenhum problema all-zero detectado - dados saudáveis');
    }
  });

  test('deve validar métricas de qualidade', async ({ page }) => {
    const healthResponse = await page.request.get(`${API_BASE}/api/v1/health/data`);
    const healthData: DataHealthResponse = await healthResponse.json();
    
    // Validar estrutura das métricas
    expect(healthData.metrics).toBeDefined();
    expect(healthData.metrics).toHaveProperty('total_fields');
    expect(healthData.metrics).toHaveProperty('numeric_fields');
    expect(healthData.metrics).toHaveProperty('data_completeness');
    
    // Validar que completeness está entre 0 e 1
    expect(healthData.metrics.data_completeness).toBeGreaterThanOrEqual(0);
    expect(healthData.metrics.data_completeness).toBeLessThanOrEqual(1);
    
    // Log das métricas para análise
    console.log('Métricas de qualidade:', {
      total_fields: healthData.metrics.total_fields,
      numeric_fields: healthData.metrics.numeric_fields,
      completeness: healthData.metrics.data_completeness,
      issues: healthData.issues_count
    });
  });

  test('deve testar resiliência da API', async ({ page }) => {
    // Testar múltiplas chamadas para verificar consistência
    const responses = [];
    
    for (let i = 0; i < 3; i++) {
      const response = await page.request.get(`${API_BASE}/api/v1/health/data`);
      expect(response.status()).toBe(200);
      
      const data: DataHealthResponse = await response.json();
      responses.push(data);
      
      await page.waitForTimeout(1000); // Aguardar 1s entre requests
    }
    
    // Verificar consistência entre responses
    const firstResponse = responses[0];
    for (const response of responses.slice(1)) {
      expect(response.all_zero).toBe(firstResponse.all_zero);
      expect(response.status).toBe(firstResponse.status);
    }
    
    console.log('Teste de resiliência passou - API consistente');
  });
});
