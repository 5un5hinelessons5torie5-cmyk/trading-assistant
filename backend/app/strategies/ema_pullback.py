from typing import List, Dict, Any
import pandas as pd
import numpy as np
from .base import Strategy
from ..models.signal import Signal

class EMAPullbackStrategy(Strategy):
    def __init__(self):
        super().__init__("ema_pullback", "Trend Reclaim Pullback", "entry_engine")

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        if len(data) < 50: return []

        # 1. EMA setup
        ema20 = data['close'].ewm(span=20, adjust=False).mean()
        ema50 = data['close'].ewm(span=50, adjust=False).mean()

        last_close = data['close'].iloc[-1]
        prev_close = data['close'].iloc[-2]

        signals = []

        # 2. Bullish Pullback: Price above EMA50, Crosses above EMA20
        if ema20.iloc[-1] > ema50.iloc[-1] and last_close > ema20.iloc[-1] and prev_close < ema20.iloc[-1]:
            atr = (data['high'] - data['low']).rolling(window=14).mean().iloc[-1]
            sl = last_close - (atr * 2)
            tp = last_close + (atr * 4)

            signals.append(Signal(
                strategy_id=self.strategy_id,
                strategy_label=self.display_label,
                strategy_role=self.role,
                broker="Exness",
                symbol=symbol,
                timeframe=timeframe,
                side="buy",
                entry_price=float(last_close),
                stop_loss=float(sl),
                take_profit=float(tp),
                tp_ladder="[]",
                confidence=0.85,
                setup_confirmation=True,
                queue_quality=0.8,
                confluence_text="Price reclaimed EMA20 with ATR-based targets",
                execution_readiness=True
            ))

        # 3. Bearish Pullback
        elif ema20.iloc[-1] < ema50.iloc[-1] and last_close < ema20.iloc[-1] and prev_close > ema20.iloc[-1]:
            atr = (data['high'] - data['low']).rolling(window=14).mean().iloc[-1]
            sl = last_close + (atr * 2)
            tp = last_close - (atr * 4)

            signals.append(Signal(
                strategy_id=self.strategy_id,
                strategy_label=self.display_label,
                strategy_role=self.role,
                broker="Exness",
                symbol=symbol,
                timeframe=timeframe,
                side="sell",
                entry_price=float(last_close),
                stop_loss=float(sl),
                take_profit=float(tp),
                tp_ladder="[]",
                confidence=0.85,
                setup_confirmation=True,
                queue_quality=0.8,
                confluence_text="Short reclaim of EMA20",
                execution_readiness=True
            ))

        return signals
