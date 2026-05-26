from typing import Optional
from pydantic import BaseModel


class ServiceUrls(BaseModel):
    production: str
    staging: Optional[str] = None
    local: Optional[str] = None


class ServiceStack(BaseModel):
    language: str
    version: str
    framework: str
    framework_version: Optional[str] = None
    extras: dict[str, str] = {}


class ServiceOwnership(BaseModel):
    path_patterns: list[str]


class Service(BaseModel):
    id: str
    name: str
    role: str
    stack: ServiceStack
    urls: ServiceUrls
    entry_points: list[str]
    owns: ServiceOwnership
    port: Optional[int] = None
    description: Optional[str] = None
