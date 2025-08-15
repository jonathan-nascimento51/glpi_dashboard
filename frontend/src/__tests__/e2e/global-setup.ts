import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test setup...');
  
  // Verificar se o servidor de desenvolvimento esta rodando
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:5173';
  
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Tentar acessar a aplicacao
    console.log(`📡 Checking if dev server is running at ${baseURL}...`);
    await page.goto(baseURL, { timeout: 30000 });
    
    // Aguardar a aplicacao carregar completamente
    await page.waitForLoadState('networkidle');
    
    // Verificar se a aplicacao carregou corretamente
    const title = await page.title();
    console.log(`✅ Application loaded successfully. Title: ${title}`);
    
    // Configurar dados de teste se necessario
    await setupTestData(page);
    
    await browser.close();
    
    console.log('✅ E2E test setup completed successfully!');
  } catch (error) {
    console.error('❌ E2E test setup failed:', error);
    throw error;
  }
}

async function setupTestData(page: any) {
  console.log('🔧 Setting up test data...');
  
  try {
    // Limpar localStorage para garantir estado limpo
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Configurar dados de teste no localStorage se necessario
    await page.evaluate(() => {
      // Configuracoes de teste
      localStorage.setItem('test-mode', 'true');
      localStorage.setItem('api-base-url', 'http://localhost:5000');
      
      // Dados de usuario de teste
      const testUser = {
        id: 999,
        name: 'Test User',
        email: 'test@example.com',
        role: 'admin'
      };
      localStorage.setItem('test-user', JSON.stringify(testUser));
      
      // Configuracoes de tema para testes
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
