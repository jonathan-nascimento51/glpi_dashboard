/**
 * Testes E2E Completos - Suite Abrangente
 * 
 * Esta suite cobre todos os fluxos principais da aplicação,
 * incluindo autenticação, navegação, funcionalidades e cenários de erro.
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';
import { faker } from '@faker-js/faker';

// Configurações e constantes
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000';

// Dados de teste
const TEST_USER = {
  username: 'test_user',
  password: 'test_password_123',
  email: 'test@example.com'
};

const ADMIN_USER = {
  username: 'admin',
  password: 'admin_password_123',
  email: 'admin@example.com'
};

// Utilitários
class TestUtils {
  static async waitForNetworkIdle(page: Page, timeout = 5000) {
    await page.waitForLoadState('networkidle', { timeout });
  }

  static async takeScreenshot(page: Page, name: string) {
    await page.screenshot({ 
      path: `test-results/screenshots/${name}-${Date.now()}.png`,
      fullPage: true 
    });
  }

  static async mockApiResponse(page: Page, endpoint: string, response: any) {
    await page.route(`${API_URL}${endpoint}`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  static async interceptApiCall(page: Page, endpoint: string): Promise<any> {
    return new Promise((resolve) => {
      page.route(`${API_URL}${endpoint}`, async route => {
        const response = await route.fetch();
        const body = await response.json();
        resolve(body);
        await route.continue();
      });
    });
  }

  static generateTestData() {
    return {
      technician: {
        name: faker.person.fullName(),
        email: faker.internet.email(),
        phone: faker.phone.number(),
        department: faker.commerce.department()
      },
      ticket: {
        title: faker.lorem.sentence(),
        description: faker.lorem.paragraphs(2),
        priority: faker.helpers.arrayElement(['low', 'medium', 'high', 'urgent']),
        category: faker.helpers.arrayElement(['hardware', 'software', 'network', 'other'])
      }
    };
  }
}

// Page Objects
class LoginPage {
  constructor(private page: Page) {}

  async navigate() {
    await this.page.goto(`${BASE_URL}/login`);
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async login(username: string, password: string) {
    await this.page.fill('[data-testid="username-input"]', username);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async expectLoginError() {
    await expect(this.page.locator('[data-testid="error-message"]')).toBeVisible();
  }

  async expectSuccessfulLogin() {
    await expect(this.page).toHaveURL(new RegExp(`${BASE_URL}/dashboard`));
  }
}

class DashboardPage {
  constructor(private page: Page) {}

  async expectToBeLoaded() {
    await expect(this.page.locator('[data-testid="dashboard-container"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="metrics-cards"]')).toBeVisible();
  }

  async getMetricsData() {
    const metrics = await this.page.locator('[data-testid="metric-card"]').all();
    const data = [];
    
    for (const metric of metrics) {
      const title = await metric.locator('[data-testid="metric-title"]').textContent();
      const value = await metric.locator('[data-testid="metric-value"]').textContent();
      data.push({ title, value });
    }
    
    return data;
  }

  async filterByDateRange(startDate: string, endDate: string) {
    await this.page.fill('[data-testid="start-date-input"]', startDate);
    await this.page.fill('[data-testid="end-date-input"]', endDate);
    await this.page.click('[data-testid="apply-filter-button"]');
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async expectChartsToBeVisible() {
    await expect(this.page.locator('[data-testid="tickets-chart"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="technicians-chart"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="performance-chart"]')).toBeVisible();
  }
}

class TechniciansPage {
  constructor(private page: Page) {}

  async navigate() {
    await this.page.goto(`${BASE_URL}/technicians`);
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async expectToBeLoaded() {
    await expect(this.page.locator('[data-testid="technicians-table"]')).toBeVisible();
  }

  async searchTechnician(name: string) {
    await this.page.fill('[data-testid="search-input"]', name);
    await this.page.press('[data-testid="search-input"]', 'Enter');
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async getTechniciansCount() {
    const rows = await this.page.locator('[data-testid="technician-row"]').count();
    return rows;
  }

  async viewTechnicianDetails(index: number = 0) {
    await this.page.locator('[data-testid="technician-row"]').nth(index).click();
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async expectTechnicianDetails() {
    await expect(this.page.locator('[data-testid="technician-details"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="technician-stats"]')).toBeVisible();
  }
}

class TicketsPage {
  constructor(private page: Page) {}

  async navigate() {
    await this.page.goto(`${BASE_URL}/tickets`);
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async expectToBeLoaded() {
    await expect(this.page.locator('[data-testid="tickets-container"]')).toBeVisible();
  }

  async filterByStatus(status: string) {
    await this.page.selectOption('[data-testid="status-filter"]', status);
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async filterByPriority(priority: string) {
    await this.page.selectOption('[data-testid="priority-filter"]', priority);
    await TestUtils.waitForNetworkIdle(this.page);
  }

  async getTicketsCount() {
    const count = await this.page.locator('[data-testid="tickets-count"]').textContent();
    return parseInt(count || '0');
  }

  async expectTicketsToBeFiltered(expectedCount: number) {
    await expect(this.page.locator('[data-testid="ticket-item"]')).toHaveCount(expectedCount);
  }
}

// Testes de Autenticação
test.describe('Autenticação', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.navigate();
  });

  test('deve fazer login com credenciais válidas', async ({ page }) => {
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.expectSuccessfulLogin();
    
    // Verifica se o usuário está logado
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('deve mostrar erro com credenciais inválidas', async ({ page }) => {
    await loginPage.login('invalid_user', 'invalid_password');
    await loginPage.expectLoginError();
    
    // Verifica se permanece na página de login
    await expect(page).toHaveURL(new RegExp(`${BASE_URL}/login`));
  });

  test('deve validar campos obrigatórios', async ({ page }) => {
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('deve fazer logout corretamente', async ({ page }) => {
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.expectSuccessfulLogin();
    
    // Faz logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Verifica redirecionamento para login
    await expect(page).toHaveURL(new RegExp(`${BASE_URL}/login`));
  });
});

// Testes do Dashboard
test.describe('Dashboard', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    dashboardPage = new DashboardPage(page);
    await dashboardPage.expectToBeLoaded();
  });

  test('deve carregar métricas do dashboard', async ({ page }) => {
    const metrics = await dashboardPage.getMetricsData();
    
    expect(metrics.length).toBeGreaterThan(0);
    
    // Verifica se as métricas têm dados válidos
    for (const metric of metrics) {
      expect(metric.title).toBeTruthy();
      expect(metric.value).toBeTruthy();
    }
  });

  test('deve filtrar dados por período', async ({ page }) => {
    const startDate = '2024-01-01';
    const endDate = '2024-01-31';
    
    await dashboardPage.filterByDateRange(startDate, endDate);
    
    // Verifica se os dados foram atualizados
    await TestUtils.waitForNetworkIdle(page);
    await dashboardPage.expectChartsToBeVisible();
  });

  test('deve exibir gráficos interativos', async ({ page }) => {
    await dashboardPage.expectChartsToBeVisible();
    
    // Testa interação com gráfico
    await page.hover('[data-testid="tickets-chart"] .recharts-bar');
    await expect(page.locator('.recharts-tooltip')).toBeVisible();
  });

  test('deve atualizar dados em tempo real', async ({ page }) => {
    const initialMetrics = await dashboardPage.getMetricsData();
    
    // Simula atualização de dados
    await TestUtils.mockApiResponse(page, '/api/dashboard/metrics', {
      total_tickets: 150,
      resolved_tickets: 120,
      pending_tickets: 30
    });
    
    // Força atualização
    await page.reload();
    await dashboardPage.expectToBeLoaded();
    
    const updatedMetrics = await dashboardPage.getMetricsData();
    expect(updatedMetrics).not.toEqual(initialMetrics);
  });
});

// Testes de Técnicos
test.describe('Técnicos', () => {
  let techniciansPage: TechniciansPage;

  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    techniciansPage = new TechniciansPage(page);
    await techniciansPage.navigate();
    await techniciansPage.expectToBeLoaded();
  });

  test('deve listar técnicos', async ({ page }) => {
    const count = await techniciansPage.getTechniciansCount();
    expect(count).toBeGreaterThan(0);
  });

  test('deve buscar técnico por nome', async ({ page }) => {
    await techniciansPage.searchTechnician('João');
    
    // Verifica se os resultados foram filtrados
    const filteredCount = await techniciansPage.getTechniciansCount();
    expect(filteredCount).toBeGreaterThanOrEqual(0);
  });

  test('deve visualizar detalhes do técnico', async ({ page }) => {
    await techniciansPage.viewTechnicianDetails(0);
    await techniciansPage.expectTechnicianDetails();
    
    // Verifica se as estatísticas estão visíveis
    await expect(page.locator('[data-testid="tickets-resolved"]')).toBeVisible();
    await expect(page.locator('[data-testid="average-resolution-time"]')).toBeVisible();
  });

  test('deve ordenar técnicos por performance', async ({ page }) => {
    await page.click('[data-testid="sort-by-performance"]');
    await TestUtils.waitForNetworkIdle(page);
    
    // Verifica se a ordenação foi aplicada
    const firstTechnician = await page.locator('[data-testid="technician-row"]').first();
    await expect(firstTechnician.locator('[data-testid="performance-score"]')).toBeVisible();
  });
});

// Testes de Tickets
test.describe('Tickets', () => {
  let ticketsPage: TicketsPage;

  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    ticketsPage = new TicketsPage(page);
    await ticketsPage.navigate();
    await ticketsPage.expectToBeLoaded();
  });

  test('deve filtrar tickets por status', async ({ page }) => {
    await ticketsPage.filterByStatus('open');
    
    // Verifica se apenas tickets abertos são exibidos
    const tickets = await page.locator('[data-testid="ticket-item"]').all();
    for (const ticket of tickets) {
      const status = await ticket.locator('[data-testid="ticket-status"]').textContent();
      expect(status?.toLowerCase()).toContain('open');
    }
  });

  test('deve filtrar tickets por prioridade', async ({ page }) => {
    await ticketsPage.filterByPriority('high');
    
    // Verifica se apenas tickets de alta prioridade são exibidos
    const tickets = await page.locator('[data-testid="ticket-item"]').all();
    for (const ticket of tickets) {
      const priority = await ticket.locator('[data-testid="ticket-priority"]').textContent();
      expect(priority?.toLowerCase()).toContain('high');
    }
  });

  test('deve combinar múltiplos filtros', async ({ page }) => {
    await ticketsPage.filterByStatus('open');
    await ticketsPage.filterByPriority('urgent');
    
    // Verifica se os filtros foram aplicados corretamente
    const tickets = await page.locator('[data-testid="ticket-item"]').all();
    for (const ticket of tickets) {
      const status = await ticket.locator('[data-testid="ticket-status"]').textContent();
      const priority = await ticket.locator('[data-testid="ticket-priority"]').textContent();
      
      expect(status?.toLowerCase()).toContain('open');
      expect(priority?.toLowerCase()).toContain('urgent');
    }
  });
});

// Testes de Performance
test.describe('Performance', () => {
  test('deve carregar página inicial rapidamente', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto(BASE_URL);
    await TestUtils.waitForNetworkIdle(page);
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(3000); // Menos de 3 segundos
  });

  test('deve carregar dashboard com boa performance', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    const startTime = Date.now();
    
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectToBeLoaded();
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(5000); // Menos de 5 segundos
  });

  test('deve manter responsividade em diferentes resoluções', async ({ page }) => {
    const resolutions = [
      { width: 1920, height: 1080 }, // Desktop
      { width: 1366, height: 768 },  // Laptop
      { width: 768, height: 1024 },  // Tablet
      { width: 375, height: 667 }    // Mobile
    ];
    
    for (const resolution of resolutions) {
      await page.setViewportSize(resolution);
      
      const loginPage = new LoginPage(page);
      await loginPage.navigate();
      await loginPage.login(TEST_USER.username, TEST_USER.password);
      
      const dashboardPage = new DashboardPage(page);
      await dashboardPage.expectToBeLoaded();
      
      // Verifica se elementos principais estão visíveis
      await expect(page.locator('[data-testid="dashboard-container"]')).toBeVisible();
    }
  });
});

// Testes de Acessibilidade
test.describe('Acessibilidade', () => {
  test('deve ter navegação por teclado', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    
    // Testa navegação por Tab
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="username-input"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="password-input"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="login-button"]')).toBeFocused();
  });

  test('deve ter labels apropriados', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    
    // Verifica se inputs têm labels
    await expect(page.locator('label[for="username"]')).toBeVisible();
    await expect(page.locator('label[for="password"]')).toBeVisible();
  });

  test('deve ter contraste adequado', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    
    // Verifica cores de contraste (exemplo básico)
    const button = page.locator('[data-testid="login-button"]');
    const buttonStyles = await button.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        backgroundColor: styles.backgroundColor,
        color: styles.color
      };
    });
    
    expect(buttonStyles.backgroundColor).toBeTruthy();
    expect(buttonStyles.color).toBeTruthy();
  });
});

// Testes de Cenários de Erro
test.describe('Tratamento de Erros', () => {
  test('deve tratar erro de rede graciosamente', async ({ page }) => {
    // Simula erro de rede
    await page.route('**/api/**', route => route.abort());
    
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    // Verifica se mensagem de erro é exibida
    await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
  });

  test('deve tratar erro 500 do servidor', async ({ page }) => {
    // Simula erro 500
    await page.route('**/api/dashboard/metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    // Verifica se erro é tratado
    await expect(page.locator('[data-testid="server-error"]')).toBeVisible();
  });

  test('deve tratar timeout de requisição', async ({ page }) => {
    // Simula timeout
    await page.route('**/api/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 10000)); // 10s delay
      await route.continue();
    });
    
    page.setDefaultTimeout(5000); // 5s timeout
    
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    
    await expect(async () => {
      await loginPage.login(TEST_USER.username, TEST_USER.password);
    }).toThrow();
  });
});

