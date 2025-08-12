// Script de debug para testar a API diretamente
const API_BASE_URL = 'http://127.0.0.1:8000';

async function testAPI() {
  console.log(' Testando API do GLPI Dashboard...');
  
  try {
    // Teste 1: Endpoint /v1/kpis
    console.log('\n Testando /v1/kpis...');
    const kpisResponse = await fetch(`${API_BASE_URL}/v1/kpis`);
    const kpisData = await kpisResponse.json();
    console.log('Status:', kpisResponse.status);
    console.log('Dados KPIs:', JSON.stringify(kpisData, null, 2));
    
    // Teste 2: Endpoint /v1/system/status
    console.log('\n Testando /v1/system/status...');
    const statusResponse = await fetch(`${API_BASE_URL}/v1/system/status`);
    const statusData = await statusResponse.json();
    console.log('Status:', statusResponse.status);
    console.log('Status do Sistema:', JSON.stringify(statusData, null, 2));
    
    // Teste 3: Endpoint /v1/technicians/ranking
    console.log('\n Testando /v1/technicians/ranking...');
    const rankingResponse = await fetch(`${API_BASE_URL}/v1/technicians/ranking`);
    const rankingData = await rankingResponse.json();
    console.log('Status:', rankingResponse.status);
    console.log('Ranking:', JSON.stringify(rankingData, null, 2));
    
    // Teste 4: Endpoint /v1/tickets/new
    console.log('\n Testando /v1/tickets/new...');
    const ticketsResponse = await fetch(`${API_BASE_URL}/v1/tickets/new`);
    const ticketsData = await ticketsResponse.json();
    console.log('Status:', ticketsResponse.status);
    console.log('Tickets Novos:', JSON.stringify(ticketsData, null, 2));
    
  } catch (error) {
    console.error(' Erro ao testar API:', error);
  }
}

// Executar o teste
testAPI();
