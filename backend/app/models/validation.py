from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from .base import TimestampModel

class Experiment(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    strategy_id: str = Field(index=True)
    preset_name: str
    is_active: bool = Field(default=False)

    # OOS Performance Metrics
    oos_winrate: float = Field(default=0.0)
    oos_profit_factor: float = Field(default=0.0)
    oos_trades_count: int = Field(default=0)
    trust_score: float = Field(default=0.0)
    feature_integrity_score: float = Field(default=0.0)

    # Decisions: promote, watch, keep_active, retire, need_more_oos_trades, reject
    decision_state: str = Field(default="watch")

    last_revalidated_at: Optional[datetime] = None
    experiment_data: str = Field(default="") # JSON string for detail data

class FeatureSnapshot(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    broker: str = Field(index=True)
    symbol: str = Field(index=True)
    timeframe: str = Field(index=True)
    bar_open_utc: datetime = Field(index=True)

    features: str = Field(default="") # JSON string of all extracted features
    feature_completeness_score: float = Field(default=1.0)

    # Composite key like broker+symbol+timeframe+bar_open_utc should be unique
    unique_key: str = Field(index=True, unique=True)
