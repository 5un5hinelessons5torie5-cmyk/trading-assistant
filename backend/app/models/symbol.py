from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base import TimestampModel

class Symbol(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    broker: str = Field(index=True)
    asset_group: str = Field(index=True) # e.g., forex, crypto, indices
    status: str = Field(default="research_only") # live_ready, research_only, blocked
    is_favorite: bool = Field(default=False)

    # Exness / MT5 specific info
    min_volume: float = Field(default=0.01)
    max_volume: float = Field(default=100.0)
    volume_step: float = Field(default=0.01)
    spread_sanity_threshold: float = Field(default=0.0)

    blocked_reason: Optional[str] = None
