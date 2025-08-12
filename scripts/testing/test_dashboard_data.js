// Script para testar se o dashboard está carregando dados corretamente
const axios = require('axios');

const FRONTEND_URL = 'http://localhost:3000';

async function testDashboardData() {
  console.log('🎯 Testando carregamento de dados do dashboard...');
  
  try {
    // Testar se o frontend está respondendo
    console.log('\n1. Testando se o frontend está ativo...');
    const frontendResponse = await axios.get(FRONTEND_URL, { timeout: 5000 });
    console.log('✅ Frontend está ativo');
    
    // Testar cada endpoint que o dashboard usa
    const endpoints = [
      { name: 'KPIs', url: '/api/v1/kpis' },
      { name: 'Status do Sistema', url: '/api/v1/system/status' },
      { name: 'Ranking de Técnicos', url: '/api/v1/technicians/ranking' },
      { name: 'Novos Tickets', url: '/api/v1/tickets/new?limit=6' }
    ];
    
    console.log('\n2. Testando endpoints através do proxy do frontend...');
    
    for (const endpoint of endpoints) {
      try {
        console.log(`\n🔍 Testando ${endpoint.name}...`);
        const response = await axios.get(`${FRONTEND_URL}${endpoint.url}`, { timeout: 10000 });
        
        console.log(`✅ Status: ${response.status}`);
        console.log(`✅ Success: ${response.data.success}`);
        
        if (endpoint.name === 'KPIs' && response.data.data) {
          const data = response.data.data;
          console.log(`✅ Dados KPI encontrados:`);
          if (data.niveis) {
            console.log(`   - Níveis: ${Object.keys(data.niveis).join(', ')}`);
            Object.entries(data.niveis).forEach(([nivel, dados]) => {
              if (dados && typeof dados === 'object') {
                console.log(`   - ${nivel}: novos=${dados.novos}, progresso=${dados.progresso}, pendentes=${dados.pendentes}, resolvidos=${dados.resolvidos}`);
              }
            });
          }
          if (data.tendencias) {
            console.log(`   - Tendências: ${Object.keys(data.tendencias).join(', ')}`);
          }
        }
        
        if (endpoint.name === 'Novos Tickets' && Array.isArray(response.data.data)) {
          console.log(`✅ ${response.data.data.length} tickets encontrados`);
        }
        
        if (endpoint.name === 'Ranking de Técnicos' && Array.isArray(response.data.data)) {
          console.log(`✅ ${response.data.data.length} técnicos no ranking`);
        }
        
      } catch (error) {
        console.log(`❌ Erro em ${endpoint.name}: ${error.message}`);
        if (error.code === 'ECONNABORTED') {
          console.log(`❌ Timeout - o endpoint pode estar lento`);
        }
      }
    }
    
    console.log('\n🎉 Teste do dashboard concluído!');
    
  } catch (error) {
    console.log(`❌ Erro geral: ${error.message}`);
  }
}

testDashboardData().catch(console.error);