from sqlmodel import Session, select, func
from ..models.execution import Position
from typing import Dict, Any

class AnalyticsEngine:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_performance_summary(self) -> Dict[str, Any]:
        # Simple aggregate
        positions = self.db.exec(select(Position)).all()

        total_trades = len(positions)
        wins = len([p for p in positions if p.pnl > 0])
        total_pnl = sum([p.pnl for p in positions])

        return {
            "total_trades": total_trades,
            "win_rate": wins / total_trades if total_trades > 0 else 0,
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / total_trades if total_trades > 0 else 0
        }
