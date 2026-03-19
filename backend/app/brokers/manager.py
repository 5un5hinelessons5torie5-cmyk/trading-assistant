from typing import Dict, List, Any, Optional
from .base import BrokerAdapter
from .mt5_adapter import MT5Adapter
from .paper_adapter import PaperAdapter
from ..models.symbol import Symbol

class BrokerManager:
    def __init__(self):
        self._adapters: Dict[str, BrokerAdapter] = {
            "Paper": PaperAdapter(),
            "Exness": MT5Adapter()
        }

    def get_adapter(self, name: str) -> Optional[BrokerAdapter]:
        return self._adapters.get(name)

    async def get_all_symbols(self) -> List[Symbol]:
        all_symbols = []
        for name, adapter in self._adapters.items():
            if not adapter.connected:
                await adapter.connect()
            symbols = await adapter.get_symbols()
            for s in symbols:
                # Add broker name if missing
                s.broker = name
            all_symbols.extend(symbols)
        return all_symbols

    async def disconnect_all(self):
        for adapter in self._adapters.values():
            await adapter.disconnect()

broker_manager = BrokerManager()
