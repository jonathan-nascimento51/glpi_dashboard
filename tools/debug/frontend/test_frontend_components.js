#!/usr/bin/env node

/**
 * Script para testar componentes do frontend do GLPI Dashboard
 * Uso: node test_frontend_components.js [--component COMPONENT_NAME]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuração
const FRONTEND_DIR = path.join(__dirname, '..', '..', '..', 'frontend');
const SRC_DIR = path.join(FRONTEND_DIR, 'src');
const COMPONENTS_DIR = path.join(SRC_DIR, 'components');
const HOOKS_DIR = path.join(SRC_DIR, 'hooks');
const SERVICES_DIR = path.join(SRC_DIR, 'services');

function log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = {
        'info': '🔍',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'debug': '🐛'
    }[type] || 'ℹ️';
    
    console.log(`${prefix} [${timestamp}] ${message}`);
}

function checkFileExists(filePath, description) {
    if (fs.existsSync(filePath)) {
        log(`${description}: Encontrado`, 'success');
        return true;
    } else {
        log(`${description}: Não encontrado em ${filePath}`, 'error');
        return false;
    }
}

function analyzeJSFile(filePath, fileName) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split('\n');
        
        const analysis = {
            totalLines: lines.length,
            imports: [],
            exports: [],
            functions: [],
            hooks: [],
            components: [],
            errors: []
        };
        
        lines.forEach((line, index) => {
            const trimmed = line.trim();
            
            // Detecta imports
            if (trimmed.startsWith('import ')) {
                analysis.imports.push({
                    line: index + 1,
                    content: trimmed
                });
            }
            
            // Detecta exports
            if (trimmed.startsWith('export ')) {
                analysis.exports.push({
                    line: index + 1,
                    content: trimmed
                });
            }
            
            // Detecta funções
            if (trimmed.includes('function ') || trimmed.includes('const ') && trimmed.includes(' = ')) {
                analysis.functions.push({
                    line: index + 1,
                    content: trimmed.substring(0, 80) + (trimmed.length > 80 ? '...' : '')
                });
            }
            
            // Detecta hooks React
            if (trimmed.includes('use') && (trimmed.includes('useState') || trimmed.includes('useEffect') || trimmed.includes('useCallback') || trimmed.includes('useMemo'))) {
                analysis.hooks.push({
                    line: index + 1,
                    content: trimmed
                });
            }
            
            // Detecta componentes React
            if (trimmed.includes('const ') && trimmed.includes(' = ') && (trimmed.includes('React.') || trimmed.includes('jsx') || trimmed.includes('tsx'))) {
                analysis.components.push({
                    line: index + 1,
                    content: trimmed.substring(0, 80) + (trimmed.length > 80 ? '...' : '')
                });
            }
            
            // Detecta possíveis erros de sintaxe
            if (trimmed.includes('console.error') || trimmed.includes('throw ') || trimmed.includes('Error(')) {
                analysis.errors.push({
                    line: index + 1,
                    content: trimmed
                });
            }
        });
        
        return analysis;
        
    } catch (error) {
        log(`Erro ao analisar ${fileName}: ${error.message}`, 'error');
        return null;
    }
}

function testComponentStructure() {
    log('\n🏗️  Testando estrutura de componentes...', 'info');
    
    const criticalComponents = [
        'dashboard/ModernDashboard.tsx',
        'dashboard/RankingTable.tsx',
        'dashboard/MetricsCards.tsx',
        'dashboard/SystemStatus.tsx'
    ];
    
    let passed = 0;
    
    criticalComponents.forEach(component => {
        const filePath = path.join(COMPONENTS_DIR, component);
        if (checkFileExists(filePath, `Componente ${component}`)) {
            passed++;
            
            // Analisa o arquivo
            const analysis = analyzeJSFile(filePath, component);
            if (analysis) {
                log(`  📊 ${component}: ${analysis.totalLines} linhas, ${analysis.imports.length} imports, ${analysis.exports.length} exports`);
                
                if (analysis.errors.length > 0) {
                    log(`  ⚠️  ${analysis.errors.length} possíveis problemas encontrados`, 'warning');
                }
            }
        }
    });
    
    return { passed, total: criticalComponents.length };
}

function testHooks() {
    log('\n🎣 Testando hooks...', 'info');
    
    const criticalHooks = [
        'useDashboard.ts',
        'useApi.ts',
        'useTechnicianRanking.ts'
    ];
    
    let passed = 0;
    
    criticalHooks.forEach(hook => {
        const filePath = path.join(HOOKS_DIR, hook);
        if (checkFileExists(filePath, `Hook ${hook}`)) {
            passed++;
            
            // Analisa o arquivo
            const analysis = analyzeJSFile(filePath, hook);
            if (analysis) {
                log(`  📊 ${hook}: ${analysis.totalLines} linhas, ${analysis.hooks.length} hooks React`);
                
                if (analysis.errors.length > 0) {
                    log(`  ⚠️  ${analysis.errors.length} possíveis problemas encontrados`, 'warning');
                }
            }
        }
    });
    
    return { passed, total: criticalHooks.length };
}

function testServices() {
    log('\n🔧 Testando serviços...', 'info');
    
    const criticalServices = [
        'api.ts',
        'apiService.ts'
    ];
    
    let passed = 0;
    
    criticalServices.forEach(service => {
        const filePath = path.join(SERVICES_DIR, service);
        if (checkFileExists(filePath, `Serviço ${service}`)) {
            passed++;
            
            // Analisa o arquivo
            const analysis = analyzeJSFile(filePath, service);
            if (analysis) {
                log(`  📊 ${service}: ${analysis.totalLines} linhas, ${analysis.functions.length} funções`);
                
                if (analysis.errors.length > 0) {
                    log(`  ⚠️  ${analysis.errors.length} possíveis problemas encontrados`, 'warning');
                }
            }
        }
    });
    
    return { passed, total: criticalServices.length };
}

function testPackageJson() {
    log('\n📦 Testando package.json...', 'info');
    
    const packagePath = path.join(FRONTEND_DIR, 'package.json');
    
    if (!checkFileExists(packagePath, 'package.json')) {
        return false;
    }
    
    try {
        const packageContent = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        
        // Verifica dependências críticas
        const criticalDeps = ['react', 'react-dom', 'typescript', 'vite'];
        const missingDeps = criticalDeps.filter(dep => 
            !packageContent.dependencies?.[dep] && !packageContent.devDependencies?.[dep]
        );
        
        if (missingDeps.length === 0) {
            log('Todas as dependências críticas estão presentes', 'success');
        } else {
            log(`Dependências ausentes: ${missingDeps.join(', ')}`, 'warning');
        }
        
        // Verifica scripts
        const criticalScripts = ['dev', 'build', 'preview'];
        const missingScripts = criticalScripts.filter(script => !packageContent.scripts?.[script]);
        
        if (missingScripts.length === 0) {
            log('Todos os scripts críticos estão presentes', 'success');
        } else {
            log(`Scripts ausentes: ${missingScripts.join(', ')}`, 'warning');
        }
        
        return missingDeps.length === 0 && missingScripts.length === 0;
        
    } catch (error) {
        log(`Erro ao analisar package.json: ${error.message}`, 'error');
        return false;
    }
}

function testBuildProcess() {
    log('\n🔨 Testando processo de build...', 'info');
    
    try {
        // Muda para o diretório do frontend
        process.chdir(FRONTEND_DIR);
        
        log('Executando npm run build...', 'info');
        const output = execSync('npm run build', { 
            encoding: 'utf8',
            timeout: 120000 // 2 minutos
        });
        
        if (output.includes('built in') || output.includes('Build completed')) {
            log('Build executado com sucesso', 'success');
            
            // Verifica se a pasta dist foi criada
            const distPath = path.join(FRONTEND_DIR, 'dist');
            if (fs.existsSync(distPath)) {
                const distFiles = fs.readdirSync(distPath);
                log(`Pasta dist criada com ${distFiles.length} arquivos`, 'success');
                return true;
            } else {
                log('Pasta dist não foi criada', 'warning');
                return false;
            }
        } else {
            log('Build pode ter falhado', 'warning');
            return false;
        }
        
    } catch (error) {
        log(`Erro no build: ${error.message}`, 'error');
        return false;
    }
}

function testTypeScript() {
    log('\n📝 Testando TypeScript...', 'info');
    
    try {
        process.chdir(FRONTEND_DIR);
        
        log('Executando verificação de tipos...', 'info');
        const output = execSync('npx tsc --noEmit', { 
            encoding: 'utf8',
            timeout: 60000 // 1 minuto
        });
        
        if (output.trim() === '') {
            log('Verificação de tipos passou sem erros', 'success');
            return true;
        } else {
            log(`Erros de tipo encontrados:\n${output}`, 'warning');
            return false;
        }
        
    } catch (error) {
        if (error.stdout && error.stdout.includes('error TS')) {
            log(`Erros de TypeScript encontrados:\n${error.stdout}`, 'warning');
        } else {
            log(`Erro na verificação de tipos: ${error.message}`, 'error');
        }
        return false;
    }
}

function main() {
    const args = process.argv.slice(2);
    const componentFilter = args.includes('--component') ? 
        args[args.indexOf('--component') + 1] : null;
    
    log('🚀 Testando componentes do frontend do GLPI Dashboard', 'info');
    log(`Timestamp: ${new Date().toISOString()}`, 'info');
    
    if (!fs.existsSync(FRONTEND_DIR)) {
        log(`Diretório do frontend não encontrado: ${FRONTEND_DIR}`, 'error');
        process.exit(1);
    }
    
    let totalTests = 0;
    let passedTests = 0;
    
    // Teste 1: Estrutura de componentes
    const componentResults = testComponentStructure();
    totalTests += componentResults.total;
    passedTests += componentResults.passed;
    
    // Teste 2: Hooks
    const hookResults = testHooks();
    totalTests += hookResults.total;
    passedTests += hookResults.passed;
    
    // Teste 3: Serviços
    const serviceResults = testServices();
    totalTests += serviceResults.total;
    passedTests += serviceResults.passed;
    
    // Teste 4: package.json
    if (testPackageJson()) {
        passedTests++;
    }
    totalTests++;
    
    // Teste 5: Build process
    if (testBuildProcess()) {
        passedTests++;
    }
    totalTests++;
    
    // Teste 6: TypeScript
    if (testTypeScript()) {
        passedTests++;
    }
    totalTests++;
    
    // Resumo
    log('\n📊 RESUMO DOS TESTES', 'info');
    log('='.repeat(50), 'info');
    log(`🎯 Resultado Final: ${passedTests}/${totalTests} testes passaram`, 'info');
    
    if (passedTests === totalTests) {
        log('🎉 Todos os testes passaram! Frontend está funcionando corretamente.', 'success');
        process.exit(0);
    } else {
        log('⚠️  Alguns testes falharam. Verifique os logs acima.', 'warning');
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    testComponentStructure,
    testHooks,
    testServices,
    testPackageJson,
    testBuildProcess,
    testTypeScript
};