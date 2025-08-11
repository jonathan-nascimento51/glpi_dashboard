// Script para debugar problemas no frontend
// Execute este script no console do navegador

console.log('🔍 Iniciando debug do frontend...');

// 1. Verificar se a API está respondendo
async function testApiDirectly() {
    console.log('📡 Testando API diretamente...');
    try {
        const response = await fetch('http://localhost:5000/api/metrics');
        const data = await response.json();
        console.log('✅ Resposta da API:', data);
        return data;
    } catch (error) {
        console.error('❌ Erro na API:', error);
        return null;
    }
}

// 2. Verificar se o React está carregado
function checkReactLoaded() {
    console.log('⚛️ Verificando React...');
    if (window.React) {
        console.log('✅ React carregado:', window.React.version);
    } else {
        console.log('❌ React não encontrado');
    }
}

// 3. Verificar componentes do dashboard
function checkDashboardComponents() {
    console.log('🎛️ Verificando componentes do dashboard...');
    
    // Verificar se há elementos do dashboard
    const dashboardElements = document.querySelectorAll('[class*="dashboard"], [class*="metric"], [class*="card"]');
    console.log(`📊 Elementos do dashboard encontrados: ${dashboardElements.length}`);
    
    dashboardElements.forEach((el, index) => {
        console.log(`${index + 1}. ${el.tagName} - ${el.className}`);
    });
    
    // Verificar se há dados sendo exibidos
    const textContent = document.body.textContent;
    if (textContent.includes('Carregando') || textContent.includes('Loading')) {
        console.log('⏳ Estado de carregamento detectado');
    }
    if (textContent.includes('Erro') || textContent.includes('Error')) {
        console.log('❌ Estado de erro detectado');
    }
    if (textContent.includes('Nenhum dado') || textContent.includes('No data')) {
        console.log('📭 Estado de "sem dados" detectado');
    }
}

// 4. Verificar erros no console
function checkConsoleErrors() {
    console.log('🚨 Verificando erros no console...');
    
    // Interceptar erros futuros
    const originalError = console.error;
    console.error = function(...args) {
        console.log('🔴 ERRO CAPTURADO:', ...args);
        originalError.apply(console, args);
    };
    
    const originalWarn = console.warn;
    console.warn = function(...args) {
        console.log('🟡 AVISO CAPTURADO:', ...args);
        originalWarn.apply(console, args);
    };
}

// 5. Verificar requisições de rede
function monitorNetworkRequests() {
    console.log('🌐 Monitorando requisições de rede...');
    
    // Interceptar fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('📡 FETCH:', args[0]);
        return originalFetch.apply(this, args)
            .then(response => {
                console.log('✅ FETCH RESPONSE:', args[0], response.status);
                return response;
            })
            .catch(error => {
                console.error('❌ FETCH ERROR:', args[0], error);
                throw error;
            });
    };
    
    // Interceptar XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        xhr.open = function(method, url) {
            console.log('📡 XHR:', method, url);
            return originalOpen.apply(this, arguments);
        };
        return xhr;
    };
}

// 6. Verificar estado do Redux/Context (se aplicável)
function checkAppState() {
    console.log('🏪 Verificando estado da aplicação...');
    
    // Tentar encontrar o estado do React
    const reactRoot = document.querySelector('#root');
    if (reactRoot && reactRoot._reactInternalFiber) {
        console.log('⚛️ React Fiber encontrado');
    } else if (reactRoot && reactRoot._reactInternalInstance) {
        console.log('⚛️ React Instance encontrada');
    } else {
        console.log('❓ Estado do React não acessível');
    }
}

// 7. Função principal de debug
async function runFullDebug() {
    console.log('🚀 Executando debug completo...');
    
    checkReactLoaded();
    checkConsoleErrors();
    monitorNetworkRequests();
    checkAppState();
    checkDashboardComponents();
    
    const apiData = await testApiDirectly();
    
    console.log('📋 Resumo do debug:');
    console.log('- API funcionando:', !!apiData);
    console.log('- React carregado:', !!window.React);
    console.log('- Elementos dashboard:', document.querySelectorAll('[class*="dashboard"], [class*="metric"]').length);
    
    return {
        apiWorking: !!apiData,
        reactLoaded: !!window.React,
        dashboardElements: document.querySelectorAll('[class*="dashboard"], [class*="metric"]').length,
        apiData
    };
}

// Executar automaticamente
runFullDebug().then(result => {
    console.log('🎯 Resultado final do debug:', result);
});

// Disponibilizar funções globalmente para uso manual
window.debugFrontend = {
    testApi: testApiDirectly,
    checkReact: checkReactLoaded,
    checkComponents: checkDashboardComponents,
    checkErrors: checkConsoleErrors,
    monitorNetwork: monitorNetworkRequests,
    checkState: checkAppState,
    runFull: runFullDebug
};

console.log('✅ Debug frontend carregado! Use window.debugFrontend para acessar as funções.');