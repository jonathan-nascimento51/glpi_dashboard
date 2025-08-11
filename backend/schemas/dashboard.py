from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

# Este arquivo foi consolidado. 
# Todos os modelos foram movidos para models/validation.py
# Mantenha apenas imports específicos se necessário

class FiltersApplied(BaseModel):
    """Filtros aplicados na consulta"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    level: Optional[str] = None
    technician: Optional[str] = None
    category: Optional[str] = None
