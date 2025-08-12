// Script para testar todos os endpoints da API
const axios = require('axios');

const BASE_URL = 'http://localhost:3000/api/v1';

const endpoints = [
  '/kpis',
  '/system/status',
  '/technicians/ranking',
  '/tickets/new?limit=5'
];

async function testEndpoint(endpoint) {
  try {
    console.log(`\n🧪 Testando: ${endpoint}`);
    const response = await axios.get(`${BASE_URL}${endpoint}`);
    console.log(`✅ Status: ${response.status}`);
    console.log(`✅ Success: ${response.data.success}`);
    console.log(`✅ Data keys: ${Object.keys(response.data.data || {}).join(', ')}`);
    return true;
  } catch (error) {
    console.log(`❌ Erro: ${error.message}`);
    if (error.response) {
      console.log(`❌ Status: ${error.response.status}`);
      console.log(`❌ Data: ${JSON.stringify(error.response.data)}`);
    }
    return false;
  }
}

async function testAllEndpoints() {
  console.log('🚀 Iniciando testes dos endpoints da API...');
  
  let successCount = 0;
  
  for (const endpoint of endpoints) {
    const success = await testEndpoint(endpoint);
    if (success) successCount++;
  }
  
  console.log(`\n📊 Resultado: ${successCount}/${endpoints.length} endpoints funcionando`);
  
  if (successCount === endpoints.length) {
    console.log('🎉 Todos os endpoints estão funcionando corretamente!');
  } else {
    console.log('⚠️ Alguns endpoints apresentaram problemas.');
  }
}

testAllEndpoints().catch(console.error);