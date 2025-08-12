// Script para debug do frontend - execute no console do navegador

// Função para testar a API diretamente
async function testAPI() {
    console.log('🔍 Testando API diretamente...');
    
    try {
        const response = await fetch('http://localhost:5000/api/metrics');
        const data = await response.json();
        console.log('✅ API Response:', data);
        return data;
    } catch (error) {
        console.error('❌ Erro na API:', error);
        return null;
    }
}

// Função para verificar se o React está carregado
function checkReact() {
    console.log('🔍 Verificando React...');
    
    if (window.React) {
        console.log('✅ React encontrado:', window.React.version);
    } else {
        console.log('❌ React não encontrado');
    }
    
    // Verificar se há elementos React
    const reactRoot = document.querySelector('#root');
    if (reactRoot) {
        console.log('✅ Root element encontrado');
        console.log('Conteúdo:', reactRoot.innerHTML.substring(0, 200) + '...');
    } else {
        console.log('❌ Root element não encontrado');
    }
}

// Função para verificar erros no console
function checkConsoleErrors() {
    console.log('🔍 Verificando erros no console...');
    
    // Interceptar console.error
    const originalError = console.error;
    const errors = [];
    
    console.error = function(...args) {
        errors.push(args);
        originalError.apply(console, args);
    };
    
    setTimeout(() => {
        console.log('📊 Erros capturados:', errors.length);
        errors.forEach((error, index) => {
            console.log(`Erro ${index + 1}:`, error);
        });
    }, 2000);
}

// Função para verificar o estado do dashboard
function checkDashboardState() {
    console.log('🔍 Verificando estado do dashboard...');
    
    // Procurar por elementos específicos do dashboard
    const metrics = document.querySelectorAll('[data-testid*="metric"], .metric, .dashboard-metric');
    console.log('📊 Elementos de métricas encontrados:', metrics.length);
    
    const loading = document.querySelectorAll('.loading, [data-testid="loading"]');
    console.log('⏳ Elementos de loading encontrados:', loading.length);
    
    const errors = document.querySelectorAll('.error, [data-testid="error"]');
    console.log('❌ Elementos de erro encontrados:', errors.length);
    
    // Verificar texto visível
    const bodyText = document.body.innerText;
    if (bodyText.includes('Dashboard')) {
        console.log('✅ Texto "Dashboard" encontrado na página');
    }
    if (bodyText.includes('Carregando') || bodyText.includes('Loading')) {
        console.log('⏳ Texto de carregamento encontrado');
    }
    if (bodyText.includes('Erro') || bodyText.includes('Error')) {
        console.log('❌ Texto de erro encontrado');
    }
}

// Função para verificar network requests
function monitorRequests() {
    console.log('🔍 Monitorando requisições...');
    
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('🌐 Fetch:', args[0]);
        return originalFetch.apply(this, args)
            .then(response => {
                console.log('✅ Response:', args[0], response.status);
                return response;
            })
            .catch(error => {
                console.error('❌ Fetch Error:', args[0], error);
                throw error;
            });
    };
}

// Executar todos os testes
console.log('🚀 Iniciando debug do frontend...');
checkReact();
checkConsoleErrors();
checkDashboardState();
monitorRequests();
testAPI();

console.log('\n📋 Para executar testes individuais:');
console.log('testAPI() - Testa a API');
console.log('checkReact() - Verifica React');
console.log('checkDashboardState() - Verifica estado do dashboard');