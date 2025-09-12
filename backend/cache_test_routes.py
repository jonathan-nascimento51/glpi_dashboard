"""
Cache test routes for validating UnifiedCache effectiveness
Tests real Redis cache behavior with hit/miss scenarios
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Blueprint, jsonify, request

from core.infrastructure.cache.unified_cache import UnifiedCache
from utils.performance import monitor_performance
from utils.prometheus_metrics import monitor_api_endpoint

cache_test_bp = Blueprint("cache_test", __name__, url_prefix="/api/cache-test")

# Initialize cache for testing
cache = UnifiedCache()

def generate_expensive_computation(complexity: int = 100) -> Dict[str, Any]:
    """Simulate expensive computation that benefits from caching."""
    start_time = time.time()
    
    # Simulate expensive operations
    result = 0
    for i in range(complexity * 1000):
        result += i ** 0.5
    
    # Simulate database/API calls
    time.sleep(0.020)  # 20ms of "external" calls
    
    computation_time = time.time() - start_time
    
    return {
        "computation_result": result,
        "complexity": complexity,
        "computation_time_ms": computation_time * 1000,
        "expensive_data": {
            "metrics": [{"id": i, "value": i * 2.5} for i in range(50)],
            "aggregations": {
                "total": result,
                "avg": result / (complexity * 1000) if complexity > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
        }
    }

@cache_test_bp.route("/expensive/legacy")
@monitor_api_endpoint("cache_test_legacy")
@monitor_performance
def expensive_computation_legacy():
    """Legacy endpoint - no caching (always computes)."""
    start_time = time.time()
    
    complexity = int(request.args.get('complexity', 100))
    
    # Always compute - no cache
    data = generate_expensive_computation(complexity)
    
    response = {
        "success": True,
        "cached": False,
        "cache_strategy": "none",
        "architecture": "legacy_no_cache",
        "data": data,
        "response_time_ms": (time.time() - start_time) * 1000,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@cache_test_bp.route("/expensive/cached")
@monitor_api_endpoint("cache_test_cached")
@monitor_performance  
def expensive_computation_cached():
    """New architecture endpoint - with UnifiedCache."""
    start_time = time.time()
    
    complexity = int(request.args.get('complexity', 100))
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    # Create cache key
    cache_key = f"expensive_computation:complexity:{complexity}"
    
    data = None
    cached = False
    
    if not force_refresh:
        # Try to get from cache first
        cached_data = cache.get("expensive_computation", {"complexity": complexity})
        if cached_data:
            data = cached_data
            cached = True
    
    if data is None:
        # Cache miss - compute expensive data
        data = generate_expensive_computation(complexity)
        
        # Store in cache (UnifiedCache manages TTL internally)
        cache.set("expensive_computation", {"complexity": complexity}, data)
        # Important: this is a cache miss, so cached should be False
        cached = False
    
    response = {
        "success": True,
        "cached": cached,
        "cache_strategy": "redis_unified_cache",
        "cache_namespace": "expensive_computation",
        "cache_params": {"complexity": complexity},
        "architecture": "new_with_cache",
        "data": data,
        "response_time_ms": (time.time() - start_time) * 1000,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@cache_test_bp.route("/metrics/legacy")
@monitor_api_endpoint("cache_test_metrics_legacy")
@monitor_performance
def metrics_computation_legacy():
    """Legacy metrics endpoint - no caching."""
    start_time = time.time()
    
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Simulate heavy metrics computation
    time.sleep(0.050)  # 50ms computation
    
    metrics_data = {
        "period": {"start": start_date, "end": end_date},
        "total_tickets": 1247 + int(time.time()) % 100,  # Vary slightly
        "resolved_tickets": 923 + int(time.time()) % 50,
        "avg_resolution_time": 4.2 + (int(time.time()) % 10) * 0.1,
        "technician_stats": {
            "active": 24,
            "avg_load": 52.3 + (int(time.time()) % 20) * 0.5
        },
        "hierarchy_breakdown": {
            "N1": {"count": 512, "avg_time": 2.3},
            "N2": {"count": 387, "avg_time": 4.7},
            "N3": {"count": 234, "avg_time": 8.2},
            "N4": {"count": 114, "avg_time": 15.6}
        }
    }
    
    response = {
        "success": True,
        "cached": False,
        "cache_strategy": "none",
        "architecture": "legacy_metrics_no_cache",
        "metrics": metrics_data,
        "response_time_ms": (time.time() - start_time) * 1000,
        "computation_expensive": True,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@cache_test_bp.route("/metrics/cached")
@monitor_api_endpoint("cache_test_metrics_cached")
@monitor_performance
def metrics_computation_cached():
    """New architecture metrics endpoint - with caching."""
    start_time = time.time()
    
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    # Create cache key based on date range
    cache_key = f"metrics:range:{start_date}:{end_date}"
    
    metrics_data = None
    cached = False
    
    cache_params = {"start_date": start_date, "end_date": end_date}
    
    if not force_refresh:
        # Try cache first
        cached_data = cache.get("metrics_computation", cache_params)
        if cached_data:
            metrics_data = cached_data
            cached = True
    
    if metrics_data is None:
        # Cache miss - compute expensive metrics
        time.sleep(0.050)  # 50ms computation
        
        metrics_data = {
            "period": {"start": start_date, "end": end_date},
            "total_tickets": 1247 + int(time.time()) % 100,
            "resolved_tickets": 923 + int(time.time()) % 50,
            "avg_resolution_time": 4.2 + (int(time.time()) % 10) * 0.1,
            "technician_stats": {
                "active": 24,
                "avg_load": 52.3 + (int(time.time()) % 20) * 0.5
            },
            "hierarchy_breakdown": {
                "N1": {"count": 512, "avg_time": 2.3},
                "N2": {"count": 387, "avg_time": 4.7},
                "N3": {"count": 234, "avg_time": 8.2},
                "N4": {"count": 114, "avg_time": 15.6}
            }
        }
        
        # Store in cache (UnifiedCache manages TTL internally)
        cache.set("metrics_computation", cache_params, metrics_data)
        cached = False
    
    response = {
        "success": True,
        "cached": cached,
        "cache_strategy": "redis_unified_cache",
        "cache_namespace": "metrics_computation", 
        "cache_params": cache_params,
        "architecture": "new_metrics_with_cache",
        "metrics": metrics_data,
        "response_time_ms": (time.time() - start_time) * 1000,
        "computation_expensive": True,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@cache_test_bp.route("/cache/stats")
@monitor_api_endpoint("cache_stats")
def get_cache_stats():
    """Get cache statistics and status."""
    try:
        # Try to get some basic cache info
        cache.set("cache_test", "heartbeat", {"test": True})
        test_result = cache.get("cache_test", "heartbeat")
        
        stats = {
            "cache_available": test_result is not None,
            "cache_type": "redis_unified_cache",
            "test_successful": test_result is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            "cache_available": False,
            "error": str(e),
            "cache_type": "redis_unified_cache",
            "timestamp": datetime.now().isoformat()
        }), 500

@cache_test_bp.route("/cache/clear")
@monitor_api_endpoint("cache_clear")
def clear_cache():
    """Clear cache for deterministic testing."""
    try:
        # Clear all cache for deterministic testing
        cleared_count = cache.clear_all()
        
        return jsonify({
            "success": True,
            "message": f"Cache cleared successfully - {cleared_count} entries removed",
            "cleared_entries": cleared_count,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@cache_test_bp.route("/cache/invalidate/<namespace>")
@monitor_api_endpoint("cache_invalidate")
def invalidate_cache_namespace(namespace: str):
    """Invalidate specific cache namespace for testing."""
    try:
        # Invalidate specific namespace
        cleared_count = cache.invalidate(namespace)
        
        return jsonify({
            "success": True,
            "message": f"Cache namespace '{namespace}' invalidated",
            "cleared_entries": cleared_count,
            "namespace": namespace,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500