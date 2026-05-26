from typing import Literal
from pydantic import BaseModel


class Landmine(BaseModel):
    id: str
    affected_services: list[str]
    trigger: str
    severity: Literal["critical", "high", "medium", "low"]
    consequence: str
    remedy: str
    related_config: list[str] = []
