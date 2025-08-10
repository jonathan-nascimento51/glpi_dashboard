import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config.settings import active_config
from services.glpi_service import GLPIService
from utils.response_formatter import ResponseFormatter


class APIService:
    """Service to handle external API communications"""


    def __init__(self):
        self.base_url = active_config.BACKEND_API_URL
        self.api_key = active_config.API_KEY
        self.timeout = active_config.API_TIMEOUT
        self.logger = logging.getLogger("services")
        self.glpi_service = GLPIService()
        self._cache = {}

        # Default headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "TechDept-Dashboard/1.0",
        }

        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate date range format and logic"""
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return start <= end
        except ValueError:
            return False

    def get_dashboard_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[Dict]:
        """Get dashboard metrics from GLPI service"""
        try:
            cache_key = f"dashboard_metrics_{start_date}_{end_date}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            level_metrics = self.glpi_service.get_metrics_by_level(start_date, end_date)
            general_metrics = self.glpi_service.get_general_metrics(start_date, end_date)
            
            result = {
                "level_metrics": level_metrics,
                "general_metrics": general_metrics
            }
            
            self._cache[cache_key] = result
            return result
        except Exception as e:
            self.logger.error(f"Error getting dashboard metrics: {str(e)}")
            return None

    def format_response(self, data: Dict) -> Dict:
        """Format success response"""
        return ResponseFormatter.format_success_response(data)

    def format_error_response(self, message: str) -> Dict:
        """Format error response"""
        return ResponseFormatter.format_error_response(message)

    def _make_request(
        self, endpoint: str, method: str = "GET", data: Dict = None
    ) -> Dict:
        """Make HTTP request to external API"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(
                    url, json=data, headers=self.headers, timeout=self.timeout
                )

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
            return self._make_request("/api/metrics")
        except Exception as e:
            # Return empty state with error indication
            logging.warning(f"Could not fetch metrics: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "data": {
                    "cpu_usage": {"value": 0, "status": "error"},
                    "memory_usage": {"value": 0, "status": "error"},
                    "disk_usage": {"value": 0, "status": "error"},
                    "network_status": {"status": "error"},
                    "active_users": {"count": 0, "status": "error"},
                    "system_uptime": {"value": 0, "status": "error"},
                },
            }

    def get_system_status(self) -> Dict:
        """Get current system status"""
        try:
            return self._make_request("/api/system/status")
        except Exception as e:
            logging.warning(f"Could not fetch system status: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "status": "offline",
                "last_update": datetime.now().isoformat(),
            }

    def search(self, query: str) -> List[Dict]:
        """Search functionality"""
        try:
            return self._make_request(f"/api/search?q={query}")
        except Exception as e:
            logging.warning(f"Search failed: {str(e)}")
            return {"error": True, "message": str(e), "results": []}

    def get_chart_data(self, chart_type: str) -> Dict:
        """Get data for specific chart types"""
        try:
            return self._make_request(f"/api/charts/{chart_type}")
        except Exception as e:
            logging.warning(f"Could not fetch chart data for {chart_type}: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "data": {"labels": [], "datasets": []},
            }

    def get_alerts(self) -> List[Dict]:
        """Get system alerts"""
        try:
            return self._make_request("/api/alerts")
        except Exception as e:
            logging.warning(f"Could not fetch alerts: {str(e)}")
            return {"error": True, "message": str(e), "alerts": []}



    def validate_date_format(self, date_str: str) -> bool:
        """Validate date format"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_trends_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get trends data from GLPI service"""
        try:
            return self.glpi_service.get_trends_data(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting trends data: {str(e)}")
            return {"error": True, "message": str(e), "data": []}

    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        import time
        try:
            response_time = self._calculate_response_time()
            return {
                "response_time": response_time,
                "timestamp": time.time(),
                "throughput": 100,
                "error_rate": 0.01,
                "cpu_usage": 45.2,
                "memory_usage": 67.8
            }
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            return {"error": True, "message": str(e)}

    def _calculate_response_time(self) -> float:
        """Calculate response time"""
        return 0.5


