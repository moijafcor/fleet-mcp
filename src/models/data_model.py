from typing import Optional
from pydantic import BaseModel


class SharedDataModel(BaseModel):
    id: str
    name: str
    owner_service: str
    consumer_services: list[str]
    storage_type: str
    description: str
    critical_tables: list[str] = []
    naming_pattern: Optional[str] = None
