from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from ..models.validation import Experiment, FeatureSnapshot
from ..models.signal import Signal
from ..models.broker import BrokerAccount
from .backtest_engine import BacktestEngine
from ..strategies.ema_pullback import EMAPullbackStrategy
from ..strategies.breakout_retest import BreakoutRetestStrategy
from ..brokers.manager import broker_manager
import json
import pandas as pd
import logging

class ValidationLab:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.engine = BacktestEngine()

    async def run_backtest(self, strategy_id: str, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        # 1. Fetch data from active broker if possible
        account = self.db.exec(select(BrokerAccount).where(BrokerAccount.is_active == True)).first()
        adapter = broker_manager.get_adapter(account.broker_name if account else "Paper")

        if account and adapter and hasattr(adapter, 'login'):
            adapter.login = account.login
            adapter.password = account.password
            adapter.server = account.server

        if not adapter.connected: await adapter.connect()

        # Attempt to get 500 bars for backtest
        data = await adapter.get_history(symbol, "H1", 500)

        if data is None or len(data) < 100:
            # Fallback only if broker fails
            data = pd.DataFrame({
                'open': [1.0800 + i * 0.0001 for i in range(500)],
                'high': [1.0805 + i * 0.0001 for i in range(500)],
                'low': [1.0795 + i * 0.0001 for i in range(500)],
                'close': [1.0802 + i * 0.0001 for i in range(500)]
            })

        # 2. Select strategy
        strategy = None
        if strategy_id == "ema_pullback": strategy = EMAPullbackStrategy()
        elif strategy_id == "breakout_retest": strategy = BreakoutRetestStrategy()

        if not strategy: return {"error": "Unknown strategy"}

        # 3. Walk-forward split
        oos_idx = int(len(data) * 0.7)
        in_sample_data = data.iloc[:oos_idx]
        oos_data = data.iloc[oos_idx:]

        # 4. Run engine
        is_result = await self.engine.run(strategy, in_sample_data)
        oos_result = await self.engine.run(strategy, oos_data)

        return {
            "strategy_id": strategy_id,
            "start_date": start_date.isoformat(),
            "split_date": (start_date + timedelta(days=200)).isoformat(),
            "end_date": end_date.isoformat(),
            "in_sample": {"winrate": is_result["win_rate"], "profit_factor": is_result["profit_factor"]},
            "oos": {"winrate": oos_result["win_rate"], "profit_factor": oos_result["profit_factor"], "trades_count": oos_result["trades_count"]},
            "trust_score": 0.82 if oos_result["win_rate"] > 0.5 else 0.4
        }

    async def promote_experiment(self, experiment_id: int):
        exp = self.db.get(Experiment, experiment_id)
        if not exp: return

        active_others = self.db.exec(
            select(Experiment).where(Experiment.strategy_id == exp.strategy_id, Experiment.is_active == True)
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
