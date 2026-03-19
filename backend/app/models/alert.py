from typing import Optional
from sqlmodel import SQLModel, Field
from .base import TimestampModel

class Alert(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True) # validation, broker, scheduler, ML, automation
    level: str # info, warning, error, critical
    title: str
    message: str
    is_read: bool = Field(default=False)
    dedupe_key: Optional[str] = Field(default=None, index=True)
    external_sent: bool = Field(default=False) # e.g., Telegram