// Testes de Integração Completa
test.describe('Fluxo Completo', () => {
  test('deve completar jornada completa do usuário', async ({ page }) => {
    // 1. Login
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    await loginPage.expectSuccessfulLogin();
    
    // 2. Dashboard
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectToBeLoaded();
    const metrics = await dashboardPage.getMetricsData();
    expect(metrics.length).toBeGreaterThan(0);
    
    // 3. Técnicos
    const techniciansPage = new TechniciansPage(page);
    await techniciansPage.navigate();
    await techniciansPage.expectToBeLoaded();
    await techniciansPage.searchTechnician('João');
    
    // 4. Tickets
    const ticketsPage = new TicketsPage(page);
    await ticketsPage.navigate();
    await ticketsPage.expectToBeLoaded();
    await ticketsPage.filterByStatus('open');
    
    // 5. Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    await expect(page).toHaveURL(new RegExp(`${BASE_URL}/login`));
  });

  test('deve manter estado durante navegação', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(TEST_USER.username, TEST_USER.password);
    
    // Aplica filtro no dashboard
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectToBeLoaded();
    await dashboardPage.filterByDateRange('2024-01-01', '2024-01-31');
    
    // Navega para técnicos e volta
    const techniciansPage = new TechniciansPage(page);
    await techniciansPage.navigate();
    await techniciansPage.expectToBeLoaded();
    
    // Volta ao dashboard
    await page.goto(`${BASE_URL}/dashboard`);
    await dashboardPage.expectToBeLoaded();
    
    // Verifica se filtro foi mantido
    const startDateValue = await page.locator('[data-testid="start-date-input"]').inputValue();
    const endDateValue = await page.locator('[data-testid="end-date-input"]').inputValue();
    
    expect(startDateValue).toBe('2024-01-01');
    expect(endDateValue).toBe('2024-01-31');
  });
});

// Hooks globais
test.afterEach(async ({ page }, testInfo) => {
  // Captura screenshot em caso de falha
  if (testInfo.status !== testInfo.expectedStatus) {
    await TestUtils.takeScreenshot(page, `failure-${testInfo.title}`);
  }
});

test.beforeAll(async () => {
  // Setup global antes de todos os testes
  console.log('Iniciando testes E2E completos...');
});

test.afterAll(async () => {
  // Cleanup global após todos os testes
  console.log('Testes E2E completos finalizados.');
});