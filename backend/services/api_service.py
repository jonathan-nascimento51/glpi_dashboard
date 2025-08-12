import requests
import logging
from typing import Dict, List, Any
from datetime import datetime
from backend.config.settings import active_config

class APIService:
    """Service to handle external API communications"""
    
    def __init__(self):
        config_obj = active_config()
        self.base_url = config_obj.BACKEND_API_URL
        self.api_key = config_obj.API_KEY
        self.timeout = config_obj.API_TIMEOUT
        self.logger = logging.getLogger('services')
        
        # Default headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TechDept-Dashboard/1.0'
        }
        
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make HTTP request to external API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout error for {url}")
            raise Exception("Timeout na conexão com a API")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error for {url}")
            raise Exception("Erro de conexão com a API")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error {e.response.status_code} for {url}")
            raise Exception(f"Erro HTTP {e.response.status_code}")
        except Exception as e:
            self.logger.error(f"Unexpected error for {url}: {str(e)}")
            raise Exception("Erro inesperado na API")
    
    def get_metrics(self) -> Dict:
        """Get dashboard metrics from external API"""
        try:
            return self._make_request('/api/metrics')
        except Exception as e:
            # Return empty state with error indication
            logging.warning(f"Could not fetch metrics: {str(e)}")
            return {
                'error': True,
                'message': str(e),
                'data': {
                    'cpu_usage': {'value': 0, 'status': 'error'},
                    'memory_usage': {'value': 0, 'status': 'error'},
                    'disk_usage': {'value': 0, 'status': 'error'},
                    'network_status': {'status': 'error'},
                    'active_users': {'count': 0, 'status': 'error'},
                    'system_uptime': {'value': 0, 'status': 'error'}
                }
            }
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        try:
            return self._make_request('/api/system/status')
        except Exception as e:
            logging.warning(f"Could not fetch system status: {str(e)}")
            return {
                'error': True,
                'message': str(e),
                'status': 'offline',
                'last_update': datetime.now().isoformat()
            }
    
    def search(self, query: str) -> List[Dict]:
        """Search functionality"""
        try:
            return self._make_request(f'/api/search?q={query}')
        except Exception as e:
            logging.warning(f"Search failed: {str(e)}")
            return {
                'error': True,
                'message': str(e),
                'results': []
            }
    
    def get_chart_data(self, chart_type: str) -> Dict:
        """Get data for specific chart types"""
        try:
            return self._make_request(f'/api/charts/{chart_type}')
        except Exception as e:
            logging.warning(f"Could not fetch chart data for {chart_type}: {str(e)}")
            return {
                'error': True,
                'message': str(e),
                'data': {
                    'labels': [],
                    'datasets': []
                }
            }
    
    def get_alerts(self) -> List[Dict]:
        """Get system alerts"""
        try:
            return self._make_request('/api/alerts')
        except Exception as e:
            logging.warning(f"Could not fetch alerts: {str(e)}")
            return {
                'error': True,
                'message': str(e),
                'alerts': []
            }
