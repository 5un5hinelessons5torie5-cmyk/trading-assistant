from typing import Optional
from sqlmodel import SQLModel, Field
from .base import TimestampModel

class SystemSettings(TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kill_switch: bool = Field(default=False)
    max_pending_mt5_approvals: int = Field(default=5)
    max_pending_paper_approvals: int = Field(default=10)
    max_mt5_open_positions: int = Field(default=3)
    max_paper_open_positions: int = Field(default=10)
    daily_loss_stop_pct: float = Field(default=2.0)

    # Asset group caps (JSON string)
    asset_group_caps: str = Field(default="{}")

    operator_notes: str = Field(default="")
