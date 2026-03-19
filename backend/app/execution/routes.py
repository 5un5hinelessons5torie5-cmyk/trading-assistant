from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from .queue_manager import QueueManager
from ..models.execution import ExecutionQueueItem
from ..models.signal import Signal
from typing import List, Dict, Any

router = APIRouter(prefix="/execution", tags=["Execution"])

@router.post("/queue-add/{signal_id}")
async def add_to_queue(signal_id: int, risk_percent: float = 1.0, session: Session = Depends(get_session)):
    signal = session.get(Signal, signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    manager = QueueManager(session)
    queue_item = await manager.add_to_queue(signal, risk_percent)
    return queue_item

@router.get("/queue", response_model=List[ExecutionQueueItem])
async def get_queue(session: Session = Depends(get_session)):
    return session.exec(select(ExecutionQueueItem)).all()

@router.post("/execute/{item_id}")
async def execute_queue_item(item_id: int, session: Session = Depends(get_session)):
    manager = QueueManager(session)
    result = await manager.execute_item(item_id)
    return result

@router.post("/queue-update/{item_id}")
async def update_queue_status(item_id: int, status: str, session: Session = Depends(get_session)):
    item = session.get(ExecutionQueueItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.status = status
    session.add(item)
    session.commit()
    return item
