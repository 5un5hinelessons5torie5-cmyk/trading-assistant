import pytest
import pandas as pd
from app.strategies.ema_pullback import EMAPullbackStrategy

@pytest.mark.asyncio
async def test_ema_pullback_analysis():
    strat = EMAPullbackStrategy()
    data = pd.DataFrame({
        'close': [100.0 + i * 0.1 for i in range(100)]
    })
    signals = await strat.analyze("EURUSD", "H1", data)
    assert len(signals) > 0
    assert signals[0].strategy_id == "ema_pullback"
