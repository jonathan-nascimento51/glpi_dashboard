// Script de teste rápido para verificar o estado do ranking no console

// Função para verificar rapidamente o estado do ranking
function quickRankingCheck() {
  console.log('🔍 VERIFICAÇÃO RÁPIDA DO RANKING');
  console.log('=' .repeat(40));
  
  // 1. Verificar elementos no DOM
  const rankingElements = document.querySelectorAll('[class*="ranking"], [class*="technician"]');
  const technicianCards = document.querySelectorAll('[class*="technician-card"], [data-testid*="technician"]');
  
  console.log('📊 Elementos no DOM:');
  console.log(`  - Elementos com "ranking": ${rankingElements.length}`);
  console.log(`  - Cards de técnicos: ${technicianCards.length}`);
  
  // 2. Verificar se há dados visíveis
  const hasVisibleData = technicianCards.length > 0;
  console.log(`✅ Dados visíveis: ${hasVisibleData ? 'SIM' : 'NÃO'}`);
  
  // 3. Verificar loading states
  const loadingElements = document.querySelectorAll('[class*="loading"], [class*="spinner"], [class*="skeleton"]');
  console.log(`⏳ Elementos de loading: ${loadingElements.length}`);
  
  // 4. Verificar cache no localStorage
  let cacheData = null;
  let cacheKeys = [];
  
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && (key.includes('ranking') || key.includes('technician') || key.includes('dashboard'))) {
      cacheKeys.push(key);
      try {
        const data = localStorage.getItem(key);
        if (data) {
          const parsed = JSON.parse(data);
          if (Array.isArray(parsed) || (parsed.data && Array.isArray(parsed.data))) {
            cacheData = Array.isArray(parsed) ? parsed : parsed.data;
          }
        }
      } catch (e) {
        // Ignorar erros de parsing
      }
    }
  }
  
  console.log('💾 Cache localStorage:');
  console.log(`  - Chaves relacionadas: ${cacheKeys.length}`);
  console.log(`  - Dados em cache: ${cacheData ? cacheData.length : 0} itens`);
  
  if (cacheKeys.length > 0) {
    console.log(`  - Chaves: ${cacheKeys.join(', ')}`);
  }
  
  // 5. Verificar se a API responde
  testApiQuick();
  
  // 6. Verificar erros no console (últimos)
  const errors = getRecentErrors();
  if (errors.length > 0) {
    console.log('❌ Erros recentes:', errors);
  }
  
  // 7. Resumo
  console.log('\n📋 RESUMO:');
  if (hasVisibleData) {
    console.log('✅ Ranking está sendo exibido normalmente');
  } else if (loadingElements.length > 0) {
    console.log('⏳ Ranking está carregando...');
  } else if (cacheData && cacheData.length > 0) {
    console.log('⚠️ Dados existem no cache mas não estão sendo exibidos');
    console.log('💡 Possível problema de renderização do React');
  } else {
    console.log('❌ Nenhum dado encontrado - possível problema na API');
  }
  
  return {
    hasVisibleData,
    elementsCount: rankingElements.length,
    cardsCount: technicianCards.length,
    loadingCount: loadingElements.length,
    cacheData: cacheData?.length || 0,
    cacheKeys
  };
}

// Função para testar a API rapidamente
async function testApiQuick() {
  try {
    console.log('🌐 Testando API...');
    const response = await fetch('/api/technicians/ranking?limit=1');
    console.log(`  - Status: ${response.status}`);
    console.log(`  - OK: ${response.ok}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log(`  - Resposta: ${JSON.stringify(data).substring(0, 100)}...`);
    }
  } catch (error) {
    console.error('  - Erro na API:', error);
  }
}

// Função para capturar erros recentes (simulada)
function getRecentErrors() {
  // Em um cenário real, isso seria implementado com um interceptor de console.error
  // Por enquanto, retornamos array vazio
  return [];
}

// Função para forçar um refresh dos dados
async function forceRankingRefresh() {
  console.log('🔄 Forçando refresh do ranking...');
  
  // Limpar cache local
  for (let i = localStorage.length - 1; i >= 0; i--) {
    const key = localStorage.key(i);
    if (key && (key.includes('ranking') || key.includes('technician'))) {
      localStorage.removeItem(key);
      console.log(`🗑️ Cache removido: ${key}`);
    }
  }
  
  // Tentar acessar função de refresh global se disponível
  if ((window as any).forceRefresh) {
    console.log('🔄 Chamando forceRefresh global...');
    (window as any).forceRefresh();
  } else if ((window as any).loadData) {
    console.log('🔄 Chamando loadData global...');
    (window as any).loadData();
  } else {
    console.log('⚠️ Nenhuma função de refresh encontrada');
    console.log('💡 Tente recarregar a página manualmente');
  }
}

// Função para monitorar mudanças em tempo real
function watchRankingChanges(duration = 10000) {
  console.log(`👀 Monitorando mudanças por ${duration/1000} segundos...`);
  
  let lastState = quickRankingCheck();
  
  const interval = setInterval(() => {
    const currentState = quickRankingCheck();
    
    // Verificar se houve mudanças
    const changed = JSON.stringify(lastState) !== JSON.stringify(currentState);
    
    if (changed) {
      console.log('🔄 MUDANÇA DETECTADA!');
      console.log('Antes:', lastState);
      console.log('Depois:', currentState);
    }
    
    lastState = currentState;
  }, 2000);
  
  setTimeout(() => {
    clearInterval(interval);
    console.log('⏹️ Monitoramento finalizado');
  }, duration);
  
  return interval;
}

// Expor funções no window para uso no console
if (typeof window !== 'undefined') {
  (window as any).quickRankingCheck = quickRankingCheck;
  (window as any).testApiQuick = testApiQuick;
  (window as any).forceRankingRefresh = forceRankingRefresh;
  (window as any).watchRankingChanges = watchRankingChanges;
  
  // Atalhos
  (window as any).qrc = quickRankingCheck;
  (window as any).frr = forceRankingRefresh;
  (window as any).wrc = watchRankingChanges;
}

export {
  quickRankingCheck,
  testApiQuick,
  forceRankingRefresh,
  watchRankingChanges
};