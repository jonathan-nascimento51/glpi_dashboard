# Adições para o GLPIService - Filtros de Data Melhorados

def get_dashboard_metrics_with_enhanced_date_filter(self, start_date: str, end_date: str, filter_type: str = "creation") -> dict:
    """
    Obtém métricas do dashboard com filtros de data aprimorados.
    
    Args:
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        filter_type: Tipo de filtro ("creation", "modification", "current_status")
    
    Returns:
        dict: Métricas formatadas para o dashboard
    """
    import datetime
    
    # Validar parâmetros
    if not start_date or not end_date:
        return self.get_dashboard_metrics()
    
    # Criar chave de cache específica para o tipo de filtro
    cache_key = f"dashboard_metrics_filtered_{filter_type}_{start_date}_{end_date}"
    
    # Verificar cache
    if self._is_cache_valid(cache_key):
        cached_data = self._get_cache_data(cache_key)
        if cached_data:
            timestamp = datetime.datetime.now().isoformat()
            self.logger.info(f"[{timestamp}] Cache hit para métricas com filtro de data {filter_type}: {start_date} a {end_date}")
            return cached_data
    
    try:
        # Garantir autenticação
        if not self._ensure_authenticated():
            raise Exception("Falha na autenticação com GLPI")
        
        # Descobrir field_ids se necessário
        if not self.discover_field_ids():
            raise Exception("Falha ao descobrir field_ids")
        
        timestamp = datetime.datetime.now().isoformat()
        self.logger.info(f"[{timestamp}] Obtendo métricas com filtro de data {filter_type}: {start_date} a {end_date}")
        
        if filter_type == "creation":
            # Abordagem original - filtro por data de criação
            totals = self._get_general_metrics_internal(start_date, end_date)
            metrics_by_level = self._get_metrics_by_level_internal(start_date, end_date)
        
        elif filter_type == "modification":
            # Nova abordagem - filtro por data de modificação
            totals = self._get_general_metrics_by_modification_date(start_date, end_date)
            metrics_by_level = self._get_metrics_by_level_by_modification_date(start_date, end_date)
        
        elif filter_type == "current_status":
            # Abordagem de snapshot - estado atual sem filtro de data
            totals = self._get_general_metrics_current_status()
            metrics_by_level = self._get_metrics_by_level_current_status()
        
        else:
            raise ValueError(f"Tipo de filtro inválido: {filter_type}")
        
        # Agregar totais por status
        total_novos = sum(level_data.get("Novo", 0) for level_data in metrics_by_level.values())
        total_pendentes = sum(level_data.get("Pendente", 0) for level_data in metrics_by_level.values())
        total_progresso = sum(
            level_data.get("Processando (atribuído)", 0) + level_data.get("Processando (planejado)", 0)
            for level_data in metrics_by_level.values()
        )
        total_resolvidos = sum(
            level_data.get("Solucionado", 0) + level_data.get("Fechado", 0)
            for level_data in metrics_by_level.values()
        )
        
        # Calcular tendências (simplificado para filtros)
        trends = {
            "novos": 0,
            "pendentes": 0,
            "progresso": 0,
            "resolvidos": 0
        }
        
        # Formatar resultado
        result = {
            "totals": {
                "novos": total_novos,
                "pendentes": total_pendentes,
                "progresso": total_progresso,
                "resolvidos": total_resolvidos
            },
            "trends": trends,
            "levels": {
                "N1": {
                    "novos": metrics_by_level.get("N1", {}).get("Novo", 0),
                    "pendentes": metrics_by_level.get("N1", {}).get("Pendente", 0),
                    "progresso": (
                        metrics_by_level.get("N1", {}).get("Processando (atribuído)", 0) +
                        metrics_by_level.get("N1", {}).get("Processando (planejado)", 0)
                    ),
                    "resolvidos": (
                        metrics_by_level.get("N1", {}).get("Solucionado", 0) +
                        metrics_by_level.get("N1", {}).get("Fechado", 0)
                    )
                },
                "N2": {
                    "novos": metrics_by_level.get("N2", {}).get("Novo", 0),
                    "pendentes": metrics_by_level.get("N2", {}).get("Pendente", 0),
                    "progresso": (
                        metrics_by_level.get("N2", {}).get("Processando (atribuído)", 0) +
                        metrics_by_level.get("N2", {}).get("Processando (planejado)", 0)
                    ),
                    "resolvidos": (
                        metrics_by_level.get("N2", {}).get("Solucionado", 0) +
                        metrics_by_level.get("N2", {}).get("Fechado", 0)
                    )
                },
                "N3": {
                    "novos": metrics_by_level.get("N3", {}).get("Novo", 0),
                    "pendentes": metrics_by_level.get("N3", {}).get("Pendente", 0),
                    "progresso": (
                        metrics_by_level.get("N3", {}).get("Processando (atribuído)", 0) +
                        metrics_by_level.get("N3", {}).get("Processando (planejado)", 0)
                    ),
                    "resolvidos": (
                        metrics_by_level.get("N3", {}).get("Solucionado", 0) +
                        metrics_by_level.get("N3", {}).get("Fechado", 0)
                    )
                },
                "N4": {
                    "novos": metrics_by_level.get("N4", {}).get("Novo", 0),
                    "pendentes": metrics_by_level.get("N4", {}).get("Pendente", 0),
                    "progresso": (
                        metrics_by_level.get("N4", {}).get("Processando (atribuído)", 0) +
                        metrics_by_level.get("N4", {}).get("Processando (planejado)", 0)
                    ),
                    "resolvidos": (
                        metrics_by_level.get("N4", {}).get("Solucionado", 0) +
                        metrics_by_level.get("N4", {}).get("Fechado", 0)
                    )
                }
            },
            "filter_info": {
                "type": filter_type,
                "start_date": start_date,
                "end_date": end_date,
                "description": self._get_filter_description(filter_type)
            }
        }
        
        # Salvar no cache
        self._set_cache_data(cache_key, result, ttl_minutes=3)
        
        timestamp = datetime.datetime.now().isoformat()
        self.logger.info(f"[{timestamp}] Métricas obtidas com sucesso - Filtro: {filter_type}, Total: {sum(result['totals'].values())}")
        
        return result
        
    except Exception as e:
        timestamp = datetime.datetime.now().isoformat()
        self.logger.error(f"[{timestamp}] Erro ao obter métricas com filtro de data {filter_type}: {e}")
        # Retornar métricas sem filtro em caso de erro
        return self.get_dashboard_metrics()

