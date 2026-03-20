from typing import Optional
from sqlmodel import SQLModel, Field
from .base import TimestampModel

class BrokerAccount(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    broker_name: str = Field(index=True) # e.g., Exness
    login: int
    password: str # Should be encrypted in a real app, storing raw for this MVP
    server: str
    is_active: bool = Field(default=False)
