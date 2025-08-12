/**
 * Script de Validação Anti-Zero
 * 
 * Verifica se o teste E2E anti-zero está funcionando corretamente
 * e gera um relatório de validação.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configurações
const ARTIFACTS_DIR = path.join(__dirname, 'artifacts', 'e2e');
const TEST_RESULTS_DIR = path.join(__dirname, 'test-results');
const REPORT_FILE = path.join(ARTIFACTS_DIR, 'anti-zero-validation-report.json');

/**
 * Verifica se o diretório de artifacts existe
 */
function checkArtifactsDirectory() {
  console.log(' Verificando diretório de artifacts...');
  
  if (!fs.existsSync(ARTIFACTS_DIR)) {
    console.log(' Criando diretório de artifacts...');
    fs.mkdirSync(ARTIFACTS_DIR, { recursive: true });
  }
  
  console.log(' Diretório de artifacts:', ARTIFACTS_DIR);
  return true;
}

/**
 * Verifica os arquivos de screenshot gerados
 */
function checkScreenshots() {
  console.log(' Verificando screenshots gerados...');
  
  const screenshots = [];
  
  // Verificar no diretório de artifacts
  if (fs.existsSync(ARTIFACTS_DIR)) {
    const artifactFiles = fs.readdirSync(ARTIFACTS_DIR)
      .filter(file => file.endsWith('.png'))
      .map(file => ({
        name: file,
        path: path.join(ARTIFACTS_DIR, file),
        size: fs.statSync(path.join(ARTIFACTS_DIR, file)).size,
        created: fs.statSync(path.join(ARTIFACTS_DIR, file)).mtime
      }));
    
    screenshots.push(...artifactFiles);
  }
  
  // Verificar no diretório de resultados de teste
  if (fs.existsSync(TEST_RESULTS_DIR)) {
    const findScreenshots = (dir) => {
      const files = [];
      const items = fs.readdirSync(dir, { withFileTypes: true });
      
      for (const item of items) {
        const fullPath = path.join(dir, item.name);
        if (item.isDirectory()) {
          files.push(...findScreenshots(fullPath));
        } else if (item.name.endsWith('.png')) {
          files.push({
            name: item.name,
            path: fullPath,
            size: fs.statSync(fullPath).size,
            created: fs.statSync(fullPath).mtime
          });
        }
      }
      
      return files;
    };
    
    const testResultScreenshots = findScreenshots(TEST_RESULTS_DIR);
    screenshots.push(...testResultScreenshots);
  }
  
  console.log(` Encontrados ${screenshots.length} screenshots`);
  screenshots.forEach(screenshot => {
    console.log(`  - ${screenshot.name} (${screenshot.size} bytes)`);
  });
  
  return screenshots;
}

/**
 * Verifica se o arquivo de teste existe e está bem formado
 */
function validateTestFile() {
  console.log(' Validando arquivo de teste...');
  
  const testFile = path.join(__dirname, 'e2e', 'anti-zero-guard.spec.ts');
  
  if (!fs.existsSync(testFile)) {
    console.log(' Arquivo de teste não encontrado:', testFile);
    return { valid: false, error: 'Arquivo não encontrado' };
  }
  
  const content = fs.readFileSync(testFile, 'utf8');
  
  // Verificar se contém os testes esperados
  const requiredTests = [
    'PASS: Dashboard deve exibir dados reais',
    'FAIL: Dashboard com dados zero deve falhar',
    'Anti-zero guard triggered',
    'Teste de conectividade'
  ];
  
  const missingTests = requiredTests.filter(test => !content.includes(test));
  
  if (missingTests.length > 0) {
    console.log(' Testes faltando:', missingTests);
    return { valid: false, error: 'Testes faltando', missing: missingTests };
  }
  
  console.log(' Arquivo de teste válido');
  return { valid: true, size: content.length, lines: content.split('\n').length };
}

/**
 * Gera relatório de validação
 */
function generateReport(screenshots, testFileValidation) {
  console.log(' Gerando relatório de validação...');
  
  const report = {
    timestamp: new Date().toISOString(),
    validation: {
      artifactsDirectory: fs.existsSync(ARTIFACTS_DIR),
      testFile: testFileValidation,
      screenshots: {
        count: screenshots.length,
        files: screenshots.map(s => ({
          name: s.name,
          size: s.size,
          created: s.created
        }))
      }
    },
    summary: {
      status: testFileValidation.valid && fs.existsSync(ARTIFACTS_DIR) ? 'READY' : 'NEEDS_ATTENTION',
      readyForE2E: testFileValidation.valid,
      artifactsConfigured: fs.existsSync(ARTIFACTS_DIR),
      screenshotsGenerated: screenshots.length > 0
    },
    nextSteps: [
      'Execute o teste completo: npm run test:e2e -- anti-zero-guard.spec.ts',
      'Verifique os screenshots em artifacts/e2e/',
      'Valide que o teste PASS funciona com dados reais',
      'Valide que o teste FAIL funciona com dados zero'
    ]
  };
  
  // Salvar relatório
  fs.writeFileSync(REPORT_FILE, JSON.stringify(report, null, 2));
  
  console.log(' Relatório salvo:', REPORT_FILE);
  return report;
}

/**
 * Função principal
 */
function main() {
  console.log(' Iniciando validação do teste anti-zero...');
  console.log('=' .repeat(50));
  
  try {
    // 1. Verificar diretório de artifacts
    checkArtifactsDirectory();
    
    // 2. Validar arquivo de teste
    const testFileValidation = validateTestFile();
    
    // 3. Verificar screenshots
    const screenshots = checkScreenshots();
    
    // 4. Gerar relatório
    const report = generateReport(screenshots, testFileValidation);
    
    console.log('\n' + '=' .repeat(50));
    console.log(' RESUMO DA VALIDAÇÃO');
    console.log('=' .repeat(50));
    console.log(`Status: ${report.summary.status}`);
    console.log(`Arquivo de teste: ${report.summary.readyForE2E ? '' : ''}`);
    console.log(`Artifacts configurados: ${report.summary.artifactsConfigured ? '' : ''}`);
    console.log(`Screenshots: ${report.summary.screenshotsGenerated ? '' : ''} (${screenshots.length})`);
    
    console.log('\n PRÓXIMOS PASSOS:');
    report.nextSteps.forEach((step, index) => {
      console.log(`${index + 1}. ${step}`);
    });
    
    console.log(`\n Relatório completo: ${REPORT_FILE}`);
    
  } catch (error) {
    console.error(' Erro durante a validação:', error.message);
    process.exit(1);
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  main();
}

module.exports = {
  checkArtifactsDirectory,
  checkScreenshots,
  validateTestFile,
  generateReport
};
