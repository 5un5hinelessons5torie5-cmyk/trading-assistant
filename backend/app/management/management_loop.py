import asyncio
import logging
from datetime import datetime
from sqlmodel import Session, select
from ..database import engine
from ..models.execution import Position
from ..brokers.manager import broker_manager
import json

class ManagementLoop:
    def __init__(self, interval: int = 15):
        self.interval = interval
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                await self.manage_positions()
            except Exception as e:
                logging.error(f"Error in management loop: {e}")
            await asyncio.sleep(self.interval)

    async def manage_positions(self):
        with Session(engine) as session:
            positions = session.exec(select(Position).where(Position.status == "open")).all()
            for pos in positions:
                broker = "Exness" if not pos.is_paper else "Paper"
                adapter = broker_manager.get_adapter(broker)
                tick = await adapter.get_latest_tick(pos.symbol)

                if not tick or "last" not in tick: continue
                current_price = tick["last"]
                pos.current_price = current_price

                # 1. Break-even check
                if not pos.is_breakeven_activated:
                    # If price moved in profit by some amount
                    if pos.side == "buy":
                        if current_price > pos.entry_price + 0.0050:
                            pos.stop_loss = pos.entry_price
                            pos.is_breakeven_activated = True
                    else:
                        if current_price < pos.entry_price - 0.0050:
                            pos.stop_loss = pos.entry_price
                            pos.is_breakeven_activated = True

                # 2. Check for close (SL/TP)
                if (pos.side == "buy" and current_price <= pos.stop_loss) or (pos.side == "sell" and current_price >= pos.stop_loss):
                    pos.status = "closed"
                    pos.closed_at = datetime.utcnow()
                    pos.pnl = (current_price - pos.entry_price) * pos.volume * 100000
                elif (pos.side == "buy" and current_price >= pos.take_profit) or (pos.side == "sell" and current_price <= pos.take_profit):
                    pos.status = "closed"
                    pos.closed_at = datetime.utcnow()
                    pos.pnl = (pos.take_profit - pos.entry_price) * pos.volume * 100000

                session.add(pos)
            session.commit()

management_loop = ManagementLoop()
