from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from ..models.validation import Experiment, FeatureSnapshot
from ..models.signal import Signal
import json

class ValidationLab:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def run_backtest(self, strategy_id: str, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        # Implementation of walk-forward validation mock
        # Real logic: split [start_date, end_date] into in-sample and out-of-sample (OOS)

        total_days = (end_date - start_date).days
        oos_days = int(total_days * 0.3)
        split_date = end_date - timedelta(days=oos_days)

        # Mock in-sample performance
        in_sample_wr = 0.58
        in_sample_pf = 2.1

        # Mock OOS performance (evidence-driven)
        oos_wr = 0.54
        oos_pf = 1.9
        oos_trades = 120

        return {
            "strategy_id": strategy_id,
            "start_date": start_date.isoformat(),
            "split_date": split_date.isoformat(),
            "end_date": end_date.isoformat(),
            "in_sample": {"winrate": in_sample_wr, "profit_factor": in_sample_pf},
            "oos": {"winrate": oos_wr, "profit_factor": oos_pf, "trades_count": oos_trades},
            "trust_score": 0.82 if oos_wr > 0.5 and oos_trades > 50 else 0.4
        }

    async def promote_experiment(self, experiment_id: int):
        exp = self.db.get(Experiment, experiment_id)
        if not exp:
            return

        # Retire others for same strategy
        active_others = self.db.exec(
            select(Experiment).where(
                Experiment.strategy_id == exp.strategy_id,
                Experiment.is_active == True
            )
        ).all()
        for other in active_others:
            other.is_active = False
            other.decision_state = "retire"
            self.db.add(other)

        exp.is_active = True
        exp.decision_state = "keep_active"
        exp.last_revalidated_at = datetime.utcnow()
        self.db.add(exp)
        self.db.commit()
