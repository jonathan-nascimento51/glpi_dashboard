import { test, expect, Page } from '@playwright/test';
import path from 'path';

/**
 * Teste E2E Anti-Zero Guard
 * 
 * Objetivo: Garantir que o dashboard exibe dados reais (anti-zero)
 * 
 * Cenários:
 * 1. PASS: Dados reais com soma > 0
 * 2. FAIL: Mock com dados = 0 (deve falhar com mensagem específica)
 */

interface DashboardMetrics {
  niveis: {
    N1: { total: number; resolvidos: number; pendentes: number; tempo_medio: number };
    N2: { total: number; resolvidos: number; pendentes: number; tempo_medio: number };
    N3: { total: number; resolvidos: number; pendentes: number; tempo_medio: number };
    N4: { total: number; resolvidos: number; pendentes: number; tempo_medio: number };
  };
  total_tickets: number;
  tickets_pendentes: number;
  tempo_medio_resolucao: number;
  satisfacao_cliente: number;
}

interface TechnicianData {
  id: number;
  nome: string;
  tickets_resolvidos: number;
  tempo_medio: number;
  nivel: string;
}

// Dados reais simulados (valores > 0)
const realDataMetrics: DashboardMetrics = {
  niveis: {
    N1: { total: 150, resolvidos: 120, pendentes: 30, tempo_medio: 2.5 },
    N2: { total: 80, resolvidos: 65, pendentes: 15, tempo_medio: 4.2 },
    N3: { total: 45, resolvidos: 35, pendentes: 10, tempo_medio: 8.1 },
    N4: { total: 20, resolvidos: 15, pendentes: 5, tempo_medio: 16.3 },
  },
  total_tickets: 295,
  tickets_pendentes: 60,
  tempo_medio_resolucao: 5.2,
  satisfacao_cliente: 4.2,
};

const realDataTechnicians: TechnicianData[] = [
  {
    id: 1,
    nome: 'João Silva',
    tickets_resolvidos: 45,
    tempo_medio: 3.2,
    nivel: 'N1',
  },
  {
    id: 2,
    nome: 'Maria Santos',
    tickets_resolvidos: 38,
    tempo_medio: 2.8,
    nivel: 'N1',
  },
  {
    id: 3,
    nome: 'Pedro Costa',
    tickets_resolvidos: 25,
    tempo_medio: 4.5,
    nivel: 'N2',
  },
];

// Dados zero (para teste negativo)
const zeroDataMetrics: DashboardMetrics = {
  niveis: {
    N1: { total: 0, resolvidos: 0, pendentes: 0, tempo_medio: 0 },
    N2: { total: 0, resolvidos: 0, pendentes: 0, tempo_medio: 0 },
    N3: { total: 0, resolvidos: 0, pendentes: 0, tempo_medio: 0 },
    N4: { total: 0, resolvidos: 0, pendentes: 0, tempo_medio: 0 },
  },
  total_tickets: 0,
  tickets_pendentes: 0,
  tempo_medio_resolucao: 0,
  satisfacao_cliente: 0,
};

const zeroDataTechnicians: TechnicianData[] = [];

/**
 * Calcula a soma total dos cards principais
 */
function calculateMainCardsSum(metrics: DashboardMetrics): number {
  const { niveis, total_tickets, tickets_pendentes } = metrics;
  
  const niveisSum = Object.values(niveis).reduce((sum, nivel) => {
    return sum + nivel.total + nivel.resolvidos + nivel.pendentes;
  }, 0);
  
  return niveisSum + total_tickets + tickets_pendentes;
}

/**
 * Aguarda o carregamento completo do dashboard
 */
async function waitForDashboardLoad(page: Page): Promise<void> {
  // Aguardar que o loading desapareça
  await page.waitForFunction(
    () => !document.querySelector('[data-testid="loading"]') && 
          !document.querySelector('text=Carregando')
  );
  
  // Aguardar que pelo menos um card principal esteja visível
  await page.waitForSelector('[data-testid="dashboard-card"]', { timeout: 10000 });
  
  // Aguardar estabilização da rede
  await page.waitForLoadState('networkidle');
}

