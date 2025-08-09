import { chromium, FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E test teardown...');
  
  try {
    // Limpar dados de teste
    await cleanupTestData();
    
    // Gerar relatório de cobertura se disponível
    await generateCoverageReport();
    
    // Limpar arquivos temporários
    await cleanupTempFiles();
    
    console.log('✅ E2E test teardown completed successfully!');
  } catch (error) {
    console.error('❌ E2E test teardown failed:', error);
    // Não falhar o processo por causa do teardown
  }
}

async function cleanupTestData() {
  console.log('🗑️ Cleaning up test data...');
  
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Limpar dados de teste do localStorage
    await page.evaluate(() => {
      // Remover apenas dados de teste, manter configurações do usuário
      const keysToRemove = [
        'test-mode',
        'test-user',
        'test-data',
        'mock-data'
      ];
      
      keysToRemove.forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
      });
    });
    
    await browser.close();
    console.log('✅ Test data cleanup completed');
  } catch (error) {
    console.error('❌ Test data cleanup failed:', error);
  }
}

async function generateCoverageReport() {
  console.log('📊 Generating coverage report...');
  
  try {
    const coverageDir = path.join(process.cwd(), 'coverage');
    const e2eCoverageDir = path.join(coverageDir, 'e2e');
    
    // Verificar se existe cobertura E2E
    if (fs.existsSync(e2eCoverageDir)) {
      console.log('📈 E2E coverage data found');
      
      // Aqui você pode adicionar lógica para processar dados de cobertura
      // Por exemplo, mesclar com cobertura de testes unitários
      
      const coverageFiles = fs.readdirSync(e2eCoverageDir);
      console.log(`📁 Found ${coverageFiles.length} coverage files`);
    } else {
      console.log('ℹ️ No E2E coverage data found');
    }
  } catch (error) {
    console.error('❌ Coverage report generation failed:', error);
  }
}

async function cleanupTempFiles() {
  console.log('🧽 Cleaning up temporary files...');
  
  try {
    const tempDirs = [
      path.join(process.cwd(), 'test-results', 'temp'),
      path.join(process.cwd(), '.playwright', 'temp'),
      path.join(process.cwd(), 'screenshots', 'temp')
    ];
    
    for (const dir of tempDirs) {
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
        console.log(`🗑️ Removed temp directory: ${dir}`);
      }
    }
    
    // Limpar arquivos de log antigos (mais de 7 dias)
    const logsDir = path.join(process.cwd(), 'logs');
    if (fs.existsSync(logsDir)) {
      const files = fs.readdirSync(logsDir);
      const now = Date.now();
      const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);
      
      files.forEach(file => {
        const filePath = path.join(logsDir, file);
        const stats = fs.statSync(filePath);
        
        if (stats.mtime.getTime() < sevenDaysAgo) {
          fs.unlinkSync(filePath);
          console.log(`🗑️ Removed old log file: ${file}`);
        }
      });
    }
    
    console.log('✅ Temporary files cleanup completed');
  } catch (error) {
    console.error('❌ Temporary files cleanup failed:', error);
  }
}

export default globalTeardown;