# -*- coding: utf-8 -*-
"""Classes para padronização de paginação e filtros GLPI"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, validator


class TicketStatus(Enum):
    """Status padronizados de tickets"""

    NOVO = 1
    PROCESSANDO_ATRIBUIDO = 2
    PROCESSANDO_PLANEJADO = 3
    PENDENTE = 4
    SOLUCIONADO = 5
    FECHADO = 6


class ServiceLevel(Enum):
    """Níveis de atendimento padronizados"""

    N1 = 89
    N2 = 90
    N3 = 91
    N4 = 92


class TicketPriority(Enum):
    """Prioridades de tickets"""

    MUITO_BAIXA = 1
    BAIXA = 2
    MEDIA = 3
    ALTA = 4
    MUITO_ALTA = 5
    CRITICA = 6


class SortOrder(Enum):
    """Ordem de classificação"""

    ASC = "ASC"
    DESC = "DESC"


class DateRange(BaseModel):
    """Intervalo de datas para filtros"""

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @validator("end_date")
    def end_date_after_start_date(cls, v, values):
        if v and values.get("start_date") and v < values["start_date"]:
            raise ValueError("end_date deve ser posterior a start_date")
        return v

    def to_glpi_format(self) -> Dict[str, str]:
        """Converte para formato esperado pelo GLPI"""
        result = {}
        if self.start_date:
            result["start_date"] = self.start_date.strftime("%Y-%m-%d")
        if self.end_date:
            result["end_date"] = self.end_date.strftime("%Y-%m-%d")
        return result


class PaginationParams(BaseModel):
    """Parâmetros de paginação padronizados"""

    page: int = Field(default=1, ge=1, description="Número da página (inicia em 1)")
    page_size: int = Field(default=50, ge=1, le=1000, description="Itens por página")
    cursor: Optional[str] = Field(
        default=None, description="Cursor para paginação baseada em cursor"
    )

    @property
    def offset(self) -> int:
        """Calcula offset baseado na página"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Alias para page_size"""
        return self.page_size

    def to_glpi_range(self) -> str:
        """Converte para formato de range do GLPI"""
        start = self.offset
        end = start + self.page_size - 1
        return f"{start}-{end}"

    def next_page(self) -> "PaginationParams":
        """Retorna parâmetros para próxima página"""
        return PaginationParams(
            page=self.page + 1, page_size=self.page_size, cursor=self.cursor
        )

    def previous_page(self) -> Optional["PaginationParams"]:
        """Retorna parâmetros para página anterior"""
        if self.page <= 1:
            return None
        return PaginationParams(
            page=self.page - 1, page_size=self.page_size, cursor=self.cursor
        )


