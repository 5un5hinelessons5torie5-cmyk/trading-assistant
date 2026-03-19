from typing import List
import pandas as pd
from .base import Strategy
from ..models.signal import Signal

class BreakoutRetestStrategy(Strategy):
    def __init__(self):
        super().__init__("breakout_retest", "Breakout Retest", "entry_engine")

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        if len(data) < 20: return []

        last_close = float(data['close'].iloc[-1])
        high_20 = float(data['high'].iloc[-20:-1].max())

        signals = []
        if last_close > high_20:
            signals.append(Signal(
                strategy_id=self.strategy_id,
                strategy_label=self.display_label,
                strategy_role=self.role,
                broker="Exness", symbol=symbol, timeframe=timeframe,
                side="buy", entry_price=last_close,
                stop_loss=last_close * 0.99, take_profit=last_close * 1.03,
                tp_ladder='[]', confidence=0.75, setup_confirmation=True,
                queue_quality=0.7, confluence_text="Breakout of 20-bar high",
                execution_readiness=True
            ))
        return signals
