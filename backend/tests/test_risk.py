from app.execution.risk import calculate_volume, calculate_risk_reward
from app.models.symbol import Symbol
import pytest

def test_calculate_risk_reward():
    assert calculate_risk_reward(100, 90, 120) == pytest.approx(2.0)
    assert calculate_risk_reward(1.0850, 1.0840, 1.0870) == pytest.approx(2.0)

def test_calculate_volume_forex():
    symbol = Symbol(name="EURUSD", broker="Exness", asset_group="forex", min_volume=0.01, max_volume=100.0, volume_step=0.01)
    # Risk $100 on 10 pips (0.0010)
    # 100 / 0.0010 / 100000 = 1.0 lot
    volume = calculate_volume(10000.0, 1.0, 1.0850, 1.0840, symbol)
    assert volume == pytest.approx(1.0)
