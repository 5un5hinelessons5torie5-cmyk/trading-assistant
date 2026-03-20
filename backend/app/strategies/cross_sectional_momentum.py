from typing import List
import pandas as pd
from .base import Strategy
from ..models.signal import Signal

class CrossSectionalMomentumStrategy(Strategy):
    def __init__(self, lookback: int = 100):
        super().__init__("cross_sectional_momentum_long_only", "Cross-Sectional Momentum (Long Only)", "selection_layer")
        self.lookback = lookback

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        if len(data) < self.lookback:
            return []

        # Momentum = (Current Price / Price X bars ago) - 1
        start_price = data['close'].iloc[-self.lookback]
        curr_price = data['close'].iloc[-1]
        momentum = (curr_price / start_price) - 1

        return [Signal(
            strategy_id=self.strategy_id,
            strategy_label=self.display_label,
            strategy_role=self.role,
            broker="System",
            symbol=symbol,
            timeframe=timeframe,
            side="buy" if momentum > 0 else "sell",
            entry_price=curr_price,
            stop_loss=0,
            take_profit=0,
            tp_ladder="[]",
            confidence=float(momentum), # Use momentum as confidence score
            setup_confirmation=momentum > 0,
            queue_quality=0.5,
            confluence_text=f"Cross-sectional momentum score: {momentum:.4f}",
            execution_readiness=False
        )]
