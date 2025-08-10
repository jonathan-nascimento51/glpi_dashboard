#!/usr/bin/env node

/**
 * Script para verificar drift da API usando orval
 * Este script verifica se a API mudou sem atualização do cliente
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const GENERATED_API_DIR = path.join(__dirname, '..', 'src', 'api', 'generated');
const TEMP_DIR = path.join(__dirname, '..', 'temp-api-check');

function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = type === 'error' ? '' : type === 'success' ? '' : 'ℹ';
  console.log(`${prefix} [${timestamp}] ${message}`);
}

function cleanup() {
  if (fs.existsSync(TEMP_DIR)) {
    fs.rmSync(TEMP_DIR, { recursive: true, force: true });
  }
}

function backupCurrentGenerated() {
  if (fs.existsSync(GENERATED_API_DIR)) {
    log('Fazendo backup dos arquivos gerados atuais...');
    fs.cpSync(GENERATED_API_DIR, TEMP_DIR, { recursive: true });
    return true;
  }
  return false;
}

function generateNewApi() {
  log('Gerando nova versão da API...');
  try {
    execSync('npm run generate:api', { 
      stdio: 'pipe',
      cwd: path.join(__dirname, '..')
    });
    return true;
  } catch (error) {
    log(`Erro ao gerar API: ${error.message}`, 'error');
    return false;
  }
}

function compareDirectories(dir1, dir2) {
  if (!fs.existsSync(dir1) || !fs.existsSync(dir2)) {
    return false;
  }

  const files1 = getAllFiles(dir1);
  const files2 = getAllFiles(dir2);

  if (files1.length !== files2.length) {
    return false;
  }

  for (const file of files1) {
    const relativePath = path.relative(dir1, file);
    const correspondingFile = path.join(dir2, relativePath);
    
    if (!fs.existsSync(correspondingFile)) {
      return false;
    }

    const content1 = fs.readFileSync(file, 'utf8');
    const content2 = fs.readFileSync(correspondingFile, 'utf8');
    
    if (content1 !== content2) {
      log(`Diferença detectada em: ${relativePath}`, 'error');
      return false;
    }
  }

  return true;
}

function getAllFiles(dir) {
  const files = [];
  
  function traverse(currentDir) {
    const items = fs.readdirSync(currentDir);
    
    for (const item of items) {
      const fullPath = path.join(currentDir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        traverse(fullPath);
      } else {
        files.push(fullPath);
      }
    }
  }
  
  traverse(dir);
  return files;
}

function restoreBackup() {
  if (fs.existsSync(TEMP_DIR)) {
    log('Restaurando backup dos arquivos originais...');
    if (fs.existsSync(GENERATED_API_DIR)) {
      fs.rmSync(GENERATED_API_DIR, { recursive: true, force: true });
    }
    fs.cpSync(TEMP_DIR, GENERATED_API_DIR, { recursive: true });
  }
}

function main() {
  log(' Iniciando verificação de drift da API...');
  
  try {
    const hasBackup = backupCurrentGenerated();
    
    if (!hasBackup) {
      log('Nenhum arquivo gerado encontrado. Gerando pela primeira vez...', 'info');
      if (generateNewApi()) {
        log('API gerada com sucesso!', 'success');
        process.exit(0);
      } else {
        log('Falha ao gerar API', 'error');
        process.exit(1);
      }
    }

    if (!generateNewApi()) {
      restoreBackup();
      cleanup();
      process.exit(1);
    }

    const isIdentical = compareDirectories(TEMP_DIR, GENERATED_API_DIR);
    
    if (isIdentical) {
      log(' Nenhum drift detectado! A API está sincronizada.', 'success');
      restoreBackup();
      cleanup();
      process.exit(0);
    } else {
      log(' DRIFT DETECTADO! A API mudou sem atualização do cliente.', 'error');
      log('', 'error');
      log('As seguintes ações são necessárias:', 'error');
      log('1. Revisar as mudanças na API', 'error');
      log('2. Atualizar o código do cliente conforme necessário', 'error');
      log('3. Executar "npm run generate:api" para atualizar os tipos', 'error');
      log('4. Testar a aplicação com as mudanças', 'error');
      
      cleanup();
      process.exit(1);
    }
  } catch (error) {
    log(`Erro inesperado: ${error.message}`, 'error');
    restoreBackup();
    cleanup();
    process.exit(1);
  }
}

process.on('SIGINT', () => {
  log('Processo interrompido. Limpando...', 'info');
  restoreBackup();
  cleanup();
  process.exit(1);
});

if (require.main === module) {
  main();
}

module.exports = { main, compareDirectories };
