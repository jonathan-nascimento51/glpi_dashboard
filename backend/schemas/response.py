from datetime import datetime, timezone
from typing import Optional, List, Any, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem descritiva sobre o resultado")
    data: Optional[T] = Field(None, description="Os dados retornados pela API")
    errors: Optional[List[Any]] = Field(None, description="Lista de erros, se houver")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp da resposta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v.tzinfo else v.replace(tzinfo=timezone.utc).isoformat()
        }

class ErrorDetail(BaseModel):
    field: Optional[str] = Field(None, description="O campo que causou o erro de validação")
    message: str = Field(..., description="Descrição do erro")
    code: Optional[str] = Field(None, description="Um código de erro interno")
