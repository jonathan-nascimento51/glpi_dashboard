from flask import render_template, jsonify, request
from app import app
from services.api_service import APIService
import logging

api_service = APIService()

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    """Get dashboard metrics data"""
    try:
        metrics = api_service.get_metrics()
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        logging.error(f"Error fetching metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar métricas do sistema'
        }), 500

@app.route('/api/system-status')
def get_system_status():
    """Get current system status"""
    try:
        status = api_service.get_system_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logging.error(f"Error fetching system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar status do sistema'
        }), 500

@app.route('/api/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    try:
        results = api_service.search(query)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        logging.error(f"Error in search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro na pesquisa'
        }), 500

@app.route('/api/chart-data/<chart_type>')
def get_chart_data(chart_type):
    """Get data for specific chart types"""
    try:
        data = api_service.get_chart_data(chart_type)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logging.error(f"Error fetching chart data for {chart_type}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar dados do gráfico {chart_type}'
        }), 500

@app.route('/api/alerts')
def get_alerts():
    """Get system alerts"""
    try:
        alerts = api_service.get_alerts()
        return jsonify({
            'success': True,
            'data': alerts
        })
    except Exception as e:
        logging.error(f"Error fetching alerts: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar alertas'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor'
    }), 500
