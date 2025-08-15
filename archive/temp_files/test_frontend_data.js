/**
 * Script de teste para verificar se os dados estão sendo carregados no frontend
 * Execute este script no console do navegador (F12 -> Console)
 */

// Função para testar a API diretamente do frontend
async function testFrontendAPI() {
    console.log('🚀 Iniciando testes de integração Frontend...');
    
    try {
        // Testar fetch direto para métricas
        console.log('\n📊 Testando fetch direto para /api/metrics...');
        const metricsResponse = await fetch('http://localhost:5000/api/metrics');
        const metricsData = await metricsResponse.json();
        
        console.log('✅ Resposta da API de métricas:', metricsData);
        
        if (metricsData.success && metricsData.data) {
            console.log('✅ Dados de métricas válidos');
            console.log('📊 Níveis disponíveis:', Object.keys(metricsData.data.niveis || {}));
        } else {
            console.error('❌ Dados de métricas inválidos');
        }
        
        // Testar se o serviço de API do frontend está funcionando
        console.log('\n🔧 Testando serviço de API do frontend...');
        
        // Verificar se o módulo de API está disponível
        if (window.apiService) {
            console.log('✅ Serviço de API encontrado no window');
            
            try {
                const frontendMetrics = await window.apiService.getMetrics();
                console.log('✅ Métricas via serviço frontend:', frontendMetrics);
            } catch (error) {
                console.error('❌ Erro ao buscar métricas via serviço frontend:', error);
            }
        } else {
            console.log('⚠️ Serviço de API não encontrado no window');
        }
        
        // Verificar estado do React (se disponível)
        console.log('\n⚛️ Verificando estado do React...');
        
        // Tentar encontrar componentes React na página
        const reactRoot = document.querySelector('#root');
        if (reactRoot && reactRoot._reactInternalFiber) {
            console.log('✅ Aplicação React encontrada');
        } else if (reactRoot && reactRoot._reactInternals) {
            console.log('✅ Aplicação React encontrada (React 17+)');
        } else {
            console.log('⚠️ Aplicação React não encontrada ou não carregada');
        }
        
        // Verificar se há erros no console
        console.log('\n🔍 Verificando erros no console...');
        
        // Interceptar erros futuros
        const originalError = console.error;
        const errors = [];
        
        console.error = function(...args) {
            errors.push(args);
            originalError.apply(console, args);
        };
        
        setTimeout(() => {
            console.error = originalError;
            if (errors.length > 0) {
                console.log('❌ Erros encontrados:', errors);
            } else {
                console.log('✅ Nenhum erro novo encontrado');
            }
        }, 2000);
        
        // Verificar elementos DOM específicos
        console.log('\n🎯 Verificando elementos DOM específicos...');
        
        const dashboardElements = {
            'Métricas Gerais': '.metrics-card, [data-testid="metrics-card"], .dashboard-metrics',
            'Cards de Nível': '.level-card, [data-testid="level-card"], .nivel-card',
            'Ranking de Técnicos': '.technician-ranking, [data-testid="technician-ranking"], .ranking-card',
            'Gráficos': '.chart, [data-testid="chart"], canvas, svg'
        };
        
        for (const [name, selector] of Object.entries(dashboardElements)) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`✅ ${name}: ${elements.length} elemento(s) encontrado(s)`);
                
                // Verificar se os elementos têm conteúdo
                elements.forEach((el, index) => {
                    const hasText = el.textContent && el.textContent.trim().length > 0;
                    const hasChildren = el.children.length > 0;
                    
                    if (hasText || hasChildren) {
                        console.log(`  ✅ Elemento ${index + 1} tem conteúdo`);
                    } else {
                        console.log(`  ⚠️ Elemento ${index + 1} está vazio`);
                    }
                });
            } else {
                console.log(`❌ ${name}: Nenhum elemento encontrado`);
            }
        }
        
        // Verificar localStorage e sessionStorage
        console.log('\n💾 Verificando armazenamento local...');
        
        const storageKeys = Object.keys(localStorage);
        if (storageKeys.length > 0) {
            console.log('✅ LocalStorage tem dados:', storageKeys);
        } else {
            console.log('⚠️ LocalStorage está vazio');
        }
        
        // Verificar se há dados em cache
        const cacheKeys = storageKeys.filter(key => key.includes('cache') || key.includes('metrics'));
        if (cacheKeys.length > 0) {
            console.log('✅ Dados em cache encontrados:', cacheKeys);
            cacheKeys.forEach(key => {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    console.log(`  📊 ${key}:`, data);
                } catch (e) {
                    console.log(`  ⚠️ ${key}: Não é JSON válido`);
                }
            });
        } else {
            console.log('⚠️ Nenhum dado em cache encontrado');
        }
        
    } catch (error) {
        console.error('❌ Erro durante os testes:', error);
    }
}

// Função para verificar problemas de CORS
function testCORS() {
    console.log('\n🌐 Testando CORS...');
    
    fetch('http://localhost:5000/api/metrics', {
        method: 'GET',
        mode: 'cors'
    })
    .then(response => {
        console.log('✅ CORS funcionando, status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('✅ Dados recebidos via CORS:', data);
    })
    .catch(error => {
        console.error('❌ Erro de CORS:', error);
    });
}

// Função para verificar network requests
function monitorNetworkRequests() {
    console.log('\n🌐 Monitorando requisições de rede...');
    
    // Interceptar fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('🌐 Fetch request:', args[0]);
        
        return originalFetch.apply(this, args)
            .then(response => {
                console.log('✅ Fetch response:', args[0], 'Status:', response.status);
                return response;
            })
            .catch(error => {
                console.error('❌ Fetch error:', args[0], error);
                throw error;
            });
    };
    
    // Interceptar XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;
        
        xhr.open = function(method, url, ...args) {
            console.log('🌐 XHR request:', method, url);
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        xhr.addEventListener('load', function() {
            console.log('✅ XHR response:', this.responseURL, 'Status:', this.status);
        });
        
        xhr.addEventListener('error', function() {
            console.error('❌ XHR error:', this.responseURL);
        });
        
        return xhr;
    };
    
    console.log('✅ Monitoramento de rede ativado');
}

// Executar todos os testes
console.log('🔧 Para executar os testes, use os seguintes comandos:');
console.log('testFrontendAPI() - Testa a integração da API');
console.log('testCORS() - Testa problemas de CORS');
console.log('monitorNetworkRequests() - Monitora requisições de rede');

// Auto-executar teste básico
testFrontendAPI();