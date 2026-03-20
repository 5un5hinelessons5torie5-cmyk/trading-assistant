from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from ..models.execution import Position, ExecutionQueueItem
from ..brokers.manager import broker_manager
import logging

class PositionTracker:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def sync_with_broker(self, broker_name: str):
        adapter = broker_manager.get_adapter(broker_name)
        if not adapter: return
        if not adapter.connected: await adapter.connect()

        broker_positions = await adapter.get_positions()

        # 1. Update existing and register new
        active_tickets = []
        for bp in broker_positions:
            ticket = str(bp.get("ticket"))
            active_tickets.append(ticket)

            existing = self.db.exec(select(Position).where(Position.broker_ticket == ticket)).first()
            if existing:
                existing.current_price = bp.get("price_current", existing.current_price)
                existing.pnl = bp.get("profit", existing.pnl)
                existing.status = "open"
                self.db.add(existing)
            else:
                new_pos = Position(
                    broker_ticket=ticket,
                    symbol=bp.get("symbol"),
                    side="buy" if bp.get("type") == 0 else "sell",
                    volume=bp.get("volume"),
                    entry_price=bp.get("price_open"),
                    current_price=bp.get("price_current", 0.0),
                    stop_loss=bp.get("sl", 0.0),
                    take_profit=bp.get("tp", 0.0),
                    tp_ladder='[]',
                    is_manual=True,
                    status="open"
                )
                self.db.add(new_pos)

        # 2. Mark closed positions
        open_in_db = self.db.exec(select(Position).where(Position.status == "open")).all()
        for pos in open_in_db:
            if pos.broker_ticket not in active_tickets:
                # Reconciliation: position no longer at broker
                pos.status = "closed"
                pos.closed_at = datetime.utcnow()
                self.db.add(pos)
                logging.info(f"Reconciled closed position: {pos.broker_ticket}")

        self.db.commit()

    async def register_executed_item(self, item_id: int, ticket: str):
        item = self.db.get(ExecutionQueueItem, item_id)
        from ..models.signal import Signal
        signal = self.db.get(Signal, item.signal_id)

        new_pos = Position(
            queue_item_id=item_id,
            broker_ticket=ticket,
            symbol=signal.symbol,
            side=signal.side,
            volume=item.executed_volume,
            entry_price=item.fill_price or signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            tp_ladder=signal.tp_ladder,
            status="open"
        )
        self.db.add(new_pos)
        self.db.commit()
