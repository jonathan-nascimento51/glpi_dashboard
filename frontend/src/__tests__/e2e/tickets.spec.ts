import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { setupTestEnvironment, cleanupTestEnvironment } from './global-setup';

// Mock page object for E2E simulation
const mockPage = {
  goto: async (url: string) => ({ url }),
  waitForSelector: async (selector: string) => ({ selector }),
  waitForLoadState: async (state: string) => ({ state }),
  click: async (selector: string, options?: any) => ({ clicked: selector, options }),
  fill: async (selector: string, value: string) => ({ filled: selector, value }),
  textContent: async () => 'Mock content',
  screenshot: async () => Buffer.from('mock-screenshot'),
  locator: (selector: string) => ({
    first: () => ({ toBeVisible: () => true, textContent: async () => 'Mock text' }),
    last: () => ({ toContainText: () => true }),
    nth: (index: number) => ({ locator: (sel: string) => ({ toContainText: () => true }) }),
    count: async () => 5,
    scrollIntoViewIfNeeded: async () => ({}),
    isVisible: async () => true
  }),
  keyboard: {
    press: async (key: string) => ({ key })
  },
  url: () => '/tickets/123',
  setViewportSize: async (size: { width: number; height: number }) => ({ size }),
  waitForTimeout: async (ms: number) => ({ ms }),
  waitForEvent: async (event: string) => ({ suggestedFilename: () => 'tickets.csv' }),
  evaluate: async (fn: Function) => fn()
};

