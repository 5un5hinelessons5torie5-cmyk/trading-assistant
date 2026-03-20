import pytest
import pandas as pd
import numpy as np
from app.strategies.ema_pullback import EMAPullbackStrategy

@pytest.mark.asyncio
async def test_ema_pullback_analysis():
    strat = EMAPullbackStrategy()

    # Create a trend followed by a pullback
    # Need high and low for ATR
    closes = [100.0 + i * 0.1 for i in range(80)] # Steady uptrend
    # Then a dip below EMA20 (which will be around 107.5)
    closes.extend([107.0, 106.0, 105.0])
    # Then a reclaim
    closes.extend([108.5])

    data = pd.DataFrame({
        'close': closes,
        'high': [c + 0.1 for c in closes],
        'low': [c - 0.1 for c in closes]
    })

    signals = await strat.analyze("EURUSD", "H1", data)
    assert len(signals) > 0
    assert signals[0].strategy_id == "ema_pullback"
    assert signals[0].side == "buy"
