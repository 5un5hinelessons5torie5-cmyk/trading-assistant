from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from .base import TimestampModel

class ExecutionQueueItem(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signal_id: int = Field(foreign_key="signal.id")
    queue_rank: int = Field(default=0)

    # Review states: active, used, unused, expired, ignored
    status: str = Field(default="active", index=True)

    requested_volume: float
    executed_volume: float = Field(default=0.0)
    fill_price: Optional[float] = None
    slippage: Optional[float] = None
    risk_reward: float

    execution_message: Optional[str] = None
    queue_admission_note: Optional[str] = None
    preflight_summary: Optional[str] = None
    preflight_snapshot: Optional[str] = None # JSON snapshot of market/risk state
    audit_trail: str = Field(default="[]") # JSON list of events

    decided_at: Optional[datetime] = None

class Position(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    queue_item_id: Optional[int] = Field(default=None, foreign_key="executionqueueitem.id")
    broker_ticket: str = Field(index=True, unique=True)
    symbol: str = Field(index=True)
    side: str # buy, sell
    volume: float
    entry_price: float
    current_price: float = Field(default=0.0)
    stop_loss: float
    take_profit: float
    tp_ladder: str = Field(default="[]") # JSON list of targets

    # Management State
    is_paper: bool = Field(default=False)
    is_manual: bool = Field(default=False)
    is_breakeven_activated: bool = Field(default=False)
    trailing_stop_distance: Optional[float] = None
    tp1_hit: bool = Field(default=False)

    status: str = Field(default="open", index=True) # open, closed, part_closed
    pnl: float = Field(default=0.0)
    closed_at: Optional[datetime] = None

    # Journaling Integration
    notes: Optional[str] = None
    tags: str = Field(default="[]") # JSON
    mistakes: str = Field(default="[]") # JSON
    discipline_score: Optional[int] = None
    setup_quality_score: Optional[int] = None
    emotions: str = Field(default="[]") # JSON