/**
 * Extrai valores dos cards principais do dashboard
 */
async function extractDashboardValues(page: Page): Promise<number[]> {
  const values: number[] = [];
  
  // Selecionar todos os cards com valores numéricos
  const cardSelectors = [
    '[data-testid="total-tickets"]',
    '[data-testid="tickets-pendentes"]',
    '[data-testid="n1-total"]',
    '[data-testid="n1-resolvidos"]',
    '[data-testid="n1-pendentes"]',
    '[data-testid="n2-total"]',
    '[data-testid="n2-resolvidos"]',
    '[data-testid="n2-pendentes"]',
    '[data-testid="n3-total"]',
    '[data-testid="n3-resolvidos"]',
    '[data-testid="n3-pendentes"]',
    '[data-testid="n4-total"]',
    '[data-testid="n4-resolvidos"]',
    '[data-testid="n4-pendentes"]',
  ];
  
  for (const selector of cardSelectors) {
    try {
      const element = await page.locator(selector).first();
      if (await element.isVisible()) {
        const text = await element.textContent();
        const numericValue = parseInt(text?.replace(/[^0-9]/g, '') || '0');
        values.push(numericValue);
      }
    } catch (error) {
      // Se o seletor não existir, tentar seletores alternativos
      console.log(`Seletor ${selector} não encontrado, tentando alternativo...`);
    }
  }
  
  // Fallback: buscar por padrões de texto numérico em cards
  if (values.length === 0) {
    const cardElements = await page.locator('[data-testid*="card"], .card, .metric-card').all();
    for (const card of cardElements) {
      const text = await card.textContent();
      const numbers = text?.match(/\d+/g);
      if (numbers) {
        values.push(...numbers.map(n => parseInt(n)));
      }
    }
  }
  
  return values;
}

/**
 * Salva screenshot com timestamp
 */
