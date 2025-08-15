from flask import Flask, jsonify
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

@app.route('/')
def home():
    return jsonify({
        "message": "GLPI Dashboard API - Mock Mode",
        "endpoints": ["/api/metrics", "/api/v1/metrics", "/api/v1/status", "/health"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mock_mode": True})

# Endpoint para métricas (ambas as versões)
@app.route('/api/metrics')
@app.route('/api/v1/metrics')
def get_metrics():
    """Endpoint para métricas do dashboard com dados mock"""
    mock_data = {
        "status": "success",
        "data": {
            "geral": {
                "total_tickets": 1250,
                "abertos": 320,
                "em_andamento": 180,
                "resolvidos": 750,
                "fechados": 680,
                "pendentes": 45
            },
            "por_nivel": {
                "N1": {
                    "total": 450,
                    "abertos": 120,
                    "em_andamento": 80,
                    "resolvidos": 250
                },
                "N2": {
                    "total": 380,
                    "abertos": 95,
                    "em_andamento": 60,
                    "resolvidos": 225
                }
            }
        },
        "timestamp": time.time(),
        "mock_mode": True
    }
    return jsonify(mock_data), 200

# Endpoint para status do sistema
@app.route('/api/v1/status')
def get_status():
    """Endpoint para status do sistema"""
    return jsonify({
        "status": "operational",
        "version": "1.0.0-mock",
        "uptime": "24h",
        "mock_mode": True
    }), 200

# Endpoint para ranking de técnicos
@app.route('/api/v1/technicians/ranking')
def get_technician_ranking():
    """Endpoint para ranking de técnicos"""
    return jsonify({
        "status": "success",
        "data": [
            {"name": "Joáo Silva", "tickets_resolved": 45, "rating": 4.8},
            {"name": "Maria Santos", "tickets_resolved": 38, "rating": 4.6},
            {"name": "Pedro Costa", "tickets_resolved": 32, "rating": 4.5}
        ],
        "mock_mode": True
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