class TicketFilters(BaseModel):
    """Filtros padronizados para tickets"""

    status: Optional[List[TicketStatus]] = None
    service_level: Optional[List[ServiceLevel]] = None
    priority: Optional[List[TicketPriority]] = None
    date_range: Optional[DateRange] = None
    technician_id: Optional[int] = None
    category_id: Optional[int] = None
    entity_id: Optional[int] = None
    search_text: Optional[str] = Field(default=None, max_length=255)

    def to_glpi_criteria(self) -> List[Dict[str, Any]]:
        """Converte filtros para critérios do GLPI"""
        criteria = []
        criteria_index = 0

        # Filtro por status
        if self.status:
            status_values = [s.value for s in self.status]
            if len(status_values) == 1:
                criteria.append(
                    {
                        f"criteria[{criteria_index}][field]": "12",  # Campo status
                        f"criteria[{criteria_index}][searchtype]": "equals",
                        f"criteria[{criteria_index}][value]": status_values[0],
                    }
                )
            else:
                # Múltiplos status usando OR
                for i, status_value in enumerate(status_values):
                    link = "OR" if i > 0 else None
                    criteria.append(
                        {
                            f"criteria[{criteria_index}][field]": "12",
                            f"criteria[{criteria_index}][searchtype]": "equals",
                            f"criteria[{criteria_index}][value]": status_value,
                            **(
                                {f"criteria[{criteria_index}][link]": link}
                                if link
                                else {}
                            ),
                        }
                    )
                    criteria_index += 1
                criteria_index -= 1  # Ajustar para próximo critério
            criteria_index += 1

        # Filtro por nível de serviço (grupo técnico)
        if self.service_level:
            level_values = [sl.value for sl in self.service_level]
            if criteria:
                criteria.append({f"criteria[{criteria_index}][link]": "AND"})

            if len(level_values) == 1:
                criteria.append(
                    {
                        f"criteria[{criteria_index}][field]": "8",  # Campo grupo
                        f"criteria[{criteria_index}][searchtype]": "equals",
                        f"criteria[{criteria_index}][value]": level_values[0],
                    }
                )
            else:
                # Múltiplos níveis usando OR
                for i, level_value in enumerate(level_values):
                    link = "OR" if i > 0 else None
                    criteria.append(
                        {
                            f"criteria[{criteria_index}][field]": "8",
                            f"criteria[{criteria_index}][searchtype]": "equals",
                            f"criteria[{criteria_index}][value]": level_value,
                            **(
                                {f"criteria[{criteria_index}][link]": link}
                                if link
                                else {}
                            ),
                        }
                    )
                    criteria_index += 1
                criteria_index -= 1
            criteria_index += 1

        # Filtro por prioridade
        if self.priority:
            priority_values = [p.value for p in self.priority]
            if criteria:
                criteria.append({f"criteria[{criteria_index}][link]": "AND"})

            criteria.append(
                {
                    f"criteria[{criteria_index}][field]": "3",  # Campo prioridade
                    f"criteria[{criteria_index}][searchtype]": "equals",
                    f"criteria[{criteria_index}][value]": priority_values[0]
                    if len(priority_values) == 1
                    else priority_values,
                }
            )
            criteria_index += 1

        # Filtro por data
        if self.date_range:
            date_filters = self.date_range.to_glpi_format()

            if date_filters.get("start_date"):
                if criteria:
                    criteria.append({f"criteria[{criteria_index}][link]": "AND"})
                criteria.append(
                    {
                        f"criteria[{criteria_index}][field]": "15",  # Campo data criação
                        f"criteria[{criteria_index}][searchtype]": "morethan",
                        f"criteria[{criteria_index}][value]": date_filters[
                            "start_date"
                        ],
                    }
                )
                criteria_index += 1

            if date_filters.get("end_date"):
                if criteria:
                    criteria.append({f"criteria[{criteria_index}][link]": "AND"})
                criteria.append(
                    {
                        f"criteria[{criteria_index}][field]": "15",
                        f"criteria[{criteria_index}][searchtype]": "lessthan",
                        f"criteria[{criteria_index}][value]": date_filters["end_date"],
                    }
                )
                criteria_index += 1

        # Filtro por técnico
        if self.technician_id:
            if criteria:
                criteria.append({f"criteria[{criteria_index}][link]": "AND"})
            criteria.append(
                {
                    f"criteria[{criteria_index}][field]": "5",  # Campo técnico atribuído
                    f"criteria[{criteria_index}][searchtype]": "equals",
                    f"criteria[{criteria_index}][value]": self.technician_id,
                }
            )
            criteria_index += 1

        # Filtro por texto
        if self.search_text:
            if criteria:
                criteria.append({f"criteria[{criteria_index}][link]": "AND"})
            criteria.append(
                {
                    f"criteria[{criteria_index}][field]": "1",  # Campo título
                    f"criteria[{criteria_index}][searchtype]": "contains",
                    f"criteria[{criteria_index}][value]": self.search_text,
                }
            )

        return criteria


