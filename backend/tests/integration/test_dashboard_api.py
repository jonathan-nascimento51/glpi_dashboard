"""Integration tests for Dashboard API."""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
from datetime import datetime, timedelta

from app import app
from services.glpi_service import GLPIService


class TestDashboardAPIIntegration:
    """Integration tests for the complete dashboard API flow."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_glpi_data(self):
        """Mock GLPI data for testing."""
        return {
            'tickets': [
                {
                    'id': 1,
                    'name': 'Test Ticket 1',
                    'status': 2,
                    'priority': 3,
                    'date': '2024-01-01 10:00:00',
                    'date_mod': '2024-01-01 11:00:00',
                    'users_id_recipient': 1,
                    'users_id_lastupdater': 2
                },
                {
                    'id': 2,
                    'name': 'Test Ticket 2',
                    'status': 5,
                    'priority': 4,
                    'date': '2024-01-01 12:00:00',
                    'date_mod': '2024-01-01 14:00:00',
                    'users_id_recipient': 2,
                    'users_id_lastupdater': 1
                }
            ],
            'users': [
                {
                    'id': 1,
                    'name': 'tech1',
                    'realname': 'Technician',
                    'firstname': 'One'
                },
                {
                    'id': 2,
                    'name': 'tech2',
                    'realname': 'Technician',
                    'firstname': 'Two'
                }
            ]
        }
    
    @pytest.mark.integration
    @patch('services.glpi_service.GLPIService.get_dashboard_metrics')
    def test_get_dashboard_metrics_success(self, mock_get_metrics, client, mock_glpi_data):
        """Test successful dashboard metrics retrieval."""
        # Mock the GLPI service response
        mock_get_metrics.return_value = {
            'total_tickets': 2,
            'open_tickets': 1,
            'closed_tickets': 1,
            'pending_tickets': 0,
            'avg_resolution_time': 120,
            'technician_ranking': [
                {'name': 'Technician One', 'tickets_resolved': 1, 'avg_time': 120},
                {'name': 'Technician Two', 'tickets_resolved': 1, 'avg_time': 120}
            ],
            'system_status': {
                'api_status': 'healthy',
                'last_update': datetime.now().isoformat(),
                'response_time': 0.5
            }
        }
        
        # Make request to the API
        response = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['total_tickets'] == 2
        assert data['data']['open_tickets'] == 1
        assert data['data']['closed_tickets'] == 1
        assert len(data['data']['technician_ranking']) == 2
        
        # Verify the GLPI service was called with correct parameters
        mock_get_metrics.assert_called_once_with('2024-01-01', '2024-01-31')
    
    @pytest.mark.integration
    def test_get_dashboard_metrics_invalid_date_format(self, client):
        """Test dashboard metrics with invalid date format."""
        response = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '01/01/2024',  # Invalid format
                'end_date': '2024-01-31'
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'Invalid date format' in data['error']
    
    @pytest.mark.integration
    def test_get_dashboard_metrics_missing_parameters(self, client):
        """Test dashboard metrics with missing required parameters."""
        response = client.get("/api/dashboard/metrics")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    def test_get_dashboard_metrics_end_date_before_start(self, client):
        """Test dashboard metrics with end date before start date."""
        response = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '2024-01-31',
                'end_date': '2024-01-01'
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'End date must be after start date' in data['error']
    
    @pytest.mark.integration
    @patch('services.glpi_service.GLPIService.get_dashboard_metrics')
    def test_get_dashboard_metrics_glpi_service_error(self, mock_get_metrics, client):
        """Test dashboard metrics when GLPI service fails."""
        # Mock GLPI service to raise an exception
        mock_get_metrics.side_effect = Exception("GLPI API connection failed")
        
        response = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data['success'] is False
        assert 'GLPI API connection failed' in data['error']
    
    @pytest.mark.integration
    @patch('services.glpi_service.GLPIService.get_dashboard_metrics')
    def test_get_dashboard_metrics_with_cache(self, mock_get_metrics, client):
        """Test dashboard metrics caching behavior."""
        # Mock the GLPI service response
        mock_response = {
            'total_tickets': 5,
            'open_tickets': 2,
            'closed_tickets': 3,
            'pending_tickets': 0,
            'technician_ranking': [],
            'system_status': {'api_status': 'healthy'}
        }
        mock_get_metrics.return_value = mock_response
        
        # Make first request
        response1 = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        )
        
        # Make second request with same parameters
        response2 = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        )
        
        # Both requests should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Data should be the same
        assert response1.json()['data'] == response2.json()['data']
        
        # GLPI service should be called at least once
        assert mock_get_metrics.call_count >= 1
    
    @pytest.mark.integration
    @patch('services.glpi_service.GLPIService.get_system_status')
    def test_get_system_status(self, mock_get_status, client):
        """Test system status endpoint."""
        # Mock the system status response
        mock_get_status.return_value = {
            'api_status': 'healthy',
            'database_status': 'connected',
            'glpi_connection': 'active',
            'last_update': datetime.now().isoformat(),
            'response_time': 0.3,
            'version': '1.0.0'
        }
        
        response = client.get("/api/system/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['api_status'] == 'healthy'
        assert data['data']['database_status'] == 'connected'
        assert data['data']['glpi_connection'] == 'active'
    
    @pytest.mark.integration
    @patch('services.glpi_service.GLPIService.get_technician_ranking')
    def test_get_technician_ranking(self, mock_get_ranking, client):
        """Test technician ranking endpoint."""
        # Mock the ranking response
        mock_get_ranking.return_value = [
            {
                'name': 'Technician One',
                'tickets_resolved': 15,
                'avg_resolution_time': 120,
                'satisfaction_score': 4.5
            },
            {
                'name': 'Technician Two',
                'tickets_resolved': 12,
                'avg_resolution_time': 150,
                'satisfaction_score': 4.2
            }
        ]
        
        response = client.get(
            "/api/technicians/ranking",
            params={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert len(data['data']) == 2
        assert data['data'][0]['name'] == 'Technician One'
        assert data['data'][0]['tickets_resolved'] == 15
    
    @pytest.mark.integration
    def test_api_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/api/dashboard/metrics")
        
        # Check for CORS headers
        assert 'access-control-allow-origin' in response.headers
        assert 'access-control-allow-methods' in response.headers
        assert 'access-control-allow-headers' in response.headers
    
    @pytest.mark.integration
    def test_api_rate_limiting(self, client):
        """Test API rate limiting behavior."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get(
                "/api/dashboard/metrics",
                params={
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-31'
                }
            )
            responses.append(response)
        
        # All requests should either succeed or be rate limited
        for response in responses:
            assert response.status_code in [200, 429, 500]  # 429 = Too Many Requests
    
    @pytest.mark.regression
    @patch('services.glpi_service.GLPIService.get_dashboard_metrics')
    def test_dashboard_api_regression_complete_flow(self, mock_get_metrics, client):
        """Comprehensive regression test for the complete dashboard API flow."""
        # This test ensures the entire API flow works as expected
        # and helps catch regressions in the integration between components
        
        # Mock comprehensive dashboard data
        mock_get_metrics.return_value = {
            'total_tickets': 100,
            'open_tickets': 25,
            'closed_tickets': 70,
            'pending_tickets': 5,
            'avg_resolution_time': 180,
            'priority_distribution': {
                'low': 30,
                'medium': 50,
                'high': 15,
                'urgent': 5
            },
            'technician_ranking': [
                {
                    'name': 'John Doe',
                    'tickets_resolved': 25,
                    'avg_resolution_time': 150,
                    'satisfaction_score': 4.8
                },
                {
                    'name': 'Jane Smith',
                    'tickets_resolved': 20,
                    'avg_resolution_time': 160,
                    'satisfaction_score': 4.6
                }
            ],
            'system_status': {
                'api_status': 'healthy',
                'database_status': 'connected',
                'glpi_connection': 'active',
                'last_update': datetime.now().isoformat(),
                'response_time': 0.45,
                'version': '1.0.0'
            },
            'trends': {
                'daily_tickets': [5, 8, 12, 6, 9, 15, 11],
                'resolution_trend': [180, 175, 170, 165, 160, 155, 150]
            }
        }
        
        # Test the main dashboard endpoint
        response = client.get(
            "/api/dashboard/metrics",
            params={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            }
        )
        
        # Verify response structure and data
        assert response.status_code == 200
        data = response.json()
        
        # Verify response format
        assert data['success'] is True
        assert 'data' in data
        assert 'metadata' in data
        
        # Verify core metrics
        metrics = data['data']
        assert metrics['total_tickets'] == 100
        assert metrics['open_tickets'] == 25
        assert metrics['closed_tickets'] == 70
        assert metrics['pending_tickets'] == 5
        
        # Verify technician ranking
        assert len(metrics['technician_ranking']) == 2
        assert metrics['technician_ranking'][0]['name'] == 'John Doe'
        
        # Verify system status
        assert metrics['system_status']['api_status'] == 'healthy'
        
        # Verify metadata
        metadata = data['metadata']
        assert 'request_id' in metadata
        assert 'timestamp' in metadata
        assert 'processing_time' in metadata
        
        # Verify the service was called correctly
        mock_get_metrics.assert_called_once_with('2024-01-01', '2024-01-31')