def _get_filter_description(self, filter_type: str) -> str:
    """Retorna descrição do tipo de filtro."""
    descriptions = {
        "creation": "Tickets criados no período (independente do status atual)",
        "modification": "Tickets modificados no período (inclui mudanças de status)",
        "current_status": "Estado atual de todos os tickets (sem filtro de data)"
    }
    return descriptions.get(filter_type, "Filtro desconhecido")

def _get_general_metrics_by_modification_date(self, start_date: str, end_date: str) -> dict:
    """Obtém métricas gerais filtradas por data de modificação."""
    totals = {}
    
    for status_name, status_id in self.status_map.items():
        search_params = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": "12",  # Status
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(status_id),
            "criteria[1][link]": "AND",
            "criteria[1][field]": "19",  # Data de modificação
            "criteria[1][searchtype]": "morethan",
            "criteria[1][value]": start_date,
            "criteria[2][link]": "AND",
            "criteria[2][field]": "19",
            "criteria[2][searchtype]": "lessthan",
            "criteria[2][value]": end_date
        }
        
        response = self._make_authenticated_request(
            'GET',
            f"{self.glpi_url}/search/Ticket",
            params=search_params
        )
        
        if response and response.status_code in [200, 206]:
            if "Content-Range" in response.headers:
                count = int(response.headers["Content-Range"].split("/")[-1])
                totals[status_name] = count
            else:
                totals[status_name] = 0
        else:
            totals[status_name] = 0
    
    return totals

def _get_metrics_by_level_by_modification_date(self, start_date: str, end_date: str) -> dict:
    """Obtém métricas por nível filtradas por data de modificação."""
    metrics = {}
    
    for level_name, group_id in self.service_levels.items():
        level_metrics = {}
        
        for status_name, status_id in self.status_map.items():
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": self.field_ids["GROUP"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(group_id),
                "criteria[1][link]": "AND",
                "criteria[1][field]": "12",  # Status
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": str(status_id),
                "criteria[2][link]": "AND",
                "criteria[2][field]": "19",  # Data de modificação
                "criteria[2][searchtype]": "morethan",
                "criteria[2][value]": start_date,
                "criteria[3][link]": "AND",
                "criteria[3][field]": "19",
                "criteria[3][searchtype]": "lessthan",
                "criteria[3][value]": end_date
            }
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and response.status_code in [200, 206]:
                if "Content-Range" in response.headers:
                    count = int(response.headers["Content-Range"].split("/")[-1])
                    level_metrics[status_name] = count
                else:
                    level_metrics[status_name] = 0
            else:
                level_metrics[status_name] = 0
        
        metrics[level_name] = level_metrics
    
    return metrics

def _get_general_metrics_current_status(self) -> dict:
    """Obtém métricas gerais do estado atual (sem filtro de data)."""
    totals = {}
    
    for status_name, status_id in self.status_map.items():
        count = self.get_ticket_count(group_id=None, status_id=status_id)
        totals[status_name] = count or 0
    
    return totals

def _get_metrics_by_level_current_status(self) -> dict:
    """Obtém métricas por nível do estado atual (sem filtro de data)."""
    metrics = {}
    
    for level_name, group_id in self.service_levels.items():
        level_metrics = {}
        
        for status_name, status_id in self.status_map.items():
            count = self.get_ticket_count(group_id=group_id, status_id=status_id)
            level_metrics[status_name] = count or 0
        
        metrics[level_name] = level_metrics
    
    return metrics
