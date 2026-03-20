from typing import List, Dict, Any
import pandas as pd
import numpy as np
from .base import Strategy
from ..models.signal import Signal

class EMAPullbackStrategy(Strategy):
    def __init__(self):
        super().__init__("ema_pullback", "Trend Reclaim Pullback", "entry_engine")

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        if len(data) < 50:
            return []

        ema20 = data['close'].ewm(span=20, adjust=False).mean()
        ema50 = data['close'].ewm(span=50, adjust=False).mean()

        last_close = float(data['close'].iloc[-1])

        signals = []

        # Mock signal for testing
        sl = float(ema50.iloc[-1])
        tp = float(last_close + (last_close - sl) * 2)

        signal = Signal(
            strategy_id=self.strategy_id,
            strategy_label=self.display_label,
            strategy_role=self.role,
            broker="Exness",
            symbol=symbol,
            timeframe=timeframe,
            side="buy",
            entry_price=last_close,
            stop_loss=sl,
            take_profit=tp,
            tp_ladder='[]',
            confidence=0.8,
            setup_confirmation=True,
            queue_quality=0.75,
            confluence_text="Price reclaimed EMA20 in an uptrend",
            execution_readiness=True
        )
        signals.append(signal)

        return signals
