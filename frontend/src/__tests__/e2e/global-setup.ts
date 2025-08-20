import { chromium, FullConfig, Page } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test setup...');

  // Verificar se o servidor de desenvolvimento está rodando
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:3001';

  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    // Tentar acessar a aplicação
    console.log(`📡 Checking if dev server is running at ${baseURL}...`);
    await page.goto(baseURL, { timeout: 30000 });

    // Aguardar a aplicação carregar completamente
    await page.waitForLoadState('networkidle');

    // Verificar se a aplicação carregou corretamente
    const title = await page.title();
    console.log(`✅ Application loaded successfully. Title: ${title}`);

    // Configurar dados de teste se necessário
    await setupTestData(page);

    await browser.close();

    console.log('✅ E2E test setup completed successfully!');
  } catch (error) {
    console.error('❌ E2E test setup failed:', error);
    throw error;
  }
}

async function setupTestData(page: Page) {
  console.log('🔧 Setting up test data...');

  try {
    // Limpar localStorage para garantir estado limpo
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Configurar dados de teste no localStorage se necessário
    await page.evaluate(() => {
      // Configurações de teste
      localStorage.setItem('test-mode', 'true');
      localStorage.setItem('api-base-url', 'http://localhost:5000');

      // Dados de usuário de teste
      const testUser = {
        id: 999,
        name: 'Test User',
        email: 'test@example.com',
        role: 'admin',
      };
      localStorage.setItem('test-user', JSON.stringify(testUser));

      // Configurações de tema para testes
      localStorage.setItem('theme', 'light');
      localStorage.setItem('language', 'pt-BR');
    });

    console.log('✅ Test data setup completed');
  } catch (error) {
    console.error('❌ Test data setup failed:', error);
    throw error;
  }
}

export default globalSetup;
