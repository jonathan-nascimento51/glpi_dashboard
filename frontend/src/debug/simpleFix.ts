// Script simples para diagnosticar e corrigir o problema do ranking

// Função para limpar todos os caches
function clearAllCaches() {
  // Limpar localStorage
  const keys = Object.keys(localStorage);
  keys.forEach(key => {
    if (key.includes('dashboard') || key.includes('ranking') || key.includes('cache')) {
      localStorage.removeItem(key);
    }
  });
  
  // Limpar sessionStorage
  const sessionKeys = Object.keys(sessionStorage);
  sessionKeys.forEach(key => {
    if (key.includes('dashboard') || key.includes('ranking') || key.includes('cache')) {
      sessionStorage.removeItem(key);
    }
  });
  
  console.log('✅ Todos os caches foram limpos');
}

// Função para testar a API diretamente
async function testRankingAPI() {
  try {
    console.log('🔍 Testando API de ranking...');
    
    const response = await fetch('/api/technicians/ranking', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('✅ Resposta da API:', data);
    
    if (Array.isArray(data) && data.length > 0) {
      console.log(`✅ API retornou ${data.length} técnicos`);
      return data;
    } else {
      console.warn('⚠️ API retornou array vazio ou dados inválidos');
      return [];
    }
  } catch (error) {
    console.error('❌ Erro ao testar API:', error);
    return null;
  }
}

// Função para forçar reload da página sem cache
function forceReload() {
  console.log('🔄 Forçando reload da página...');
  window.location.reload();
}

// Função para diagnóstico completo
async function fullDiagnostic() {
  console.log('🔍 Iniciando diagnóstico completo...');
  
  // 1. Limpar caches
  clearAllCaches();
  
  // 2. Testar API
  const apiData = await testRankingAPI();
  
  // 3. Verificar se há dados
  if (apiData && apiData.length > 0) {
    console.log('✅ API está funcionando corretamente');
    console.log('🔄 Recarregando página para aplicar correções...');
    setTimeout(() => {
      forceReload();
    }, 2000);
  } else {
    console.error('❌ Problema na API ou backend');
    console.log('💡 Verifique se o backend está rodando');
  }
}

// Exportar funções para o console global
(window as any).clearAllCaches = clearAllCaches;
(window as any).testRankingAPI = testRankingAPI;
(window as any).forceReload = forceReload;
(window as any).fullDiagnostic = fullDiagnostic;

console.log('🛠️ Ferramentas de diagnóstico carregadas:');
console.log('- clearAllCaches() - Limpa todos os caches');
console.log('- testRankingAPI() - Testa a API diretamente');
console.log('- forceReload() - Força reload da página');
console.log('- fullDiagnostic() - Executa diagnóstico completo');

export {};