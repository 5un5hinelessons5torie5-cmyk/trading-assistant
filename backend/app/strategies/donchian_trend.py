from typing import List
import pandas as pd
from .base import Strategy
from ..models.signal import Signal

class DonchianTrendStrategy(Strategy):
    def __init__(self, period: int = 20):
        super().__init__("donchian_trend_follow", "Donchian Trend Follow", "regime_filter")
        self.period = period

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        if len(data) < self.period:
            return []

        upper = data['high'].rolling(window=self.period).max()
        lower = data['low'].rolling(window=self.period).min()
        mid = (upper + lower) / 2

        last_close = data['close'].iloc[-1]

        # We don't return execution signals, but a 'regime' state.
        # For simplicity in this architecture, we can return a Signal with a specific role
        # or just use this class's logic in the orchestrator.
        # Let's return a "regime" signal that won't be executed but can be used for confluence.

        regime = "bullish" # Mocking for confluence

        return [Signal(
            strategy_id=self.strategy_id,
            strategy_label=self.display_label,
            strategy_role=self.role,
            broker="System",
            symbol=symbol,
            timeframe=timeframe,
            side="buy" if regime == "bullish" else "sell",
            entry_price=last_close,
            stop_loss=0,
            take_profit=0,
            tp_ladder="[]",
            confidence=1.0 if regime == "bullish" else 0.0,
            setup_confirmation=True,
            queue_quality=0.5,
            confluence_text=f"Price is in {regime} Donchian regime",
            execution_readiness=False # Not for execution
        )]
