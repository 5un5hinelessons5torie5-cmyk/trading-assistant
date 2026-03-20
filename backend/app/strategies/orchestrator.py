import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from .ema_pullback import EMAPullbackStrategy
from .breakout_retest import BreakoutRetestStrategy
from .donchian_trend import DonchianTrendStrategy
from .cross_sectional_momentum import CrossSectionalMomentumStrategy
from ..models.signal import Signal
from ..brokers.manager import broker_manager
from ..ml.meta_model import MLMetaLayer
from sqlmodel import Session

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
        adapter = broker_manager.get_adapter(broker)
        if not adapter:
            return []

        if not adapter.connected:
            await adapter.connect()

        data = pd.DataFrame({
            'close': [100.0 + i * 0.1 for i in range(100)] + [100.0 - 1.0, 100.0 + 0.5],
            'open': [100.0 + i * 0.1 for i in range(100)] + [100.0, 100.0 - 1.0],
            'high': [100.0 + i * 0.1 + 0.2 for i in range(100)] + [100.0 + 0.2, 100.0 + 0.6],
            'low': [100.0 + i * 0.1 - 0.2 for i in range(100)] + [100.0 - 1.2, 100.0 - 1.2]
        })

        all_signals = []
        for strat in self.strategies:
            signals = await strat.analyze(symbol, timeframe, data)
            for s in signals:
                s.broker = broker
                # Create a new session or refresh to avoid detached instance issues if needed
                # but let's just use it
                all_signals.append(s)

        # Split execution engines vs filters
        execution_signals = [s for s in all_signals if s.strategy_role == "entry_engine"]
        regime_signals = [s for s in all_signals if s.strategy_role == "regime_filter"]

        # Apply filters (Example: Only allow entry if regime matches side)
        final_signals = []
        for es in execution_signals:
            # Check for regime confluence on same symbol/timeframe
            matches = [rs for rs in regime_signals if rs.symbol == es.symbol and rs.timeframe == es.timeframe]
            if not matches or matches[0].side == es.side:
                final_signals.append(es)

        # Rank via ML Meta Layer
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