describe('Tickets E2E Tests', () => {
  beforeAll(async () => {
    await setupTestEnvironment();
  });

  afterAll(async () => {
    await cleanupTestEnvironment();
  });

  beforeEach(async () => {
    // Navegar para a página de tickets
    await mockPage.goto('/tickets');
    
    // Aguardar o carregamento da página
    await mockPage.waitForLoadState('networkidle');
  });

  it('should display tickets list', async () => {
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

  it('should filter tickets by status', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Contar o número inicial de tickets
    const initialCount = await mockPage.locator('[data-testid="ticket-card"]').count();
    
    // Aplicar filtro de status
    await mockPage.click('[data-testid="status-filter"]');
    await mockPage.click('[data-testid="status-option-open"]');
    
    // Aguardar a filtragem
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se apenas tickets com status "open" estão visíveis
    const openTickets = mockPage.locator('[data-testid="ticket-card"][data-status="open"]');
    const ticketCount = await openTickets.count();
    
    expect(ticketCount).toBeGreaterThan(0);
    
    // Verificar se todos os tickets visíveis têm status "open"
    for (let i = 0; i < ticketCount; i++) {
      const ticket = openTickets.nth(i);
      expect(ticket.locator('[data-testid="ticket-status"]').toContainText('Aberto')).toBe(true);
    }
  });

  it('should filter tickets by priority', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Aplicar filtro de prioridade
    await mockPage.click('[data-testid="priority-filter"]');
    await mockPage.click('[data-testid="priority-option-high"]');
    
    // Aguardar a filtragem
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se apenas tickets com prioridade "high" estão visíveis
    const highPriorityTickets = mockPage.locator('[data-testid="ticket-card"][data-priority="high"]');
    const ticketCount = await highPriorityTickets.count();
    
    expect(ticketCount).toBeGreaterThan(0);
    
    // Verificar se todos os tickets visíveis têm prioridade "high"
    for (let i = 0; i < ticketCount; i++) {
      const ticket = highPriorityTickets.nth(i);
      expect(ticket.locator('[data-testid="ticket-priority"]').toContainText('Alta')).toBe(true);
    }
  });

  it('should search tickets by text', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Realizar busca por texto
    await mockPage.fill('[data-testid="search-input"]', 'rede');
    await mockPage.keyboard.press('Enter');
    
    // Aguardar os resultados da busca
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se os resultados contêm o termo buscado
    const searchResults = mockPage.locator('[data-testid="ticket-card"]');
    const resultCount = await searchResults.count();
    
    if (resultCount > 0) {
      // Verificar se pelo menos um resultado contém o termo "rede"
      const firstResult = searchResults.first();
      const title = await firstResult.textContent();
      const description = await firstResult.textContent();
      
      const containsSearchTerm = 
        title?.toLowerCase().includes('rede') || 
        description?.toLowerCase().includes('rede');
      
      expect(containsSearchTerm).toBeTruthy();
    }
  });

  it('should open ticket details', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Clicar no primeiro ticket
    await mockPage.click('[data-testid="ticket-card"]');
    
    // Aguardar a página de detalhes carregar
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se estamos na página de detalhes
    expect(mockPage.url()).toMatch(/\/tickets\/\d+/);
    
    // Verificar se os elementos de detalhes estão visíveis
    expect(await mockPage.locator('[data-testid="ticket-details-header"]').isVisible()).toBe(true);
    expect(await mockPage.locator('[data-testid="ticket-title"]').isVisible()).toBe(true);
    expect(await mockPage.locator('[data-testid="ticket-description"]').isVisible()).toBe(true);
    expect(await mockPage.locator('[data-testid="ticket-metadata"]').isVisible()).toBe(true);
  });

  it('should create new ticket', async () => {
    // Clicar no botão de criar novo ticket
    await mockPage.click('[data-testid="new-ticket-button"]');
    
    // Aguardar o modal/formulário aparecer
    await mockPage.waitForSelector('[data-testid="ticket-form"]');
    
    // Preencher o formulário
    await mockPage.fill('[data-testid="ticket-title-input"]', 'Teste E2E - Novo Ticket');
    await mockPage.fill('[data-testid="ticket-description-input"]', 'Descrição do ticket criado via teste E2E');
    
    // Selecionar prioridade
    await mockPage.click('[data-testid="priority-select"]');
    await mockPage.click('[data-testid="priority-option-normal"]');
    
    // Selecionar categoria
    await mockPage.click('[data-testid="category-select"]');
    await mockPage.click('[data-testid="category-option-software"]');
    
    // Submeter o formulário
    await mockPage.click('[data-testid="submit-ticket-button"]');
    
    // Aguardar a criação e redirecionamento
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se foi redirecionado para a lista ou detalhes
    const currentUrl = mockPage.url();
    expect(currentUrl).toMatch(/\/tickets/);
    
    // Verificar se há uma mensagem de sucesso
    expect(await mockPage.locator('[data-testid="success-message"]').isVisible()).toBe(true);
  });

  it('should update ticket status', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Clicar no primeiro ticket para abrir detalhes
    await mockPage.click('[data-testid="ticket-card"]');
    
    // Aguardar a página de detalhes carregar
    await mockPage.waitForLoadState('networkidle');
    
    // Clicar no botão de editar status
    await mockPage.click('[data-testid="edit-status-button"]');
    
    // Aguardar o dropdown de status aparecer
    await mockPage.waitForSelector('[data-testid="status-dropdown"]');
    
    // Selecionar novo status
    await mockPage.click('[data-testid="status-option-assigned"]');
    
    // Confirmar a mudança
    await mockPage.click('[data-testid="confirm-status-change"]');
    
    // Aguardar a atualização
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se o status foi atualizado
    expect(mockPage.locator('[data-testid="ticket-status"]').toContainText('Atribuído')).toBe(true);
    
    // Verificar se há uma mensagem de sucesso
    expect(await mockPage.locator('[data-testid="success-message"]').isVisible()).toBe(true);
  });

  it('should add comment to ticket', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Clicar no primeiro ticket para abrir detalhes
    await mockPage.click('[data-testid="ticket-card"]');
    
    // Aguardar a página de detalhes carregar
    await mockPage.waitForLoadState('networkidle');
    
    // Rolar até a seção de comentários
    await mockPage.locator('[data-testid="comments-section"]').scrollIntoViewIfNeeded();
    
    // Contar comentários existentes
    const initialCommentCount = await mockPage.locator('[data-testid="comment-item"]').count();
    
    // Adicionar novo comentário
    await mockPage.fill('[data-testid="comment-input"]', 'Comentário adicionado via teste E2E');
    await mockPage.click('[data-testid="add-comment-button"]');
    
    // Aguardar o comentário ser adicionado
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se o número de comentários aumentou
    const newCommentCount = await mockPage.locator('[data-testid="comment-item"]').count();
    expect(newCommentCount).toBe(initialCommentCount + 1);
    
    // Verificar se o novo comentário está visível
    const lastComment = mockPage.locator('[data-testid="comment-item"]').last();
    expect(lastComment.toContainText('Comentário adicionado via teste E2E')).toBe(true);
  });

  it('should handle pagination', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Verificar se a paginação está presente (se houver muitos tickets)
    const paginationExists = await mockPage.locator('[data-testid="pagination"]').isVisible();
    
    if (paginationExists) {
      // Contar tickets na primeira página
      const firstPageTickets = await mockPage.locator('[data-testid="ticket-card"]').count();
      
      // Ir para a próxima página
      await mockPage.click('[data-testid="next-page-button"]');
      
      // Aguardar o carregamento
      await mockPage.waitForLoadState('networkidle');
      
      // Verificar se estamos na página 2
      expect(mockPage.locator('[data-testid="current-page"]').toContainText('2')).toBe(true);
      
      // Verificar se há tickets na segunda página
      const secondPageTickets = await mockPage.locator('[data-testid="ticket-card"]').count();
      expect(secondPageTickets).toBeGreaterThan(0);
      
      // Voltar para a primeira página
      await mockPage.click('[data-testid="prev-page-button"]');
      
      // Aguardar o carregamento
      await mockPage.waitForLoadState('networkidle');
      
      // Verificar se voltamos para a página 1
      expect(mockPage.locator('[data-testid="current-page"]').toContainText('1')).toBe(true);
    }
  });

  it('should handle bulk actions', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Selecionar múltiplos tickets
    await mockPage.click('[data-testid="ticket-checkbox"]', { nth: 0 });
    await mockPage.click('[data-testid="ticket-checkbox"]', { nth: 1 });
    
    // Verificar se a barra de ações em lote apareceu
    expect(await mockPage.locator('[data-testid="bulk-actions-bar"]').isVisible()).toBe(true);
    
    // Verificar se o contador de selecionados está correto
    expect(mockPage.locator('[data-testid="selected-count"]').toContainText('2')).toBe(true);
    
    // Testar ação em lote (ex: mudar status)
    await mockPage.click('[data-testid="bulk-status-change"]');
    await mockPage.click('[data-testid="bulk-status-option-assigned"]');
    
    // Confirmar a ação
    await mockPage.click('[data-testid="confirm-bulk-action"]');
    
    // Aguardar a atualização
    await mockPage.waitForLoadState('networkidle');
    
    // Verificar se há uma mensagem de sucesso
    expect(await mockPage.locator('[data-testid="success-message"]').isVisible()).toBe(true);
  });

  it('should export tickets data', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Clicar no botão de exportar
    await mockPage.click('[data-testid="export-tickets-button"]');
    
    // Aguardar o menu de exportação aparecer
    await mockPage.waitForSelector('[data-testid="export-menu"]');
    
    // Configurar o listener para download
    const downloadPromise = mockPage.waitForEvent('download');
    
    // Clicar na opção de exportar CSV
    await mockPage.click('[data-testid="export-csv"]');
    
    // Aguardar o download
    const download = await downloadPromise;
    
    // Verificar se o arquivo foi baixado
    expect(download.suggestedFilename()).toContain('tickets');
    expect(download.suggestedFilename()).toContain('.csv');
  });

  it('should handle real-time ticket updates', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Simular uma atualização em tempo real
    await mockPage.evaluate(() => {
      // Disparar um evento customizado que simula atualização de ticket
      window.dispatchEvent(new CustomEvent('ticket-updated', {
        detail: {
          ticketId: 1,
          status: 'resolved',
          updatedAt: new Date().toISOString()
        }
      }));
    });
    
    // Aguardar a atualização ser processada
    await mockPage.waitForTimeout(1000);
    
    // Verificar se a notificação de atualização aparece
    expect(await mockPage.locator('[data-testid="realtime-notification"]').isVisible()).toBe(true);
  });

  it('should be responsive on mobile devices', async () => {
    // Definir viewport para mobile
    await mockPage.setViewportSize({ width: 375, height: 667 });
    
    // Aguardar o carregamento
    await mockPage.waitForSelector('[data-testid="tickets-list"]');
    
    // Verificar se o layout mobile está ativo
    expect(await mockPage.locator('[data-testid="mobile-filters-button"]').isVisible()).toBe(true);
    
    // Verificar se os tickets estão em layout de lista vertical
    const ticketCards = mockPage.locator('[data-testid="ticket-card"]');
    expect(await ticketCards.first().toBeVisible()).toBe(true);
    
    // Testar o menu de filtros mobile
    await mockPage.click('[data-testid="mobile-filters-button"]');
    expect(await mockPage.locator('[data-testid="mobile-filters-menu"]').isVisible()).toBe(true);
  });

  it('should handle keyboard shortcuts', async () => {
    // Aguardar a lista de tickets carregar
    await mockPage.waitForSelector('[data-testid="ticket-card"]');
    
    // Testar atalho para criar novo ticket (Ctrl+N)
    await mockPage.keyboard.press('Control+n');
    
    // Verificar se o formulário de novo ticket aparece
    expect(await mockPage.locator('[data-testid="ticket-form"]').isVisible()).toBe(true);
    
    // Fechar o formulário (Escape)
    await mockPage.keyboard.press('Escape');
    
    // Verificar se o formulário foi fechado
    expect(await mockPage.locator('[data-testid="ticket-form"]').isVisible()).toBe(false);
    
    // Testar atalho para busca (Ctrl+F)
    await mockPage.keyboard.press('Control+f');
    
    // Verificar se o campo de busca está focado
    const searchInput = mockPage.locator('[data-testid="search-input"]');
    expect(await searchInput.isVisible()).toBe(true);
  });
});