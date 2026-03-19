from typing import List
import pandas as pd
from .base import Strategy
from ..models.signal import Signal

class DonchianTrendStrategy(Strategy):
    def __init__(self):
        super().__init__("donchian_trend_follow", "Donchian Trend Follow", "regime_filter")

    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        return []
