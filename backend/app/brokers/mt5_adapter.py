import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from .base import BrokerAdapter
from ..models.symbol import Symbol

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

        self.tf_map = {
            "M1": mt5.TIMEFRAME_M1 if MT5_AVAILABLE else 1,
            "M5": mt5.TIMEFRAME_M5 if MT5_AVAILABLE else 5,
            "M15": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
            "H1": mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 60,
            "H4": mt5.TIMEFRAME_H4 if MT5_AVAILABLE else 240,
            "D1": mt5.TIMEFRAME_D1 if MT5_AVAILABLE else 1440,
        }

    async def connect(self) -> bool:
        if not MT5_AVAILABLE:
            self.connected = True
            return True

        if not mt5.initialize():
            logging.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False

        if self.login:
            if not mt5.login(login=self.login, password=self.password, server=self.server):
                logging.error(f"MT5 login failed: {mt5.last_error()}")
                return False

        self.connected = True
        return True

    async def disconnect(self):
        if MT5_AVAILABLE:
            mt5.shutdown()
        self.connected = False

    async def get_account_info(self) -> Dict[str, Any]:
        if not self.connected: return {}
        if not MT5_AVAILABLE:
            return {"balance": 10000.0, "equity": 10000.0, "currency": "USD"}

        acc = mt5.account_info()
        return acc._asdict() if acc else {}

    async def get_symbols(self) -> List[Symbol]:
        if not self.connected: return []
        if not MT5_AVAILABLE:
            return [Symbol(name="EURUSD", broker="Exness", asset_group="forex", status="live_ready")]

        mt5_symbols = mt5.symbols_get()
        symbols = []
        for s in mt5_symbols:
            symbols.append(Symbol(
                name=s.name,
                broker="Exness",
                asset_group=s.path.split("\\")[0] if len(s.path.split("\\")) > 0 else "other",
                status="live_ready" if s.visible else "research_only",
                min_volume=s.volume_min,
                max_volume=s.volume_max,
                volume_step=s.volume_step
            ))
        return symbols

    async def get_latest_tick(self, symbol: str) -> Dict[str, Any]:
        if not self.connected: return {}
        if not MT5_AVAILABLE:
            return {"bid": 1.0850, "ask": 1.0852, "last": 1.0851, "time": 0}

        tick = mt5.symbol_info_tick(symbol)
        return tick._asdict() if tick else {}

    async def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.connected: return {"error": "Not connected"}
        if not MT5_AVAILABLE:
            return {"retcode": 10009, "ticket": "123456"}

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order_data["symbol"],
            "volume": float(order_data["volume"]),
            "type": mt5.ORDER_TYPE_BUY if order_data["type"] == 0 else mt5.ORDER_TYPE_SELL,
            "price": float(order_data["price"]),
            "sl": float(order_data["sl"]),
            "tp": float(order_data["tp"]),
            "magic": 123456,
            "comment": "Workstation Exec",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return result._asdict() if result else {"error": "Order send failed"}

    async def get_positions(self) -> List[Dict[str, Any]]:
        if not self.connected: return []
        if not MT5_AVAILABLE: return []
        positions = mt5.positions_get()
        return [p._asdict() for p in positions] if positions else []

    async def get_history(self, symbol: str, timeframe: str, count: int) -> Optional[pd.DataFrame]:
        if not self.connected: return None
        tf = self.tf_map.get(timeframe, mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 60)

        if not MT5_AVAILABLE:
            # Mock data
            return pd.DataFrame({
                'close': [1.0800 + i * 0.0001 for i in range(count)],
                'high': [1.0805 + i * 0.0001 for i in range(count)],
                'low': [1.0795 + i * 0.0001 for i in range(count)],
                'open': [1.0800 + i * 0.0001 for i in range(count)]
            })

        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        if rates is None or len(rates) == 0:
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
