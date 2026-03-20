import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from .ema_pullback import EMAPullbackStrategy
from .breakout_retest import BreakoutRetestStrategy
from .donchian_trend import DonchianTrendStrategy
from .cross_sectional_momentum import CrossSectionalMomentumStrategy
from ..models.signal import Signal
from ..models.broker import BrokerAccount
from ..brokers.manager import broker_manager
from ..ml.meta_model import MLMetaLayer
from sqlmodel import Session, select

class SignalOrchestrator:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.strategies = [
            EMAPullbackStrategy(),
            BreakoutRetestStrategy(),
            DonchianTrendStrategy(),
            CrossSectionalMomentumStrategy()
        ]

    async def run_scan(self, symbol: str, timeframe: str, broker: str = "Exness", scan_mode: str = "manual") -> List[Signal]:
        account = self.db.exec(select(BrokerAccount).where(BrokerAccount.broker_name == broker, BrokerAccount.is_active == True)).first()
        adapter = broker_manager.get_adapter(broker)

        if account and adapter and hasattr(adapter, 'login'):
            adapter.login = account.login
            adapter.password = account.password
            adapter.server = account.server

        if not adapter: return []
        if not adapter.connected: await adapter.connect()

        data = await adapter.get_history(symbol, timeframe, 100)
        if data is None or len(data) < 50: return []

        all_signals = []
        for strat in self.strategies:
            signals = await strat.analyze(symbol, timeframe, data)
            for s in signals:
                s.broker = broker
                s.scan_mode = scan_mode
                all_signals.append(s)

        execution_signals = [s for s in all_signals if s.strategy_role == "entry_engine"]
        regime_signals = [s for s in all_signals if s.strategy_role == "regime_filter"]

        final_signals = []
        for es in execution_signals:
            # Apply Regime Filter (e.g., only buy if Donchian is bullish)
            matches = [rs for rs in regime_signals if rs.symbol == es.symbol and rs.timeframe == es.timeframe]
            if not matches or matches[0].side == es.side:
                final_signals.append(es)

        ml = MLMetaLayer()
        ranked_signals = await ml.rank_signals(final_signals)

        for s in ranked_signals:
            self.db.add(s)
            self.db.commit()
            self.db.refresh(s)

        return ranked_signals

    async def auto_best_setup_scan(self, symbol: str, timeframes: List[str], broker: str = "Exness") -> Optional[Signal]:
        best_signal = None
        for tf in timeframes:
            signals = await self.run_scan(symbol, tf, broker, scan_mode="auto_best_setup")
            if signals:
                for s in signals:
                    if best_signal is None or (s.ml_score or 0) > (best_signal.ml_score or 0):
                        best_signal = s
        return best_signal
