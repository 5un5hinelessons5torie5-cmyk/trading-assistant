import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..strategies.base import Strategy

class BacktestEngine:
    def __init__(self, spread_pips: float = 2.0, commission_per_lot: float = 7.0):
        self.spread = spread_pips / 10000.0 # Standard forex pips
        self.commission = commission_per_lot

    async def run(self, strategy: Strategy, data: pd.DataFrame) -> Dict[str, Any]:
        trades = []
        # Sliding window for strategy analysis
        for i in range(50, len(data)):
            window = data.iloc[:i]
            signals = await strategy.analyze("BACKTEST", "H1", window)

            for s in signals:
                if s.strategy_role != "entry_engine": continue

                # Simulate execution from i+1 onwards
                entry_idx = i
                entry_price = s.entry_price + (self.spread / 2) if s.side == "buy" else s.entry_price - (self.spread / 2)

                # Check outcome
                outcome = None
                for j in range(i + 1, len(data)):
                    curr_high = data.iloc[j]['high']
                    curr_low = data.iloc[j]['low']

                    if s.side == "buy":
                        if curr_low <= s.stop_loss:
                            outcome = "loss"
                            exit_price = s.stop_loss
                            break
                        if curr_high >= s.take_profit:
                            outcome = "win"
                            exit_price = s.take_profit
                            break
                    else:
                        if curr_high >= s.stop_loss:
                            outcome = "loss"
                            exit_price = s.stop_loss
                            break
                        if curr_low <= s.take_profit:
                            outcome = "win"
                            exit_price = s.take_profit
                            break

                if outcome:
                    pnl = (exit_price - entry_price) if s.side == "buy" else (entry_price - exit_price)
                    trades.append({
                        "entry_time": data.index[i] if isinstance(data.index[i], datetime) else str(i),
                        "outcome": outcome,
                        "pnl_pips": pnl * 10000.0,
                        "r_multiple": pnl / abs(s.entry_price - s.stop_loss) if abs(s.entry_price - s.stop_loss) > 0 else 0
                    })

        if not trades:
            return {"win_rate": 0, "profit_factor": 0, "trades_count": 0}

        wins = [t for t in trades if t['outcome'] == "win"]
        losses = [t for t in trades if t['outcome'] == "loss"]

        win_rate = len(wins) / len(trades)
        gross_profit = sum([t['pnl_pips'] for t in wins])
        gross_loss = abs(sum([t['pnl_pips'] for t in losses]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        return {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "trades_count": len(trades),
            "trades": trades[:10] # Return samples
        }