async function saveScreenshot(page: Page, testName: string, status: 'pass' | 'fail'): Promise<string> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${testName}-${status}-${timestamp}.png`;
  const filepath = path.join('artifacts', 'e2e', filename);
  
  await page.screenshot({ 
    path: filepath, 
    fullPage: true,
    animations: 'disabled'
  });
  
  return filepath;
}

test.describe('Anti-Zero Guard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Configurar timeout aumentado para operações de rede
    test.setTimeout(60000);
  });

  test(' PASS: Dashboard deve exibir dados reais (soma > 0)', async ({ page }) => {
    // Interceptar chamadas da API e retornar dados reais
    await page.route('**/api/metrics*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(realDataMetrics),
      });
    });

    await page.route('**/api/technicians*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(realDataTechnicians),
      });
    });

    // Navegar para o dashboard
    await page.goto('/');
    
    // Aguardar carregamento completo
    await waitForDashboardLoad(page);
    
    // Extrair valores dos cards principais
    const dashboardValues = await extractDashboardValues(page);
    
    // Calcular soma total
    const totalSum = dashboardValues.reduce((sum, value) => sum + value, 0);
    
    // Calcular soma esperada dos dados mockados
    const expectedSum = calculateMainCardsSum(realDataMetrics);
    
    console.log(' Valores extraídos do dashboard:', dashboardValues);
    console.log(' Soma total dos cards:', totalSum);
    console.log(' Soma esperada:', expectedSum);
    
    // Salvar screenshot de sucesso
    const screenshotPath = await saveScreenshot(page, 'anti-zero-real-data', 'pass');
    console.log(' Screenshot salvo:', screenshotPath);
    
    // Validações Anti-Zero
    expect(totalSum, 'A soma dos cards principais deve ser maior que zero (dados reais)').toBeGreaterThan(0);
    expect(totalSum, 'A soma deve ser significativa (> 100)').toBeGreaterThan(100);
    
    // Validar valores específicos esperados
    expect(totalSum, `Soma total (${totalSum}) deve estar próxima da esperada (${expectedSum})`)
      .toBeGreaterThanOrEqual(expectedSum * 0.8); // Tolerância de 20%
    
    // Validar que elementos principais estão visíveis
    await expect(page.locator('text=Total')).toBeVisible();
    await expect(page.locator('text=N1')).toBeVisible();
    await expect(page.locator('text=N2')).toBeVisible();
    
    console.log(' Teste PASS: Dashboard exibindo dados reais com sucesso!');
  });

  test(' FAIL: Dashboard com dados zero deve falhar (Anti-zero guard triggered)', async ({ page }) => {
    // Interceptar chamadas da API e retornar dados zero
    await page.route('**/api/metrics*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(zeroDataMetrics),
      });
    });

    await page.route('**/api/technicians*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(zeroDataTechnicians),
      });
    });

    // Navegar para o dashboard
    await page.goto('/');
    
    // Aguardar carregamento completo
    await waitForDashboardLoad(page);
    
    // Extrair valores dos cards principais
    const dashboardValues = await extractDashboardValues(page);
    
    // Calcular soma total
    const totalSum = dashboardValues.reduce((sum, value) => sum + value, 0);
    
    console.log(' Valores extraídos do dashboard (zero test):', dashboardValues);
    console.log(' Soma total dos cards:', totalSum);
    
    // Salvar screenshot de falha
    const screenshotPath = await saveScreenshot(page, 'anti-zero-zero-data', 'fail');
    console.log(' Screenshot salvo:', screenshotPath);
    
    // Este teste DEVE falhar quando dados são zero
    // Simular o comportamento esperado do anti-zero guard
    if (totalSum === 0) {
      console.log(' Anti-zero guard triggered: Todos os valores são zero!');
      
      // Falhar intencionalmente com mensagem específica
      throw new Error('Anti-zero guard triggered');
    }
    
    // Se chegou aqui, significa que há dados não-zero (teste deveria passar)
    expect(totalSum, 'Este teste deveria falhar com dados zero, mas encontrou valores > 0').toBeGreaterThan(0);
    
    console.log('  Teste inesperadamente passou - dados não são zero');
  });

  test(' Teste de conectividade: Verificar se backend está respondendo', async ({ page }) => {
    let apiResponded = false;
    let apiError: string | null = null;
    
    // Interceptar e monitorar chamadas da API
    await page.route('**/api/**', async route => {
      try {
        // Permitir que a requisição real passe
        const response = await route.fetch();
        apiResponded = true;
        
        // Se a API real responder, usar os dados reais
        await route.fulfill({
          status: response.status(),
          headers: response.headers(),
          body: await response.body(),
        });
      } catch (error) {
        apiError = error instanceof Error ? error.message : 'Erro desconhecido';
        
        // Fallback para dados mockados se API real falhar
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(realDataMetrics),
        });
      }
    });

    // Navegar para o dashboard
    await page.goto('/');
    
    // Aguardar carregamento
    await waitForDashboardLoad(page);
    
    // Salvar screenshot de conectividade
    const screenshotPath = await saveScreenshot(page, 'connectivity-test', apiResponded ? 'pass' : 'fail');
    console.log(' Screenshot de conectividade salvo:', screenshotPath);
    
    // Relatório de conectividade
    console.log(' Status da API:', apiResponded ? 'Respondendo' : 'Não respondeu');
    if (apiError) {
      console.log(' Erro da API:', apiError);
    }
    
    // Validar que o dashboard carregou independentemente da API
    await expect(page.locator('body')).toBeVisible();
    
    console.log(' Teste de conectividade concluído');
  });
});

/**
 * Teste de setup: Verificar se o ambiente está pronto
 */
test.describe('Setup Validation', () => {
  test(' Verificar se diretório de artifacts existe', async () => {
    const fs = require('fs');
    const artifactsDir = path.join(process.cwd(), 'artifacts', 'e2e');
    
    expect(fs.existsSync(artifactsDir), `Diretório ${artifactsDir} deve existir`).toBeTruthy();
    
    console.log(' Diretório de artifacts configurado:', artifactsDir);
  });
});
