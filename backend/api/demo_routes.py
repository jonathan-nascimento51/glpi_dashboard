"""
Demo routes with mock data for performance benchmarking
Allows testing architecture performance without external GLPI dependency
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Blueprint, jsonify, request

from core.application.services.refactoring_integration import get_refactoring_integration_service
from utils.performance import monitor_performance
from utils.prometheus_metrics import monitor_api_endpoint

demo_bp = Blueprint("demo", __name__, url_prefix="/api/demo")

# Mock data generators
def generate_mock_metrics_data(start_date: Optional[str] = None, end_date: Optional[str] = None, architecture_type: str = "generic") -> Dict[str, Any]:
    """Generate realistic mock metrics data with consistent processing time."""
    
    # Fair processing time - identical for both architectures
    time.sleep(0.010)  # 10ms consistent processing time
    
    base_metrics = {
        "total_tickets": 1247,
        "new_tickets": 89,
        "in_progress_tickets": 156,
        "resolved_tickets": 923,
        "pending_tickets": 79,
        "hierarchy_breakdown": {
            "N1": {"total": 512, "resolved": 445, "avg_resolution_time": 2.3},
            "N2": {"total": 387, "resolved": 298, "avg_resolution_time": 4.7}, 
            "N3": {"total": 234, "resolved": 156, "avg_resolution_time": 8.2},
            "N4": {"total": 114, "resolved": 24, "avg_resolution_time": 15.6}
        },
        "priority_breakdown": {
            "1_very_low": 125,
            "2_low": 456, 
            "3_medium": 487,
            "4_high": 156,
            "5_very_high": 23
        },
        "technician_stats": {
            "active_technicians": 24,
            "avg_tickets_per_technician": 52,
            "top_performers": [
                {"id": 101, "name": "João Silva", "resolved": 89, "avg_time": 2.1},
                {"id": 102, "name": "Maria Santos", "resolved": 76, "avg_time": 2.8},
                {"id": 103, "name": "Pedro Costa", "resolved": 65, "avg_time": 3.2}
            ]
        },
        "response_times": {
            "avg_first_response": 0.8,
            "avg_resolution": 4.2,
            "sla_compliance": 0.89
        },
        "date_range": {
            "start_date": start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": end_date or datetime.now().strftime('%Y-%m-%d')
        },
        "cached": False,
        "generated_at": datetime.now().isoformat(),
        "architecture": "mock_data",
        "processing_time_ms": 10
    }
    
    return base_metrics

def generate_mock_technician_ranking(limit: int = 10) -> List[Dict[str, Any]]:
    """Generate mock technician ranking data with consistent processing time."""
    
    # Fair processing time - identical for both architectures
    time.sleep(0.008)  # 8ms consistent processing time
    
    mock_technicians = [
        {"id": 101, "name": "João Silva", "resolved": 89, "avg_time": 2.1, "satisfaction": 4.8},
        {"id": 102, "name": "Maria Santos", "resolved": 76, "avg_time": 2.8, "satisfaction": 4.6},
        {"id": 103, "name": "Pedro Costa", "resolved": 65, "avg_time": 3.2, "satisfaction": 4.5},
        {"id": 104, "name": "Ana Oliveira", "resolved": 58, "avg_time": 3.8, "satisfaction": 4.3},
        {"id": 105, "name": "Carlos Ferreira", "resolved": 52, "avg_time": 4.1, "satisfaction": 4.2},
        {"id": 106, "name": "Lucia Mendes", "resolved": 47, "avg_time": 4.5, "satisfaction": 4.0},
        {"id": 107, "name": "Roberto Lima", "resolved": 43, "avg_time": 4.8, "satisfaction": 3.9},
        {"id": 108, "name": "Fernanda Rocha", "resolved": 39, "avg_time": 5.2, "satisfaction": 3.8},
        {"id": 109, "name": "Miguel Torres", "resolved": 35, "avg_time": 5.6, "satisfaction": 3.7},
        {"id": 110, "name": "Beatriz Alves", "resolved": 31, "avg_time": 6.0, "satisfaction": 3.6}
    ]
    
    return mock_technicians[:limit]

# Legacy-style demo endpoint
@demo_bp.route("/metrics/legacy")
@monitor_api_endpoint("demo_metrics_legacy") 
@monitor_performance
def demo_metrics_legacy():
    """Demo endpoint simulating legacy GLPIService architecture."""
    start_time = time.time()
    
    # Extract parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Fair simulation - same base processing for both architectures
    # No artificial overhead bias
    
    # Generate mock data
    metrics_data = generate_mock_metrics_data(start_date, end_date, "legacy")
    
    # Add legacy-specific metadata
    metrics_data["architecture"] = "legacy_simulation"
    metrics_data["service_type"] = "GLPIService"
    metrics_data["processing_layers"] = ["route", "service", "glpi_api", "cache"]
    metrics_data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return jsonify(metrics_data)

# New architecture demo endpoint 
@demo_bp.route("/metrics/new")
@monitor_api_endpoint("demo_metrics_new")
@monitor_performance
def demo_metrics_new():
    """Demo endpoint using new Clean Architecture via MetricsFacade."""
    start_time = time.time()
    
    # Extract parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # Fair simulation - same base processing for both architectures
        # Let real architecture differences show naturally
        
        # Get service through new architecture
        service = get_refactoring_integration_service().get_service()
        
        # Generate mock data (in real scenario this would come from facade)
        metrics_data = generate_mock_metrics_data(start_date, end_date, "new")
        
        # Add new architecture metadata
        metrics_data["architecture"] = "new_clean_architecture"
        metrics_data["service_type"] = "MetricsFacade"
        metrics_data["processing_layers"] = ["route", "facade", "query", "adapter", "cache"]
        metrics_data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        metrics_data["optimizations"] = ["unified_cache", "async_processing", "dto_validation"]
        
        return jsonify(metrics_data)
        
    except Exception as e:
        # Fallback response
        return jsonify({
            "error": f"New architecture error: {str(e)}",
            "architecture": "new_clean_architecture_error",
            "fallback": True
        }), 500

# Legacy technician ranking demo
@demo_bp.route("/technicians/ranking/legacy")
@monitor_api_endpoint("demo_ranking_legacy")
@monitor_performance
def demo_technician_ranking_legacy():
    """Demo technician ranking with legacy architecture simulation."""
    start_time = time.time()
    
    limit = int(request.args.get('limit', 10))
    
    # Fair simulation - same base processing for both architectures
    
    ranking_data = generate_mock_technician_ranking(limit)
    
    response = {
        "success": True,
        "ranking": ranking_data,
        "total_technicians": len(ranking_data),
        "architecture": "legacy_simulation",
        "service_type": "GLPIService",
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "cached": False
    }
    
    return jsonify(response)

# New architecture technician ranking demo
@demo_bp.route("/technicians/ranking/new") 
@monitor_api_endpoint("demo_ranking_new")
@monitor_performance
def demo_technician_ranking_new():
    """Demo technician ranking with new Clean Architecture."""
    start_time = time.time()
    
    limit = int(request.args.get('limit', 10))
    
    # Fair simulation - same base processing for both architectures
    
    ranking_data = generate_mock_technician_ranking(limit)
    
    response = {
        "success": True,
        "ranking": ranking_data, 
        "total_technicians": len(ranking_data),
        "architecture": "new_clean_architecture",
        "service_type": "MetricsFacade",
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "optimizations": ["query_optimization", "cached_results", "async_processing"],
        "cached": False
    }
    
    return jsonify(response)

# System status demo
@demo_bp.route("/status")
@monitor_api_endpoint("demo_status")
@monitor_performance
def demo_status():
    """Demo system status endpoint."""
    return jsonify({
        "status": "online",
        "mode": "demo",
        "backend_status": "running",
        "architecture": "clean_architecture_demo",
        "available_endpoints": [
            "/api/demo/metrics/legacy",
            "/api/demo/metrics/new", 
            "/api/demo/technicians/ranking/legacy",
            "/api/demo/technicians/ranking/new",
            "/api/demo/status"
        ],
        "timestamp": datetime.now().isoformat()
    })

# Stress test endpoint
@demo_bp.route("/stress/<int:delay_ms>")
@monitor_api_endpoint("demo_stress")
@monitor_performance
def demo_stress_test(delay_ms: int):
    """Demo endpoint for stress testing with configurable delay."""
    start_time = time.time()
    
    # Configurable delay to simulate different processing loads
    delay_seconds = min(delay_ms / 1000.0, 1.0)  # Max 1 second
    time.sleep(delay_seconds)
    
    return jsonify({
        "requested_delay_ms": delay_ms,
        "actual_delay_ms": delay_seconds * 1000,
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "timestamp": datetime.now().isoformat(),
        "mode": "stress_test"
    })