import { test, expect } from '@playwright/test';

// Note: Global setup and teardown are handled by playwright.config.ts

test.describe('Tickets E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navegar para a página de tickets
    await page.goto('/tickets');

    // Aguardar o carregamento da página
    await page.waitForLoadState('networkidle');
  });

  test('should display tickets list', async ({ page }) => {
    // Verificar se o título da página está correto
    expect(mockPage.url()).toContain('/tickets');

    // Verificar se os elementos principais estão visíveis
    expect(await mockPage.locator('[data-testid="tickets-header"]').isVisible()).toBe(true);
    expect(await mockPage.locator('[data-testid="tickets-list"]').isVisible()).toBe(true);

    // Verificar se pelo menos um ticket está sendo exibido
    expect(await mockPage.locator('[data-testid="ticket-card"]').first().toBeVisible()).toBe(true);

    // Verificar se os controles de filtro estão presentes
    expect(await mockPage.locator('[data-testid="status-filter"]').isVisible()).toBe(true);
    expect(await mockPage.locator('[data-testid="priority-filter"]').isVisible()).toBe(true);
    expect(await mockPage.locator('[data-testid="search-input"]').isVisible()).toBe(true);
  });

  test('should filter tickets by status', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Contar o número inicial de tickets
    const initialCount = await page.locator('[data-testid="ticket-card"]').count();

    // Aplicar filtro de status
    await page.click('[data-testid="status-filter"]');
    await page.click('[data-testid="status-option-open"]');

    // Aguardar a filtragem
    await page.waitForLoadState('networkidle');

    // Verificar se apenas tickets com status "open" estão visíveis
    const openTickets = page.locator('[data-testid="ticket-card"][data-status="open"]');
    const ticketCount = await openTickets.count();

    expect(ticketCount).toBeGreaterThan(0);

    // Verificar se todos os tickets visíveis têm status "open"
    for (let i = 0; i < ticketCount; i++) {
      const ticket = openTickets.nth(i);
      await expect(ticket.locator('[data-testid="ticket-status"]')).toContainText('Aberto');
    }
  });

  test('should filter tickets by priority', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Aplicar filtro de prioridade
    await page.click('[data-testid="priority-filter"]');
    await page.click('[data-testid="priority-option-high"]');

    // Aguardar a filtragem
    await page.waitForLoadState('networkidle');

    // Verificar se apenas tickets com prioridade "high" estão visíveis
    const highPriorityTickets = page.locator('[data-testid="ticket-card"][data-priority="high"]');
    const ticketCount = await highPriorityTickets.count();

    expect(ticketCount).toBeGreaterThan(0);

    // Verificar se todos os tickets visíveis têm prioridade "high"
    for (let i = 0; i < ticketCount; i++) {
      const ticket = highPriorityTickets.nth(i);
      await expect(ticket.locator('[data-testid="ticket-priority"]')).toContainText('Alta');
    }
  });

  test('should search tickets by text', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Realizar busca por texto
    await page.fill('[data-testid="search-input"]', 'rede');
    await page.keyboard.press('Enter');

    // Aguardar os resultados da busca
    await page.waitForLoadState('networkidle');

    // Verificar se os resultados contêm o termo buscado
    const searchResults = page.locator('[data-testid="ticket-card"]');
    const resultCount = await searchResults.count();

    if (resultCount > 0) {
      // Verificar se pelo menos um resultado contém o termo "rede"
      const firstResult = searchResults.first();
      const title = await firstResult.textContent();
      const description = await firstResult.textContent();

      const containsSearchTerm =
        title?.toLowerCase().includes('rede') || description?.toLowerCase().includes('rede');

      expect(containsSearchTerm).toBeTruthy();
    }
  });

  test('should open ticket details', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Clicar no primeiro ticket
    await page.click('[data-testid="ticket-card"]');

    // Aguardar a página de detalhes carregar
    await page.waitForLoadState('networkidle');

    // Verificar se estamos na página de detalhes
    expect(page.url()).toMatch(/\/tickets\/\d+/);

    // Verificar se os elementos de detalhes estão visíveis
    await expect(page.locator('[data-testid="ticket-details-header"]')).toBeVisible();
    await expect(page.locator('[data-testid="ticket-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="ticket-description"]')).toBeVisible();
    await expect(page.locator('[data-testid="ticket-metadata"]')).toBeVisible();
  });

  test('should create new ticket', async ({ page }) => {
    // Clicar no botão de criar novo ticket
    await page.click('[data-testid="new-ticket-button"]');

    // Aguardar o modal/formulário aparecer
    await page.waitForSelector('[data-testid="ticket-form"]');

    // Preencher o formulário
    await page.fill('[data-testid="ticket-title-input"]', 'Teste E2E - Novo Ticket');
    await page.fill(
      '[data-testid="ticket-description-input"]',
      'Descrição do ticket criado via teste E2E'
    );

    // Selecionar prioridade
    await page.click('[data-testid="priority-select"]');
    await page.click('[data-testid="priority-option-normal"]');

    // Selecionar categoria
    await page.click('[data-testid="category-select"]');
    await page.click('[data-testid="category-option-software"]');

    // Submeter o formulário
    await page.click('[data-testid="submit-ticket-button"]');

    // Aguardar a criação e redirecionamento
    await page.waitForLoadState('networkidle');

    // Verificar se foi redirecionado para a lista ou detalhes
    const currentUrl = page.url();
    expect(currentUrl).toMatch(/\/tickets/);

    // Verificar se há uma mensagem de sucesso
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('should update ticket status', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Clicar no primeiro ticket para abrir detalhes
    await page.click('[data-testid="ticket-card"]');

    // Aguardar a página de detalhes carregar
    await page.waitForLoadState('networkidle');

    // Clicar no botão de editar status
    await page.click('[data-testid="edit-status-button"]');

    // Aguardar o dropdown de status aparecer
    await page.waitForSelector('[data-testid="status-dropdown"]');

    // Selecionar novo status
    await page.click('[data-testid="status-option-assigned"]');

    // Confirmar a mudança
    await page.click('[data-testid="confirm-status-change"]');

    // Aguardar a atualização
    await page.waitForLoadState('networkidle');

    // Verificar se o status foi atualizado
    await expect(page.locator('[data-testid="ticket-status"]')).toContainText('Atribuído');

    // Verificar se há uma mensagem de sucesso
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('should add comment to ticket', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Clicar no primeiro ticket para abrir detalhes
    await page.click('[data-testid="ticket-card"]');

    // Aguardar a página de detalhes carregar
    await page.waitForLoadState('networkidle');

    // Rolar até a seção de comentários
    await page.locator('[data-testid="comments-section"]').scrollIntoViewIfNeeded();

    // Contar comentários existentes
    const initialCommentCount = await page.locator('[data-testid="comment-item"]').count();

    // Adicionar novo comentário
    await page.fill('[data-testid="comment-input"]', 'Comentário adicionado via teste E2E');
    await page.click('[data-testid="add-comment-button"]');

    // Aguardar o comentário ser adicionado
    await page.waitForLoadState('networkidle');

    // Verificar se o número de comentários aumentou
    const newCommentCount = await page.locator('[data-testid="comment-item"]').count();
    expect(newCommentCount).toBe(initialCommentCount + 1);

    // Verificar se o novo comentário está visível
    const lastComment = page.locator('[data-testid="comment-item"]').last();
    await expect(lastComment).toContainText('Comentário adicionado via teste E2E');
  });

  test('should handle pagination', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Verificar se a paginação está presente (se houver muitos tickets)
    const paginationExists = await page.locator('[data-testid="pagination"]').isVisible();

    if (paginationExists) {
      // Contar tickets na primeira página
      const firstPageTickets = await page.locator('[data-testid="ticket-card"]').count();

      // Ir para a próxima página
      await page.click('[data-testid="next-page-button"]');

      // Aguardar o carregamento
      await page.waitForLoadState('networkidle');

      // Verificar se estamos na página 2
      await expect(page.locator('[data-testid="current-page"]')).toContainText('2');

      // Verificar se há tickets na segunda página
      const secondPageTickets = await page.locator('[data-testid="ticket-card"]').count();
      expect(secondPageTickets).toBeGreaterThan(0);

      // Voltar para a primeira página
      await page.click('[data-testid="prev-page-button"]');

      // Aguardar o carregamento
      await page.waitForLoadState('networkidle');

      // Verificar se voltamos para a página 1
      await expect(page.locator('[data-testid="current-page"]')).toContainText('1');
    }
  });

  test('should handle bulk actions', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Selecionar múltiplos tickets
    await page.click('[data-testid="ticket-checkbox"]', { nth: 0 });
    await page.click('[data-testid="ticket-checkbox"]', { nth: 1 });

    // Verificar se a barra de ações em lote apareceu
    await expect(page.locator('[data-testid="bulk-actions-bar"]')).toBeVisible();

    // Verificar se o contador de selecionados está correto
    await expect(page.locator('[data-testid="selected-count"]')).toContainText('2');

    // Testar ação em lote (ex: mudar status)
    await page.click('[data-testid="bulk-status-change"]');
    await page.click('[data-testid="bulk-status-option-assigned"]');

    // Confirmar a ação
    await page.click('[data-testid="confirm-bulk-action"]');

    // Aguardar a atualização
    await page.waitForLoadState('networkidle');

    // Verificar se há uma mensagem de sucesso
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('should export tickets data', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Clicar no botão de exportar
    await page.click('[data-testid="export-tickets-button"]');

    // Aguardar o menu de exportação aparecer
    await page.waitForSelector('[data-testid="export-menu"]');

    // Configurar o listener para download
    const downloadPromise = page.waitForEvent('download');

    // Clicar na opção de exportar CSV
    await page.click('[data-testid="export-csv"]');

    // Aguardar o download
    const download = await downloadPromise;

    // Verificar se o arquivo foi baixado
    expect(download.suggestedFilename()).toContain('tickets');
    expect(download.suggestedFilename()).toContain('.csv');
  });

  test('should handle real-time ticket updates', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Simular uma atualização em tempo real
    await page.evaluate(() => {
      // Disparar um evento customizado que simula atualização de ticket
      window.dispatchEvent(
        new CustomEvent('ticket-updated', {
          detail: {
            ticketId: 1,
            status: 'resolved',
            updatedAt: new Date().toISOString(),
          },
        })
      );
    });

    // Aguardar a atualização ser processada
    await page.waitForTimeout(1000);

    // Verificar se a notificação de atualização aparece
    await expect(page.locator('[data-testid="realtime-notification"]')).toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Definir viewport para mobile
    await page.setViewportSize({ width: 375, height: 667 });

    // Aguardar o carregamento
    await page.waitForSelector('[data-testid="tickets-list"]');

    // Verificar se o layout mobile está ativo
    await expect(page.locator('[data-testid="mobile-filters-button"]')).toBeVisible();

    // Verificar se os tickets estão em layout de lista vertical
    const ticketCards = page.locator('[data-testid="ticket-card"]');
    await expect(ticketCards.first()).toBeVisible();

    // Testar o menu de filtros mobile
    await page.click('[data-testid="mobile-filters-button"]');
    await expect(page.locator('[data-testid="mobile-filters-menu"]')).toBeVisible();
  });

  test('should handle keyboard shortcuts', async ({ page }) => {
    // Aguardar a lista de tickets carregar
    await page.waitForSelector('[data-testid="ticket-card"]');

    // Testar atalho para criar novo ticket (Ctrl+N)
    await page.keyboard.press('Control+n');

    // Verificar se o formulário de novo ticket aparece
    await expect(page.locator('[data-testid="ticket-form"]')).toBeVisible();

    // Fechar o formulário (Escape)
    await page.keyboard.press('Escape');

    // Verificar se o formulário foi fechado
    await expect(page.locator('[data-testid="ticket-form"]')).not.toBeVisible();

    // Testar atalho para busca (Ctrl+F)
    await page.keyboard.press('Control+f');

    // Verificar se o campo de busca está focado
    const searchInput = page.locator('[data-testid="search-input"]');
    await expect(searchInput).toBeVisible();
  });
});
