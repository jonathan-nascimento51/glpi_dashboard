// Script para verificar se há erros no console do frontend
// Execute este código no console do navegador (F12)

console.log('=== VERIFICANDO ESTADO DO FRONTEND ===');

// Verificar se há dados de técnicos carregados
if (window.localStorage) {
  console.log('LocalStorage keys:', Object.keys(localStorage));
  
  // Limpar cache do localStorage se existir
  const keysToRemove = Object.keys(localStorage).filter(key => 
    key.includes('technician') || key.includes('ranking') || key.includes('cache')
  );
  
  if (keysToRemove.length > 0) {
    console.log('Removendo chaves de cache:', keysToRemove);
    keysToRemove.forEach(key => localStorage.removeItem(key));
    console.log('Cache limpo! Recarregue a página.');
  } else {
    console.log('Nenhum cache encontrado no localStorage');
  }
}

// Verificar se há dados no sessionStorage
if (window.sessionStorage) {
  console.log('SessionStorage keys:', Object.keys(sessionStorage));
  
  const sessionKeysToRemove = Object.keys(sessionStorage).filter(key => 
    key.includes('technician') || key.includes('ranking') || key.includes('cache')
  );
  
  if (sessionKeysToRemove.length > 0) {
    console.log('Removendo chaves de cache do sessionStorage:', sessionKeysToRemove);
    sessionKeysToRemove.forEach(key => sessionStorage.removeItem(key));
    console.log('SessionStorage limpo!');
  }
}

// Forçar reload da página para garantir que os dados sejam recarregados
console.log('Recarregando página em 2 segundos...');
setTimeout(() => {
  window.location.reload();
}, 2000);