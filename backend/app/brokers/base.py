from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
from ..models.symbol import Symbol

class BrokerAdapter(ABC):
    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_symbols(self) -> List[Symbol]:
        pass

    @abstractmethod
    async def get_latest_tick(self, symbol: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_history(self, symbol: str, timeframe: str, count: int) -> Optional[pd.DataFrame]:
        pass
