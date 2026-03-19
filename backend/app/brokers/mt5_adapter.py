import logging
from typing import List, Dict, Any, Optional
from .base import BrokerAdapter
from ..models.symbol import Symbol

# Mocking MT5 for environments where it is not available (like Linux/Sandbox)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logging.warning("MetaTrader5 package not found. MT5Adapter will run in mock mode.")

class MT5Adapter(BrokerAdapter):
    def __init__(self, login: int = None, password: str = None, server: str = None):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False

    async def connect(self) -> bool:
        if not MT5_AVAILABLE:
            self.connected = True
            return True

        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            logging.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False

        self.connected = True
        return True

    async def disconnect(self):
        if MT5_AVAILABLE:
            mt5.shutdown()
        self.connected = False

    async def get_account_info(self) -> Dict[str, Any]:
        if not self.connected:
            return {}

        if not MT5_AVAILABLE:
            return {
                "balance": 10000.0,
                "equity": 10000.0,
                "margin": 0.0,
                "margin_free": 10000.0,
                "currency": "USD"
            }

        acc = mt5.account_info()
        if acc is None:
            return {}

        return acc._asdict()

    async def get_symbols(self) -> List[Symbol]:
        if not self.connected:
            return []

        if not MT5_AVAILABLE:
            # Mock some symbols for Exness
            return [
                Symbol(name="EURUSD", broker="Exness", asset_group="forex", status="live_ready"),
                Symbol(name="XAUUSD", broker="Exness", asset_group="metals", status="live_ready"),
                Symbol(name="BTCUSD", broker="Exness", asset_group="crypto", status="research_only"),
            ]

        mt5_symbols = mt5.symbols_get()
        symbols = []
        for s in mt5_symbols:
            # Safely handle path splitting
            path_parts = s.path.split("\\")
            asset_group = path_parts[0] if len(path_parts) > 0 else "other"

            symbols.append(Symbol(
                name=s.name,
                broker="Exness",
                asset_group=asset_group,
                status="live_ready" if s.visible else "research_only",
                min_volume=s.volume_min,
                max_volume=s.volume_max,
                volume_step=s.volume_step
            ))
        return symbols

    async def get_latest_tick(self, symbol: str) -> Dict[str, Any]:
        if not self.connected:
            return {}

        if not MT5_AVAILABLE:
            return {"bid": 1.0850, "ask": 1.0852, "last": 1.0851, "time": 0}

        tick = mt5.symbol_info_tick(symbol)
        return tick._asdict() if tick else {}

    async def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.connected or not MT5_AVAILABLE:
            return {"status": "mock_executed", "ticket": "123456"}

        result = mt5.order_send(order_data)
        if result is None:
            return {"status": "failed", "error": str(mt5.last_error())}
        return result._asdict()

    async def get_positions(self) -> List[Dict[str, Any]]:
        if not self.connected:
            return []

        if not MT5_AVAILABLE:
            return []

        positions = mt5.positions_get()
        return [p._asdict() for p in positions] if positions else []
