import asyncio
import logging
from datetime import datetime
from sqlmodel import Session, select
from ..database import engine
from ..strategies.orchestrator import SignalOrchestrator
from ..models.symbol import Symbol
from ..models.execution import Position
from ..ml.meta_model import ml_trainer

class SchedulerLoop:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                await self.run_tasks()
            except Exception as e:
                logging.error(f"Error in scheduler loop: {e}")
            await asyncio.sleep(self.interval)

    async def run_tasks(self):
        logging.info(f"Running scheduled tasks at {datetime.utcnow()}")
        with Session(engine) as session:
            # Task 1: Scan for signals on live ready symbols
            symbols = session.exec(select(Symbol).where(Symbol.status == "live_ready")).all()
            orchestrator = SignalOrchestrator(session)
            for sym in symbols:
                # Basic scan on H1. In a production system, this would be more dynamic.
                await orchestrator.run_scan(sym.name, "H1", sym.broker)

            # Task 2: Sync Positions (Reconciliation)
            from ..management.position_tracker import PositionTracker
            tracker = PositionTracker(session)
            await tracker.sync_with_broker("Exness")
            await tracker.sync_with_broker("Paper")

            # Task 3: Periodic ML Retraining from closed history
            closed_positions = session.exec(select(Position).where(Position.status == "closed")).all()
            if closed_positions:
                ml_trainer.train_from_history(closed_positions)

            session.commit()

    def stop(self):
        self.running = False

scheduler = SchedulerLoop()
