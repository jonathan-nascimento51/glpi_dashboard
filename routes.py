from flask import render_template, jsonify
from app import app
import logging

# Configure logging  
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    """Dashboard principal - Foco exclusivo nas métricas"""
    return render_template('index.html')

@app.route('/api/metrics')
def api_metrics():
    """Dados das métricas de chamados"""
    return jsonify({
        'novos': 42,
        'pendentes': 11,
        'progresso': 37,
        'resolvidos': 64,
        'total': 154,
        'niveis': {
            'n1': {'novos': 15, 'progresso': 12, 'pendentes': 4, 'resolvidos': 28},
            'n2': {'novos': 12, 'progresso': 15, 'pendentes': 4, 'resolvidos': 18},
            'n3': {'novos': 8, 'progresso': 6, 'pendentes': 2, 'resolvidos': 10},
            'n4': {'novos': 6, 'progresso': 4, 'pendentes': 1, 'resolvidos': 6}
        },
        'tendencias': {
            'novos': '+12%',
            'pendentes': '-8%',
            'progresso': '+5%',
            'resolvidos': '+18%'
        }
    })

@app.route('/api/status')
def api_status():
    """Status do sistema"""
    return jsonify({
        'status': 'online',
        'sistema_ativo': True,
        'ultima_atualizacao': '2024-08-04T00:45:00Z'
    })