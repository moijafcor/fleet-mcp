from typing import Optional
from pydantic import BaseModel


class ApiContract(BaseModel):
    id: str
    from_service: str
    to_service: str
    protocol: str
    mechanism: str
    endpoint: Optional[str] = None
    description: str
    critical_config: list[str] = []
    break_risk: Optional[str] = None
