# Adições para routes.py - Suporte a Filtros de Data Melhorados

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Endpoint melhorado para obter métricas com diferentes tipos de filtro de data."""
    try:
        # Extrair parâmetros
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        filter_type = request.args.get('filter_type', 'creation')  # Novo parâmetro
        
        # Outros filtros existentes
        status = request.args.get('status')
        priority = request.args.get('priority')
        level = request.args.get('level')
        technician = request.args.get('technician')
        category = request.args.get('category')
        
        # Validar tipo de filtro
        valid_filter_types = ['creation', 'modification', 'current_status']
        if filter_type not in valid_filter_types:
            return jsonify({
                'error': f'Tipo de filtro inválido. Use: {", ".join(valid_filter_types)}'
            }), 400
        
        # Log da requisição
        app.logger.info(f"Requisição de métricas - Filtro: {filter_type}, Datas: {start_date} a {end_date}")
        
        # Validar formato das datas se fornecidas
        if start_date or end_date:
            try:
                if start_date:
                    datetime.strptime(start_date, '%Y-%m-%d')
                if end_date:
                    datetime.strptime(end_date, '%Y-%m-%d')
                    
                # Validar ordem das datas
                if start_date and end_date and start_date > end_date:
                    return jsonify({
                        'error': 'Data de início deve ser anterior à data de fim'
                    }), 400
                    
            except ValueError:
                return jsonify({
                    'error': 'Formato de data inválido. Use YYYY-MM-DD'
                }), 400
        
        # Determinar qual função chamar
        if start_date and end_date:
            # Usar nova função com tipo de filtro
            metrics = glpi_service.get_dashboard_metrics_with_enhanced_date_filter(
                start_date, end_date, filter_type
            )
        elif any([status, priority, level, technician, category]):
            # Outros filtros (implementação existente)
            filters = extract_filter_params(request)
            metrics = glpi_service.get_dashboard_metrics_with_filters(filters)
        else:
            # Sem filtros
            metrics = glpi_service.get_dashboard_metrics()
        
        return jsonify(metrics)
        
    except Exception as e:
        app.logger.error(f"Erro ao obter métricas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/filter-types', methods=['GET'])
def get_filter_types():
    """Endpoint para obter tipos de filtro disponíveis."""
    filter_types = [
        {
            'value': 'creation',
            'label': 'Data de Criação',
            'description': 'Tickets criados no período (independente do status atual)'
        },
        {
            'value': 'modification',
            'label': 'Data de Modificação',
            'description': 'Tickets modificados no período (inclui mudanças de status)'
        },
        {
            'value': 'current_status',
            'label': 'Estado Atual',
            'description': 'Estado atual de todos os tickets (sem filtro de data)'
        }
    ]
    
    return jsonify({
        'filter_types': filter_types,
        'default': 'creation'
    })
