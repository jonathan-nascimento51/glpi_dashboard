import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navegar para a página do dashboard
    await page.goto('/');
    
    // Aguardar o carregamento da página
    await page.waitForLoadState('networkidle');
  });

  test('should display dashboard with metrics', async ({ page }) => {
    // Verificar se o título da página está correto
    await expect(page).toHaveTitle(/GLPI Dashboard/);
    
    // Verificar se os elementos principais estão visíveis
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="metrics-grid"]')).toBeVisible();
    
    // Verificar se as métricas principais estão sendo exibidas
    await expect(page.locator('[data-testid="total-tickets"]')).toBeVisible();
    await expect(page.locator('[data-testid="open-tickets"]')).toBeVisible();
    await expect(page.locator('[data-testid="closed-tickets"]')).toBeVisible();
    await expect(page.locator('[data-testid="pending-tickets"]')).toBeVisible();
  });

  test('should load and display charts', async ({ page }) => {
    // Aguardar o carregamento dos gráficos
    await page.waitForSelector('[data-testid="charts-container"]');
    
    // Verificar se os gráficos estão presentes
    await expect(page.locator('[data-testid="priority-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="status-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="trends-chart"]')).toBeVisible();
    
    // Verificar se os gráficos têm conteúdo (canvas)
    const priorityChart = page.locator('[data-testid="priority-chart"] canvas');
    await expect(priorityChart).toBeVisible();
    
    const statusChart = page.locator('[data-testid="status-chart"] canvas');
    await expect(statusChart).toBeVisible();
  });

  test('should filter data by date range', async ({ page }) => {
    // Abrir o seletor de data
    await page.click('[data-testid="date-filter-button"]');
    
    // Aguardar o calendário aparecer
    await page.waitForSelector('[data-testid="date-picker"]');
    
    // Selecionar uma data de início
    await page.click('[data-testid="start-date-input"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    
    // Selecionar uma data de fim
    await page.click('[data-testid="end-date-input"]');
    await page.fill('[data-testid="end-date-input"]', '2024-01-15');
    
    // Aplicar o filtro
    await page.click('[data-testid="apply-date-filter"]');
    
    // Aguardar o carregamento dos dados filtrados
    await page.waitForLoadState('networkidle');
    
    // Verificar se o indicador de filtro está ativo
    await expect(page.locator('[data-testid="active-filter-indicator"]')).toBeVisible();
    
    // Verificar se os dados foram atualizados
    await expect(page.locator('[data-testid="metrics-grid"]')).toBeVisible();
  });

  test('should refresh data manually', async ({ page }) => {
    // Aguardar o carregamento inicial
    await page.waitForSelector('[data-testid="metrics-grid"]');
    
    // Capturar o valor inicial de um métrica
    const initialValue = await page.locator('[data-testid="total-tickets"] .metric-value').textContent();
    
    // Clicar no botão de refresh
    await page.click('[data-testid="refresh-button"]');
    
    // Verificar se o indicador de carregamento aparece
    await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();
    
    // Aguardar o carregamento terminar
    await page.waitForLoadState('networkidle');
    
    // Verificar se o indicador de carregamento desaparece
    await expect(page.locator('[data-testid="loading-indicator"]')).not.toBeVisible();
    
    // Verificar se os dados ainda estão presentes
    await expect(page.locator('[data-testid="total-tickets"] .metric-value')).toBeVisible();
  });

  test('should toggle between chart types', async ({ page }) => {
    // Aguardar o carregamento dos gráficos
    await page.waitForSelector('[data-testid="charts-container"]');
    
    // Verificar se o toggle de tipo de gráfico está presente
    await expect(page.locator('[data-testid="chart-type-toggle"]')).toBeVisible();
    
    // Clicar para alternar o tipo de gráfico
    await page.click('[data-testid="chart-type-toggle"]');
    
    // Aguardar a animação/transição
    await page.waitForTimeout(500);
    
    // Verificar se o gráfico ainda está visível após a mudança
    await expect(page.locator('[data-testid="priority-chart"] canvas')).toBeVisible();
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Interceptar requisições da API para simular erro
    await page.route('**/api/dashboard/metrics', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    // Recarregar a página para acionar o erro
    await page.reload();
    
    // Aguardar o estado de erro aparecer
    await page.waitForSelector('[data-testid="error-message"]');
    
    // Verificar se a mensagem de erro está visível
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Erro ao carregar');
    
    // Verificar se o botão de retry está presente
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('should export data', async ({ page }) => {
    // Aguardar o carregamento da página
    await page.waitForSelector('[data-testid="metrics-grid"]');
    
    // Clicar no botão de exportar
    await page.click('[data-testid="export-button"]');
    
    // Aguardar o menu de exportação aparecer
    await page.waitForSelector('[data-testid="export-menu"]');
    
    // Verificar se as opções de exportação estão disponíveis
    await expect(page.locator('[data-testid="export-csv"]')).toBeVisible();
    await expect(page.locator('[data-testid="export-json"]')).toBeVisible();
    
    // Configurar o listener para download
    const downloadPromise = page.waitForEvent('download');
    
    // Clicar na opção de exportar CSV
    await page.click('[data-testid="export-csv"]');
    
    // Aguardar o download
    const download = await downloadPromise;
    
    // Verificar se o arquivo foi baixado
    expect(download.suggestedFilename()).toContain('.csv');
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Definir viewport para mobile
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Aguardar o carregamento
    await page.waitForSelector('[data-testid="dashboard-title"]');
    
    // Verificar se o layout mobile está ativo
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();
    
    // Verificar se as métricas estão empilhadas verticalmente
    const metricsGrid = page.locator('[data-testid="metrics-grid"]');
    await expect(metricsGrid).toHaveClass(/mobile-layout/);
    
    // Verificar se os gráficos são responsivos
    await expect(page.locator('[data-testid="charts-container"]')).toBeVisible();
    
    // Testar o menu mobile
    await page.click('[data-testid="mobile-menu-button"]');
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
  });

  test('should persist filter preferences', async ({ page }) => {
    // Aplicar um filtro de data
    await page.click('[data-testid="date-filter-button"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-01-15');
    await page.click('[data-testid="apply-date-filter"]');
    
    // Aguardar o filtro ser aplicado
    await page.waitForLoadState('networkidle');
    
    // Recarregar a página
    await page.reload();
    
    // Aguardar o carregamento
    await page.waitForLoadState('networkidle');
    
    // Verificar se o filtro foi persistido
    await expect(page.locator('[data-testid="active-filter-indicator"]')).toBeVisible();
    
    // Verificar se as datas estão preenchidas
    const startDate = await page.locator('[data-testid="start-date-input"]').inputValue();
    const endDate = await page.locator('[data-testid="end-date-input"]').inputValue();
    
    expect(startDate).toBe('2024-01-01');
    expect(endDate).toBe('2024-01-15');
  });

  test('should handle real-time updates', async ({ page }) => {
    // Aguardar o carregamento inicial
    await page.waitForSelector('[data-testid="metrics-grid"]');
    
    // Simular uma atualização em tempo real
    await page.evaluate(() => {
      // Disparar um evento customizado que simula atualização em tempo real
      window.dispatchEvent(new CustomEvent('realtime-update', {
        detail: {
          type: 'ticket_created',
          data: { id: 999, title: 'Novo ticket' }
        }
      }));
    });
    
    // Aguardar a atualização ser processada
    await page.waitForTimeout(1000);
    
    // Verificar se a notificação de atualização aparece
    await expect(page.locator('[data-testid="update-notification"]')).toBeVisible();
    
    // Verificar se os dados foram atualizados
    await expect(page.locator('[data-testid="metrics-grid"]')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Aguardar o carregamento
    await page.waitForSelector('[data-testid="dashboard-title"]');
    
    // Testar navegação por tab
    await page.keyboard.press('Tab');
    
    // Verificar se o primeiro elemento focável está focado
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Continuar navegando por tab
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Testar atalhos de teclado
    await page.keyboard.press('Control+r'); // Refresh
    await page.waitForLoadState('networkidle');
    
    // Verificar se a página foi atualizada
    await expect(page.locator('[data-testid="metrics-grid"]')).toBeVisible();
  });

  test('should display tooltips on hover', async ({ page }) => {
    // Aguardar o carregamento
    await page.waitForSelector('[data-testid="metrics-grid"]');
    
    // Fazer hover sobre uma métrica
    await page.hover('[data-testid="total-tickets"]');
    
    // Aguardar o tooltip aparecer
    await page.waitForSelector('[data-testid="tooltip"]');
    
    // Verificar se o tooltip está visível e tem conteúdo
    await expect(page.locator('[data-testid="tooltip"]')).toBeVisible();
    await expect(page.locator('[data-testid="tooltip"]')).toContainText('Total de tickets');
    
    // Mover o mouse para fora para esconder o tooltip
    await page.hover('[data-testid="dashboard-title"]');
    
    // Verificar se o tooltip desapareceu
    await expect(page.locator('[data-testid="tooltip"]')).not.toBeVisible();
  });
});