class SortParams(BaseModel):
    """Parâmetros de ordenação"""

    field: str = Field(default="date", description="Campo para ordenação")
    order: SortOrder = Field(
        default=SortOrder.DESC, description="Ordem de classificação"
    )

    def to_glpi_sort(self) -> Dict[str, str]:
        """Converte para formato de ordenação do GLPI"""
        field_mapping = {
            "date": "15",  # Data de criação
            "status": "12",  # Status
            "priority": "3",  # Prioridade
            "title": "1",  # Título
            "technician": "5",  # Técnico
        }

        glpi_field = field_mapping.get(self.field, "15")
        return {"sort": glpi_field, "order": self.order.value}


@dataclass
class PaginatedResponse:
    """Resposta paginada padronizada"""

    items: List[Any]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None

    @classmethod
    def from_glpi_response(
        cls, items: List[Any], content_range: str, pagination: PaginationParams
    ) -> "PaginatedResponse":
        """Cria resposta paginada a partir da resposta do GLPI"""
        # Parse Content-Range: "items 0-49/150"
        try:
            range_part, total_str = content_range.split("/")
            total_count = int(total_str)
            start, end = map(int, range_part.split("-"))
        except (ValueError, AttributeError):
            total_count = len(items)
            start = pagination.offset
            end = start + len(items) - 1

        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size

        return cls(
            items=items,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_previous=pagination.page > 1,
        )


class GLPIQueryBuilder:
    """Construtor de queries GLPI padronizado"""

    def __init__(self):
        self.params = {
            "is_deleted": 0,
            "forcedisplay[0]": 1,  # ID
            "forcedisplay[1]": 1,  # Título
            "forcedisplay[2]": 12,  # Status
            "forcedisplay[3]": 3,  # Prioridade
            "forcedisplay[4]": 15,  # Data criação
            "forcedisplay[5]": 8,  # Grupo
        }

    def add_filters(self, filters: TicketFilters) -> "GLPIQueryBuilder":
        """Adiciona filtros à query"""
        criteria = filters.to_glpi_criteria()
        for criterion in criteria:
            self.params.update(criterion)
        return self

    def add_pagination(self, pagination: PaginationParams) -> "GLPIQueryBuilder":
        """Adiciona paginação à query"""
        self.params["range"] = pagination.to_glpi_range()
        return self

    def add_sort(self, sort: SortParams) -> "GLPIQueryBuilder":
        """Adiciona ordenação à query"""
        sort_params = sort.to_glpi_sort()
        self.params.update(sort_params)
        return self

    def build(self) -> Dict[str, Any]:
        """Constrói os parâmetros finais da query"""
        return self.params.copy()

    def reset(self) -> "GLPIQueryBuilder":
        """Reseta o builder para estado inicial"""
        self.__init__()
        return self


# Funções utilitárias
def create_date_range(
    start_date: Optional[Union[str, date]] = None,
    end_date: Optional[Union[str, date]] = None,
) -> DateRange:
    """Cria um DateRange a partir de strings ou objetos date"""

    def parse_date(d: Union[str, date, None]) -> Optional[date]:
        if d is None:
            return None
        if isinstance(d, str):
            return datetime.strptime(d, "%Y-%m-%d").date()
        return d

    return DateRange(start_date=parse_date(start_date), end_date=parse_date(end_date))


def create_ticket_filters(
    status: Optional[List[Union[TicketStatus, int]]] = None,
    service_level: Optional[List[Union[ServiceLevel, int]]] = None,
    priority: Optional[List[Union[TicketPriority, int]]] = None,
    **kwargs,
) -> TicketFilters:
    """Cria filtros de ticket com conversão automática de tipos"""

    def convert_enum_list(items, enum_class):
        if not items:
            return None
        result = []
        for item in items:
            if isinstance(item, int):
                # Encontrar enum por valor
                for enum_item in enum_class:
                    if enum_item.value == item:
                        result.append(enum_item)
                        break
            else:
                result.append(item)
        return result

    return TicketFilters(
        status=convert_enum_list(status, TicketStatus),
        service_level=convert_enum_list(service_level, ServiceLevel),
        priority=convert_enum_list(priority, TicketPriority),
        **kwargs,
    )
