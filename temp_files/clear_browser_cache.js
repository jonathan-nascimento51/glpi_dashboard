
// Execute este código no console do navegador (F12)
console.log('=== LIMPANDO CACHE DO FRONTEND ===');

// Limpar localStorage
if (window.localStorage) {
  const keysToRemove = Object.keys(localStorage).filter(key => 
    key.includes('technician') || key.includes('ranking') || key.includes('cache') || key.includes('metrics')
  );
  keysToRemove.forEach(key => localStorage.removeItem(key));
  console.log('LocalStorage limpo:', keysToRemove.length, 'chaves removidas');
}

// Limpar sessionStorage
if (window.sessionStorage) {
  const sessionKeysToRemove = Object.keys(sessionStorage).filter(key => 
    key.includes('technician') || key.includes('ranking') || key.includes('cache') || key.includes('metrics')
  );
  sessionKeysToRemove.forEach(key => sessionStorage.removeItem(key));
  console.log('SessionStorage limpo:', sessionKeysToRemove.length, 'chaves removidas');
}

// Limpar cache do sistema de cache personalizado (se existir)
if (window.debugCache) {
  window.debugCache.clear();
  console.log('Cache personalizado limpo');
}

// Forçar reload completo
console.log('Recarregando página...');
window.location.reload(true);
