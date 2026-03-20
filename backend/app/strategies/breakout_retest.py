from typing import List
import pandas as pd
from .base import Strategy
from ..models.signal import Signal

class BreakoutRetestStrategy(Strategy):
    def __init__(self):
        super().__init__("breakout_retest", "Breakout Retest", "entry_engine")

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        if len(data) < 40: return []

        # Identify local high/low (Resistance/Support)
        resistance = data['high'].iloc[-40:-10].max()
        last_close = data['close'].iloc[-1]

        signals = []
        # Simplified breakout logic
        if last_close > resistance:
            sl = float(data['low'].iloc[-10:].min())
            tp = last_close + (last_close - sl) * 3

            signals.append(Signal(
                strategy_id=self.strategy_id,
                strategy_label=self.display_label,
                strategy_role=self.role,
                broker="Exness", symbol=symbol, timeframe=timeframe,
                side="buy", entry_price=float(last_close),
                stop_loss=float(sl), take_profit=float(tp),
                tp_ladder="[]", confidence=0.78, setup_confirmation=True,
                queue_quality=0.7, confluence_text=f"Bullish breakout above {resistance:.5f}",
                execution_readiness=True
            ))
        return signals
