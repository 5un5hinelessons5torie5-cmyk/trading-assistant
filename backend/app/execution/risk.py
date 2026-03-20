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

    # Lot-based risk calculation
    # Forex: 1 lot = 100,000 units. Loss in Pips/Points needs translation to account currency.
    # Heuristic for major pairs where 1 pip = 0.0001: 1 lot risk is approx $10 per pip.
    # For robust volume, we'd ideally use broker-provided 'contract_size' and 'tick_value'.
    # Fallback to standard 100k contract size for forex if not specified.

    contract_size = 100000.0 if symbol_info.asset_group.lower() == "forex" else 1.0

    # Volume = Risk Amount / (Price Risk * Contract Size)
    raw_volume = risk_amount / (price_risk * contract_size)

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
