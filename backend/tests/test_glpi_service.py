"""Unit tests for GLPI Service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from services.glpi_service import GLPIService
from utils.validators import ValidationError


class TestGLPIService:
    """Test cases for GLPIService class."""
    
    @pytest.fixture
    def glpi_service(self):
        """Create a GLPIService instance for testing."""
        with patch.dict('os.environ', {
            'GLPI_URL': 'http://test-glpi.com',
            'GLPI_USER_TOKEN': 'test_user_token',
            'GLPI_APP_TOKEN': 'test_app_token'
        }):
            return GLPIService()
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing."""
        return Mock(spec=requests.Session)
    
    def test_init_with_environment_variables(self):
        """Test GLPIService initialization with environment variables."""
        with patch.dict('os.environ', {
            'GLPI_URL': 'http://test-glpi.com',
            'GLPI_USER_TOKEN': 'test_user_token',
            'GLPI_APP_TOKEN': 'test_app_token'
        }):
            service = GLPIService()
            assert service.base_url == 'http://test-glpi.com/apirest.php'
            assert service.user_token == 'test_user_token'
            assert service.app_token == 'test_app_token'
    
    def test_init_missing_environment_variables(self):
        """Test GLPIService initialization with missing environment variables."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GLPI_URL environment variable is required"):
                GLPIService()
    
    @pytest.mark.unit
    def test_authenticate_success(self, glpi_service, mock_session):
        """Test successful authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'session_token': 'test_session_token'}
        mock_session.get.return_value = mock_response
        
        glpi_service.session = mock_session
        result = glpi_service._authenticate()
        
        assert result is True
        assert glpi_service.session_token == 'test_session_token'
        mock_session.get.assert_called_once()
    
    @pytest.mark.unit
    def test_authenticate_failure(self, glpi_service, mock_session):
        """Test authentication failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_session.get.return_value = mock_response
        
        glpi_service.session = mock_session
        result = glpi_service._authenticate()
        
        assert result is False
        assert glpi_service.session_token is None
    
    @pytest.mark.unit
    def test_authenticate_network_error(self, glpi_service, mock_session):
        """Test authentication with network error."""
        mock_session.get.side_effect = ConnectionError("Network error")
        glpi_service.session = mock_session
        
        result = glpi_service._authenticate()
        
        assert result is False
        assert glpi_service.session_token is None
    
    @pytest.mark.unit
    def test_validate_date_filters_valid(self, glpi_service):
        """Test date filter validation with valid dates."""
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        
        # Should not raise any exception
        glpi_service._validate_date_filters(start_date, end_date)
    
    @pytest.mark.unit
    def test_validate_date_filters_invalid_format(self, glpi_service):
        """Test date filter validation with invalid format."""
        start_date = '01/01/2024'  # Invalid format
        end_date = '2024-01-31'
        
        with pytest.raises(ValidationError, match="Invalid date format"):
            glpi_service._validate_date_filters(start_date, end_date)
    
    @pytest.mark.unit
    def test_validate_date_filters_end_before_start(self, glpi_service):
        """Test date filter validation with end date before start date."""
        start_date = '2024-01-31'
        end_date = '2024-01-01'
        
        with pytest.raises(ValidationError, match="End date must be after start date"):
            glpi_service._validate_date_filters(start_date, end_date)
    
    @pytest.mark.unit
    def test_validate_date_filters_too_large_range(self, glpi_service):
        """Test date filter validation with too large date range."""
        start_date = '2022-01-01'
        end_date = '2024-12-31'  # More than 2 years
        
        with pytest.raises(ValidationError, match="Date range cannot exceed 2 years"):
            glpi_service._validate_date_filters(start_date, end_date)
    
    @pytest.mark.unit
    @patch('services.glpi_service.GLPIService._authenticate')
    def test_get_tickets_success(self, mock_auth, glpi_service, mock_session):
        """Test successful ticket retrieval."""
        mock_auth.return_value = True
        glpi_service.session_token = 'test_session_token'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Test Ticket',
                'status': 2,
                'priority': 3,
                'date': '2024-01-01 10:00:00',
                'date_mod': '2024-01-01 11:00:00'
            }
        ]
        mock_session.get.return_value = mock_response
        glpi_service.session = mock_session
        
        result = glpi_service.get_tickets('2024-01-01', '2024-01-31')
        
        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['name'] == 'Test Ticket'
    
    @pytest.mark.unit
    @patch('services.glpi_service.GLPIService._authenticate')
    def test_get_tickets_authentication_failure(self, mock_auth, glpi_service):
        """Test ticket retrieval with authentication failure."""
        mock_auth.return_value = False
        
        with pytest.raises(Exception, match="Failed to authenticate with GLPI"):
            glpi_service.get_tickets('2024-01-01', '2024-01-31')
    
    @pytest.mark.unit
    @patch('services.glpi_service.GLPIService._authenticate')
    def test_get_tickets_api_error(self, mock_auth, glpi_service, mock_session):
        """Test ticket retrieval with API error."""
        mock_auth.return_value = True
        glpi_service.session_token = 'test_session_token'
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_session.get.return_value = mock_response
        glpi_service.session = mock_session
        
        with pytest.raises(Exception, match="GLPI API error"):
            glpi_service.get_tickets('2024-01-01', '2024-01-31')
    
    @pytest.mark.unit
    @patch('services.glpi_service.GLPIService._authenticate')
    def test_get_tickets_timeout(self, mock_auth, glpi_service, mock_session):
        """Test ticket retrieval with timeout."""
        mock_auth.return_value = True
        glpi_service.session_token = 'test_session_token'
        
        mock_session.get.side_effect = Timeout("Request timeout")
        glpi_service.session = mock_session
        
        with pytest.raises(Exception, match="Request timeout"):
            glpi_service.get_tickets('2024-01-01', '2024-01-31')
    
    @pytest.mark.unit
    def test_calculate_metrics_empty_tickets(self, glpi_service):
        """Test metrics calculation with empty ticket list."""
        tickets = []
        
        metrics = glpi_service._calculate_metrics(tickets)
        
        assert metrics['total_tickets'] == 0
        assert metrics['open_tickets'] == 0
        assert metrics['closed_tickets'] == 0
        assert metrics['pending_tickets'] == 0
        assert metrics['avg_resolution_time'] == 0
    
    @pytest.mark.unit
    def test_calculate_metrics_with_tickets(self, glpi_service):
        """Test metrics calculation with sample tickets."""
        tickets = [
            {
                'id': 1,
                'status': 2,  # Open
                'priority': 3,
                'date': '2024-01-01 10:00:00',
                'date_mod': '2024-01-01 11:00:00'
            },
            {
                'id': 2,
                'status': 5,  # Closed
                'priority': 4,
                'date': '2024-01-01 12:00:00',
                'date_mod': '2024-01-01 14:00:00'
            },
            {
                'id': 3,
                'status': 4,  # Pending
                'priority': 2,
                'date': '2024-01-01 15:00:00',
                'date_mod': '2024-01-01 16:00:00'
            }
        ]
        
        metrics = glpi_service._calculate_metrics(tickets)
        
        assert metrics['total_tickets'] == 3
        assert metrics['open_tickets'] == 1
        assert metrics['closed_tickets'] == 1
        assert metrics['pending_tickets'] == 1
    
    @pytest.mark.regression
    @patch('services.glpi_service.GLPIService._authenticate')
    def test_get_dashboard_metrics_regression(self, mock_auth, glpi_service, mock_session):
        """Regression test for get_dashboard_metrics method."""
        # This test ensures that the main dashboard metrics method
        # continues to work as expected after changes
        mock_auth.return_value = True
        glpi_service.session_token = 'test_session_token'
        
        # Mock tickets response
        mock_tickets_response = Mock()
        mock_tickets_response.status_code = 200
        mock_tickets_response.json.return_value = [
            {
                'id': 1,
                'name': 'Test Ticket',
                'status': 2,
                'priority': 3,
                'date': '2024-01-01 10:00:00',
                'date_mod': '2024-01-01 11:00:00'
            }
        ]
        
        # Mock users response
        mock_users_response = Mock()
        mock_users_response.status_code = 200
        mock_users_response.json.return_value = [
            {
                'id': 1,
                'name': 'Test User',
                'realname': 'Test',
                'firstname': 'User'
            }
        ]
        
        mock_session.get.side_effect = [mock_tickets_response, mock_users_response]
        glpi_service.session = mock_session
        
        result = glpi_service.get_dashboard_metrics('2024-01-01', '2024-01-31')
        
        # Verify the structure of the returned metrics
        assert 'total_tickets' in result
        assert 'open_tickets' in result
        assert 'closed_tickets' in result
        assert 'pending_tickets' in result
        assert 'technician_ranking' in result
        assert 'system_status' in result
        
        # Verify data types
        assert isinstance(result['total_tickets'], int)
        assert isinstance(result['open_tickets'], int)
        assert isinstance(result['closed_tickets'], int)
        assert isinstance(result['pending_tickets'], int)
        assert isinstance(result['technician_ranking'], list)
        assert isinstance(result['system_status'], dict)
    
    @pytest.mark.unit
    def test_cache_functionality(self, glpi_service):
        """Test that caching works correctly."""
        # Test cache key generation
        cache_key = glpi_service._generate_cache_key('2024-01-01', '2024-01-31')
        assert isinstance(cache_key, str)
        assert '2024-01-01' in cache_key
        assert '2024-01-31' in cache_key
        
        # Test cache storage and retrieval
        test_data = {'test': 'data'}
        glpi_service._set_cache(cache_key, test_data)
        cached_data = glpi_service._get_cache(cache_key)
        
        assert cached_data == test_data
    
    @pytest.mark.unit
    def test_session_management(self, glpi_service):
        """Test session management and cleanup."""
        # Test session initialization
        assert glpi_service.session is not None
        assert isinstance(glpi_service.session, requests.Session)
        
        # Test session cleanup
        glpi_service._cleanup_session()
        # After cleanup, session should be reset for next use
        assert glpi_service.session_token is None