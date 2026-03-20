from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.signal import Signal
import pandas as pd

class Strategy(ABC):
    def __init__(self, strategy_id: str, display_label: str, role: str):
        self.strategy_id = strategy_id
        self.display_label = display_label
        self.role = role

    @abstractmethod
    async def analyze(self, symbol: str, timeframe: str, data: pd.DataFrame) -> List[Signal]:
        pass
