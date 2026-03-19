from typing import List, Dict, Any, Optional
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
        return {
            "balance": self.balance,
            "equity": self.equity,
            "margin": 0.0,
            "margin_free": self.equity,
            "currency": "USD"
        }

    async def get_symbols(self) -> List[Symbol]:
        # Return a standard list for paper trading
        return [
            Symbol(name="EURUSD_PAPER", broker="Paper", asset_group="forex", status="live_ready"),
            Symbol(name="XAUUSD_PAPER", broker="Paper", asset_group="metals", status="live_ready"),
            Symbol(name="BTCUSD_PAPER", broker="Paper", asset_group="crypto", status="live_ready"),
        ]

    async def get_latest_tick(self, symbol: str) -> Dict[str, Any]:
        return {"bid": 1.0, "ask": 1.0001, "last": 1.0, "time": 0}

    async def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket = str(self.next_ticket)
        self.next_ticket += 1

        position = {
            "ticket": ticket,
            "symbol": order_data.get("symbol"),
            "type": order_data.get("type"),
            "volume": order_data.get("volume"),
            "price_open": order_data.get("price"),
            "sl": order_data.get("sl"),
            "tp": order_data.get("tp"),
            "time": 0,
            "profit": 0.0
        }
        self.positions.append(position)
        return {"retcode": 10009, "comment": "Paper order done", "order": ticket, "deal": ticket}

    async def get_positions(self) -> List[Dict[str, Any]]:
        return self.positions
