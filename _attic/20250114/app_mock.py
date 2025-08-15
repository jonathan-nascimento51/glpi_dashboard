from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "GLPI Dashboard API - Mock Mode",
        "endpoints": ["/api/metrics", "/health"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mock_mode": True})

@app.route('/api/metrics')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
