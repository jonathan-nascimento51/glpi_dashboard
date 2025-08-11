// Service Worker para cache de recursos e melhoria de performance
const CACHE_NAME = 'glpi-dashboard-v1';
const STATIC_CACHE = 'static-v1';
const API_CACHE = 'api-v1';

// Recursos para cache estático
const STATIC_RESOURCES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico'
];

// URLs da API para cache
const API_URLS = [
  '/api/metrics',
  '/api/system-status',
  '/api/technicians/ranking'
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker instalando...');
  
  event.waitUntil(
    Promise.all([
      // Cache de recursos estáticos
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Cacheando recursos estáticos');
        return cache.addAll(STATIC_RESOURCES);
      }),
      // Cache da API
      caches.open(API_CACHE).then((cache) => {
        console.log('🔄 Preparando cache da API');
        return Promise.resolve();
      })
    ]).then(() => {
      console.log('✅ Service Worker instalado com sucesso');
      return self.skipWaiting();
    })
  );
});

// Ativar Service Worker
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker ativando...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Limpar caches antigos
          if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
            console.log('🗑️ Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ Service Worker ativado');
      return self.clients.claim();
    })
  );
});

// Interceptar requisições
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégia para recursos estáticos: Cache First
  if (request.method === 'GET' && STATIC_RESOURCES.some(resource => url.pathname.endsWith(resource))) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          console.log('📦 Servindo do cache estático:', url.pathname);
          return cachedResponse;
        }
        
        return fetch(request).then((response) => {
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
    return;
  }
  
  // Estratégia para API: Network First com fallback para cache
  if (request.method === 'GET' && url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Se a resposta for bem-sucedida, cachear
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(API_CACHE).then((cache) => {
              // Cache com TTL de 30 segundos
              const headers = new Headers(responseClone.headers);
              headers.set('sw-cached-at', Date.now().toString());
              const cachedResponse = new Response(responseClone.body, {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers: headers
              });
              cache.put(request, cachedResponse);
            });
          }
          return response;
        })
        .catch(() => {
          // Se a rede falhar, tentar cache
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              const cachedAt = cachedResponse.headers.get('sw-cached-at');
              const now = Date.now();
              const cacheAge = now - parseInt(cachedAt || '0');
              
              // Se o cache tem menos de 5 minutos, usar
              if (cacheAge < 300000) {
                console.log('📱 Servindo da API cache (offline):', url.pathname);
                return cachedResponse;
              }
            }
            
            // Retornar resposta de erro padrão
            return new Response(
              JSON.stringify({ 
                error: 'Dados não disponíveis offline',
                cached: false 
              }),
              {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
        })
    );
    return;
  }
  
  // Para outras requisições, usar estratégia padrão
  event.respondWith(fetch(request));
});

// Limpar cache periodicamente
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName === API_CACHE) {
              console.log('🗑️ Limpando cache da API');
              return caches.delete(cacheName);
            }
          })
        );
      })
    );
  }
});

// Notificar sobre atualizações
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});