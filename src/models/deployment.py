from typing import Optional
from pydantic import BaseModel


class DeploymentEntry(BaseModel):
    service_id: str
    environment: str
    host: str
    internal_ip: Optional[str] = None
    port: int
    process: str
    notes: Optional[str] = None
