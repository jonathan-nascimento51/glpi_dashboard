from datetime import datetime
from typing import Optional

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