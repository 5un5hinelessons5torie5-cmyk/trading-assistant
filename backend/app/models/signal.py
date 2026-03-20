from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base import TimestampModel

class Signal(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    strategy_id: str = Field(index=True)
    strategy_label: str
    strategy_role: str # entry_engine, regime_filter, selection_layer
    broker: str = Field(index=True)
    symbol: str = Field(index=True)
    timeframe: str
    side: str # buy, sell
    entry_price: float
    stop_loss: float
    take_profit: float
    tp_ladder: str # JSON string for multiple targets

    confidence: float
    setup_confirmation: bool
    queue_quality: float
    confluence_text: str

    execution_readiness: bool
    execution_block_reason: Optional[str] = None

    preflight_summary: Optional[str] = None
    preflight_snapshot: Optional[str] = None # JSON string

    ml_score: Optional[float] = None
    ml_pass: Optional[bool] = None
    ml_reason: Optional[str] = None
    ml_model_version: Optional[str] = None
