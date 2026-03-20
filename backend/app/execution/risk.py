from typing import Dict, Any, Optional
from ..models.symbol import Symbol

def calculate_volume(
    balance: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float,
    symbol_info: Symbol
) -> float:
    if entry_price == stop_loss:
        return symbol_info.min_volume

    risk_amount = balance * (risk_percent / 100.0)
    price_risk = abs(entry_price - stop_loss)

    # Simple volume calculation (for Forex, 1 lot is usually 100,000 units)
    # This needs to be adjusted based on asset group and contract size
    raw_volume = risk_amount / price_risk / 100000.0 if symbol_info.asset_group == "forex" else risk_amount / price_risk

    # Normalize to broker constraints
    volume = max(symbol_info.min_volume, min(symbol_info.max_volume, raw_volume))

    # Snap to volume step
    if symbol_info.volume_step > 0:
        volume = round(volume / symbol_info.volume_step) * symbol_info.volume_step

    return float(volume)

def calculate_risk_reward(entry_price: float, stop_loss: float, take_profit: float) -> float:
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    return float(reward / risk) if risk > 0 else 0.0
