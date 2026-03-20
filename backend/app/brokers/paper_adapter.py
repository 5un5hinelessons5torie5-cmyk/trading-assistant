from typing import List, Dict, Any, Optional
import pandas as pd
from .base import BrokerAdapter
from ..models.symbol import Symbol

class PaperAdapter(BrokerAdapter):
    def __init__(self, initial_balance: float = 100000.0):
        self.balance = initial_balance
        self.equity = initial_balance
        self.positions = []
        self.next_ticket = 1000000
        self.connected = False

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def disconnect(self):
        self.connected = False

    async def get_account_info(self) -> Dict[str, Any]:
        return {"balance": self.balance, "equity": self.equity, "currency": "USD"}

    async def get_symbols(self) -> List[Symbol]:
        return [Symbol(name="EURUSD_PAPER", broker="Paper", asset_group="forex", status="live_ready")]

    async def get_latest_tick(self, symbol: str) -> Dict[str, Any]:
        return {"bid": 1.0, "ask": 1.0001, "last": 1.0, "time": 0}

    async def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket = str(self.next_ticket)
        self.next_ticket += 1
        return {"retcode": 10009, "order": ticket}

    async def get_positions(self) -> List[Dict[str, Any]]:
        return self.positions

    async def get_history(self, symbol: str, timeframe: str, count: int) -> Optional[pd.DataFrame]:
        return pd.DataFrame({
            'close': [1.0 + i * 0.0001 for i in range(count)],
            'high': [1.0005 + i * 0.0001 for i in range(count)],
            'low': [0.9995 + i * 0.0001 for i in range(count)],
            'open': [1.0 + i * 0.0001 for i in range(count)]
        })
