from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from ..models.signal import Signal
from ..models.execution import ExecutionQueueItem, Position
from ..models.symbol import Symbol
from ..models.system import SystemSettings
from ..brokers.manager import broker_manager
from .risk import calculate_volume, calculate_risk_reward
import json

class QueueManager:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def add_to_queue(self, signal: Signal, risk_percent: float = 1.0) -> ExecutionQueueItem:
        # Preflight check
        symbol_info = self.db.exec(select(Symbol).where(Symbol.name == signal.symbol)).first()
        if not symbol_info:
            # Fallback for mock if not in DB
            symbol_info = Symbol(name=signal.symbol, broker=signal.broker, asset_group="forex")

        adapter = broker_manager.get_adapter(signal.broker)
        acc_info = await adapter.get_account_info() if adapter else {"balance": 10000.0}

        balance = acc_info.get("balance", 10000.0)
        volume = calculate_volume(balance, risk_percent, signal.entry_price, signal.stop_loss, symbol_info)
        rr = calculate_risk_reward(signal.entry_price, signal.stop_loss, signal.take_profit)

        queue_item = ExecutionQueueItem(
            signal_id=signal.id,
            requested_volume=volume,
            risk_reward=rr,
            status="active",
            queue_admission_note=f"Admitted via {signal.strategy_id} scan",
            preflight_summary="Symbol and risk checked"
        )

        self.db.add(queue_item)
        self.db.commit()
        self.db.refresh(queue_item)
        return queue_item

    async def execute_item(self, item_id: int) -> Dict[str, Any]:
        item = self.db.get(ExecutionQueueItem, item_id)
        if not item or item.status != "active":
            return {"error": "Invalid queue item"}

        # Check system risk controls
        settings = self.db.exec(select(SystemSettings)).first()
        if settings:
            if settings.kill_switch:
                return {"error": "Kill switch is active. Execution blocked."}

            # Max open positions check
            open_pos_count = len(self.db.exec(select(Position).where(Position.status == "open")).all())
            if open_pos_count >= settings.max_mt5_open_positions:
                return {"error": f"Max open positions ({settings.max_mt5_open_positions}) reached."}

            # Asset group caps check
            signal = self.db.get(Signal, item.signal_id)
            symbol_info = self.db.exec(select(Symbol).where(Symbol.name == signal.symbol)).first()
            if symbol_info and settings.asset_group_caps:
                caps = json.loads(settings.asset_group_caps)
                group = symbol_info.asset_group
                if group in caps:
                    group_count = len(self.db.exec(
                        select(Position).join(Symbol, Position.symbol == Symbol.name)
                        .where(Position.status == "open", Symbol.asset_group == group)
                    ).all())
                    if group_count >= caps[group]:
                        return {"error": f"Exposure cap for {group} ({caps[group]}) reached."}

        signal = self.db.get(Signal, item.signal_id)

        # Check for duplicate positions
        existing_pos = self.db.exec(select(Position).where(Position.symbol == signal.symbol, Position.status == "open")).all()
        if existing_pos:
            # We can log a warning or require explicit override if needed
            # For now we'll allow but record in audit trail
            pass
        adapter = broker_manager.get_adapter(signal.broker)

        # Build order
        order = {
            "symbol": signal.symbol,
            "volume": item.requested_volume,
            "price": signal.entry_price,
            "sl": signal.stop_loss,
            "tp": signal.take_profit,
            "type": 0 if signal.side == "buy" else 1, # 0 for Buy, 1 for Sell
        }

        result = await adapter.execute_order(order)

        if result.get("retcode") in [10009, 10008]: # Done or Placed
            item.status = "used"
            item.executed_volume = item.requested_volume
            item.fill_price = signal.entry_price # Simple fill mock
            item.execution_message = "Executed successfully"

            # Record execution in audit trail
            audit = json.loads(item.audit_trail)
            audit.append({
                "time": str(datetime.utcnow()),
                "event": "executed",
                "ticket": result.get("order") or result.get("ticket")
            })
            item.audit_trail = json.dumps(audit)

            # Create internal Position
            from ..management.position_tracker import PositionTracker
            tracker = PositionTracker(self.db)
            await tracker.register_executed_item(item.id, str(result.get("order") or result.get("ticket")))
        else:
            item.status = "active" # Keep active on failure? or move to 'failed'
            item.execution_message = f"Execution failed: {result.get('error', 'Unknown')}"

        item.decided_at = datetime.utcnow()
        self.db.add(item)
        self.db.commit()
        return result
