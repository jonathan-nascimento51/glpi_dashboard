from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
import re
import logging

logger = logging.getLogger('validators')

class ValidationError(Exception):
    """Exceção customizada para erros de validação"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

class ValidationResult:
    """Resultado de uma validação"""
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)

def validate_date_format(date_string: Optional[str]) -> bool:
    """
    Valida se uma string de data está no formato correto (YYYY-MM-DD)
    
    Args:
        date_string: String da data para validar
        
    Returns:
        bool: True se a data é válida, False caso contrário
    """
    if not date_string:
        return True  # Datas vazias são consideradas válidas (opcionais)
    
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> bool:
    """
    Valida se um intervalo de datas é válido
    
    Args:
        start_date: Data de início no formato YYYY-MM-DD
        end_date: Data de fim no formato YYYY-MM-DD
        
    Returns:
        bool: True se o intervalo é válido, False caso contrário
    """
    if not start_date or not end_date:
        return True  # Se uma das datas está vazia, considera válido
    
    if not validate_date_format(start_date) or not validate_date_format(end_date):
        return False
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return start <= end
    except ValueError:
        return False

def validate_limit(limit: Optional[int], max_limit: int = 1000) -> bool:
    """
    Valida se um limite é válido
    
    Args:
        limit: Limite a ser validado
        max_limit: Limite máximo permitido
        
    Returns:
        bool: True se o limite é válido, False caso contrário
    """
    if limit is None:
        return True
    
    return isinstance(limit, int) and 0 < limit <= max_limit

def validate_filter_params(params: Dict[str, Any]) -> ValidationResult:
    """
    Valida parâmetros de filtro de forma abrangente
    
    Args:
        params: Dicionário com parâmetros de filtro
        
    Returns:
        ValidationResult: Resultado da validação
    """
    result = ValidationResult()
    
    # Validar datas
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    
    if start_date and not validate_date_format(start_date):
        result.add_error(f"Formato de data_inicio inválido: {start_date}. Use YYYY-MM-DD")
    
    if end_date and not validate_date_format(end_date):
        result.add_error(f"Formato de data_fim inválido: {end_date}. Use YYYY-MM-DD")
    
    if not validate_date_range(start_date, end_date):
        result.add_error("Data de início não pode ser posterior à data de fim")
    
    # Validar status
    status = params.get('status')
    valid_statuses = ['novo', 'pendente', 'progresso', 'resolvido']
    if status and status not in valid_statuses:
        result.add_error(f"Status inválido: {status}. Valores válidos: {', '.join(valid_statuses)}")
    
    # Validar prioridade
    priority = params.get('priority')
    if priority is not None:
        try:
            priority_int = int(priority)
            if not (1 <= priority_int <= 5):
                result.add_error(f"Prioridade deve estar entre 1 e 5, recebido: {priority}")
        except (ValueError, TypeError):
            result.add_error(f"Prioridade deve ser um número inteiro, recebido: {priority}")
    
    # Validar nível
    level = params.get('level')
    valid_levels = ['n1', 'n2', 'n3', 'n4']
    if level and level not in valid_levels:
        result.add_error(f"Nível inválido: {level}. Valores válidos: {', '.join(valid_levels)}")
    
    # Validar limite
    limit = params.get('limit')
    if limit is not None and not validate_limit(limit):
        result.add_error(f"Limite inválido: {limit}. Deve ser um número entre 1 e 1000")
    
    # Validar IDs (técnico, categoria)
    for field in ['technician', 'category']:
        value = params.get(field)
        if value is not None:
            try:
                int(value)
            except (ValueError, TypeError):
                result.add_error(f"{field.capitalize()} deve ser um ID numérico válido, recebido: {value}")
    
    # Verificar se o intervalo de datas não é muito amplo (warning)
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            days_diff = (end_dt - start_dt).days
            
            if days_diff > 365:
                result.add_warning(f"Intervalo de datas muito amplo ({days_diff} dias). Considere usar um período menor para melhor performance.")
            elif days_diff > 90:
                result.add_warning(f"Intervalo de datas amplo ({days_diff} dias). Pode impactar a performance.")
        except ValueError:
            pass  # Erro já capturado na validação de formato
    
    return result

def validate_api_response(response_data: Any) -> ValidationResult:
    """
    Valida estrutura de resposta da API
    
    Args:
        response_data: Dados da resposta da API
        
    Returns:
        ValidationResult: Resultado da validação
    """
    result = ValidationResult()
    
    if not isinstance(response_data, dict):
        result.add_error("Resposta da API deve ser um objeto JSON")
        return result
    
    # Verificar campos obrigatórios
    required_fields = ['success']
    for field in required_fields:
        if field not in response_data:
            result.add_error(f"Campo obrigatório ausente: {field}")
    
    # Se é uma resposta de sucesso, verificar estrutura de dados
    if response_data.get('success') is True:
        if 'data' not in response_data:
            result.add_error("Resposta de sucesso deve conter campo 'data'")
        else:
            data = response_data['data']
            if isinstance(data, dict) and 'niveis' in data:
                # Validar estrutura de métricas
                niveis = data['niveis']
                expected_levels = ['Manutenção Geral', 'Patrimônio', 'Atendimento', 'Mecanografia']
                
                for level in expected_levels:
                    if level not in niveis:
                        result.add_warning(f"Nível esperado ausente: {level}")
                    else:
                        level_data = niveis[level]
                        if not isinstance(level_data, dict):
                            result.add_error(f"Dados do nível {level} devem ser um objeto")
                        else:
                            expected_metrics = ['novos', 'pendentes', 'progresso', 'resolvidos', 'total']
                            for metric in expected_metrics:
                                if metric not in level_data:
                                    result.add_warning(f"Métrica ausente no nível {level}: {metric}")
                                elif not isinstance(level_data[metric], (int, float)):
                                    result.add_error(f"Métrica {metric} do nível {level} deve ser numérica")
    
    # Se é uma resposta de erro, verificar estrutura de erro
    elif response_data.get('success') is False:
        if 'message' not in response_data and 'error' not in response_data:
            result.add_error("Resposta de erro deve conter campo 'message' ou 'error'")
    
    return result

def sanitize_input(value: str, max_length: int = 255, allow_html: bool = False) -> str:
    """
    Sanitiza entrada do usuário
    
    Args:
        value: Valor a ser sanitizado
        max_length: Comprimento máximo permitido
        allow_html: Se permite tags HTML
        
    Returns:
        str: Valor sanitizado
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remover espaços em branco no início e fim
    value = value.strip()
    
    # Limitar comprimento
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"Input truncado para {max_length} caracteres")
    
    # Remover caracteres de controle
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Remover HTML se não permitido
    if not allow_html:
        value = re.sub(r'<[^>]*>', '', value)
    
    return value

def validate_pagination_params(page: Optional[int] = None, per_page: Optional[int] = None) -> ValidationResult:
    """
    Valida parâmetros de paginação
    
    Args:
        page: Número da página
        per_page: Itens por página
        
    Returns:
        ValidationResult: Resultado da validação
    """
    result = ValidationResult()
    
    if page is not None:
        if not isinstance(page, int) or page < 1:
            result.add_error("Página deve ser um número inteiro maior que 0")
    
    if per_page is not None:
        if not isinstance(per_page, int) or per_page < 1:
            result.add_error("Itens por página deve ser um número inteiro maior que 0")
        elif per_page > 100:
            result.add_error("Máximo de 100 itens por página")
    
    return result