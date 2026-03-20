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

    async def run_scan(self, symbol: str, timeframe: str, broker: str = "Exness") -> List[Signal]:
        # Try to connect with real credentials if available
        account = self.db.exec(select(BrokerAccount).where(BrokerAccount.broker_name == broker, BrokerAccount.is_active == True)).first()
        adapter = broker_manager.get_adapter(broker)

        if account and adapter and hasattr(adapter, 'login'):
            adapter.login = account.login
            adapter.password = account.password
            adapter.server = account.server

        if not adapter: return []
        if not adapter.connected: await adapter.connect()

        # Get REAL history
        data = await adapter.get_history(symbol, timeframe, 100)
        if data is None or len(data) < 50:
            logging.warning(f"Insufficient history for {symbol} {timeframe}")
            return []

        all_signals = []
        for strat in self.strategies:
            signals = await strat.analyze(symbol, timeframe, data)
            for s in signals:
                s.broker = broker
                all_signals.append(s)

        execution_signals = [s for s in all_signals if s.strategy_role == "entry_engine"]
        regime_signals = [s for s in all_signals if s.strategy_role == "regime_filter"]

        final_signals = []
        for es in execution_signals:
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
            signals = await self.run_scan(symbol, tf, broker)
            if signals:
                for s in signals:
                    if best_signal is None or s.confidence > best_signal.confidence:
                        best_signal = s
        return best_signal
