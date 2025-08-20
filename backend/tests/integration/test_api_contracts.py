"""Testes de validação de contratos da API contra especificação OpenAPI."""

import json
import os
import pytest
import requests
import yaml
from jsonschema import validate, ValidationError
from typing import Dict, Any


class TestAPIContracts:
    """Testes para validar se a API está em conformidade com a especificação OpenAPI."""
    
    @classmethod
    def setup_class(cls):
        """Configuração inicial dos testes."""
        cls.base_url = "http://localhost:5000/api"
        cls.openapi_spec = cls._load_openapi_spec()
        
    @classmethod
    def _load_openapi_spec(cls) -> Dict[str, Any]:
        """Carrega a especificação OpenAPI."""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "..", "docs", "api", "openapi.yaml"
        )
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_schema_for_endpoint(self, path: str, method: str, response_code: str) -> Dict[str, Any]:
        """Obtém o schema de resposta para um endpoint específico."""
        try:
            endpoint_spec = self.openapi_spec['paths'][path][method.lower()]
            response_spec = endpoint_spec['responses'][response_code]
            
            if 'content' in response_spec:
                content_type = 'application/json'
                if content_type in response_spec['content']:
                    schema_ref = response_spec['content'][content_type]['schema']
                    
                    # Resolve referência de schema
                    if '$ref' in schema_ref:
                        ref_path = schema_ref['$ref'].split('/')[-1]
                        return self.openapi_spec['components']['schemas'][ref_path]
                    else:
                        return schema_ref
            
            return {}
        except KeyError:
            return {}
    
    def _validate_response_schema(self, response_data: Dict[str, Any], schema: Dict[str, Any]):
        """Valida se a resposta está em conformidade com o schema."""
        if not schema:
            return  # Sem schema para validar
            
        try:
            validate(instance=response_data, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Resposta não está em conformidade com o schema: {e.message}")
    
    def test_metrics_endpoint_contract(self):
        """Testa se o endpoint /metrics está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/metrics")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/metrics', 'GET', '200')
        self._validate_response_schema(response_data, schema)
        
        # Validações específicas do endpoint
        data = response_data['data']
        assert 'novos' in data, "Campo 'novos' deve estar presente"
        assert 'pendentes' in data, "Campo 'pendentes' deve estar presente"
        assert 'progresso' in data, "Campo 'progresso' deve estar presente"
        assert 'resolvidos' in data, "Campo 'resolvidos' deve estar presente"
        assert 'total' in data, "Campo 'total' deve estar presente"
        assert 'niveis' in data, "Campo 'niveis' deve estar presente"
        assert 'tendencias' in data, "Campo 'tendencias' deve estar presente"
        
        # Valida estrutura dos níveis
        niveis = data['niveis']
        for nivel in ['n1', 'n2', 'n3', 'n4']:
            assert nivel in niveis, f"Nível '{nivel}' deve estar presente"
            nivel_data = niveis[nivel]
            for campo in ['novos', 'pendentes', 'progresso', 'resolvidos']:
                assert campo in nivel_data, f"Campo '{campo}' deve estar presente no nível '{nivel}'"
    
    def test_metrics_filtered_endpoint_contract(self):
        """Testa se o endpoint /metrics/filtered está em conformidade com o contrato."""
        params = {
            'data_inicio': '2024-01-01',
            'data_fim': '2024-01-31',
            'tipo_filtro': 'creation'
        }
        
        response = requests.get(f"{self.base_url}/metrics/filtered", params=params)
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/metrics/filtered', 'GET', '200')
        self._validate_response_schema(response_data, schema)
        
        # Validações específicas do endpoint filtrado
        assert 'data' in response_data, "Campo 'data' deve estar presente"
        data = response_data['data']
        assert 'filters_applied' in data, "Campo 'filters_applied' deve estar presente em data"
        filters_applied = data['filters_applied']
        assert 'start_date' in filters_applied, "Campo 'start_date' deve estar presente em filters_applied"
        assert 'end_date' in filters_applied, "Campo 'end_date' deve estar presente em filters_applied"
    
    def test_technicians_ranking_endpoint_contract(self):
        """Testa se o endpoint /technicians/ranking está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/technicians/ranking")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/technicians/ranking', 'GET', '200')
        self._validate_response_schema(response_data, schema)
        
        # Validações específicas do ranking
        assert 'data' in response_data, "Campo 'data' deve estar presente"
        assert isinstance(response_data['data'], list), "Campo 'data' deve ser uma lista"
        assert 'correlation_id' in response_data, "Campo 'correlation_id' deve estar presente"
        assert 'filters_applied' in response_data, "Campo 'filters_applied' deve estar presente"
    
    def test_tickets_new_endpoint_contract(self):
        """Testa se o endpoint /tickets/new está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/tickets/new")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/tickets/new', 'GET', '200')
        self._validate_response_schema(response_data, schema)
    
    def test_alerts_endpoint_contract(self):
        """Testa se o endpoint /alerts está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/alerts")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/alerts', 'GET', '200')
        self._validate_response_schema(response_data, schema)
    
    def test_performance_stats_endpoint_contract(self):
        """Testa se o endpoint /performance/stats está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/performance/stats")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/performance/stats', 'GET', '200')
        self._validate_response_schema(response_data, schema)
    
    def test_status_endpoint_contract(self):
        """Testa se o endpoint /status está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/status")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/status', 'GET', '200')
        self._validate_response_schema(response_data, schema)
    
    def test_health_endpoint_contract(self):
        """Testa se o endpoint /health está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/health")
        
        # Verifica status code (pode ser 200 ou 503)
        assert response.status_code in [200, 503], f"Status code deve ser 200 ou 503, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/health', 'GET', str(response.status_code))
        self._validate_response_schema(response_data, schema)
    
    def test_filter_types_endpoint_contract(self):
        """Testa se o endpoint /filter-types está em conformidade com o contrato."""
        response = requests.get(f"{self.base_url}/filter-types")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert response.headers.get('content-type') == 'application/json', "Content-Type deve ser application/json"
        
        # Valida schema da resposta
        response_data = response.json()
        schema = self._get_schema_for_endpoint('/filter-types', 'GET', '200')
        self._validate_response_schema(response_data, schema)
        
        # Validações específicas dos tipos de filtro
        assert 'data' in response_data, "Campo 'data' deve estar presente"
        filter_types = response_data['data']
        assert isinstance(filter_types, dict), "Campo 'data' deve ser um objeto"
        
        # Verifica se os tipos de filtro esperados estão presentes
        expected_types = ['creation', 'modification', 'current_status']
        for filter_type in expected_types:
            assert filter_type in filter_types, f"Tipo de filtro '{filter_type}' deve estar presente"
            # Verifica estrutura de cada tipo de filtro
            filter_obj = filter_types[filter_type]
            assert 'name' in filter_obj, f"Campo 'name' deve estar presente em '{filter_type}'"
            assert 'description' in filter_obj, f"Campo 'description' deve estar presente em '{filter_type}'"
            assert 'default' in filter_obj, f"Campo 'default' deve estar presente em '{filter_type}'"
    
    def test_openapi_spec_endpoint(self):
        """Testa se o endpoint /openapi.yaml está acessível."""
        response = requests.get(f"{self.base_url}/openapi.yaml")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert 'yaml' in response.headers.get('content-type', '').lower(), "Content-Type deve ser YAML"
        
        # Verifica se o conteúdo é YAML válido
        try:
            yaml.safe_load(response.text)
        except yaml.YAMLError:
            pytest.fail("Resposta não é um YAML válido")
    
    def test_swagger_ui_endpoint(self):
        """Testa se o endpoint /docs (Swagger UI) está acessível."""
        response = requests.get(f"{self.base_url}/docs")
        
        # Verifica status code
        assert response.status_code == 200, f"Status code esperado: 200, recebido: {response.status_code}"
        
        # Verifica content-type
        assert 'html' in response.headers.get('content-type', '').lower(), "Content-Type deve ser HTML"
        
        # Verifica se contém elementos do Swagger UI
        content = response.text
        assert 'swagger-ui' in content, "Página deve conter elementos do Swagger UI"
        assert 'SwaggerUIBundle' in content, "Página deve carregar o SwaggerUIBundle"
    
    def test_error_responses_contract(self):
        """Testa se as respostas de erro estão em conformidade com o contrato."""
        # Testa endpoint inexistente (404)
        response = requests.get(f"{self.base_url}/nonexistent")
        assert response.status_code == 404, "Endpoint inexistente deve retornar 404"
        
        # Testa parâmetros inválidos (400)
        response = requests.get(f"{self.base_url}/metrics/filtered?start_date=invalid-date")
        assert response.status_code == 400, "Parâmetros inválidos devem retornar 400"
        
        # Verifica se as respostas de erro têm content-type JSON
        assert response.headers.get('content-type') == 'application/json', "Respostas de erro devem ser JSON"
    
    def test_cors_headers(self):
        """Testa se os cabeçalhos CORS estão configurados corretamente."""
        response = requests.get(f"{self.base_url}/metrics")
        
        # Verifica cabeçalhos CORS
        assert 'Access-Control-Allow-Origin' in response.headers, "Cabeçalho CORS deve estar presente"
    
    def test_response_time_performance(self):
        """Testa se os tempos de resposta estão dentro dos limites aceitáveis."""
        import time
        
        endpoints = [
            '/api/metrics',
            '/api/technicians/ranking',
            '/api/tickets/new',
            '/api/alerts',
            '/api/status',
            '/api/health'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Verifica se o tempo de resposta é aceitável (< 5 segundos)
            assert response_time < 5.0, f"Endpoint {endpoint} demorou {response_time:.2f}s (limite: 5s)"
            
            # Para endpoints críticos, tempo deve ser ainda menor
            if endpoint in ['/health', '/status']:
                assert response_time < 2.0, f"Endpoint crítico {endpoint} demorou {response_time:.2f}s (limite: 2s)"