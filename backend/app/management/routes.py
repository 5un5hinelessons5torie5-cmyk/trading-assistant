from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from .position_tracker import PositionTracker
from ..models.execution import Position
from typing import List

router = APIRouter(prefix="/management", tags=["Management"])

@router.get("/positions", response_model=List[Position])
async def get_positions(session: Session = Depends(get_session)):
    return session.exec(select(Position)).all()

@router.post("/sync-positions/{broker_name}")
async def sync_positions(broker_name: str, session: Session = Depends(get_session)):
    tracker = PositionTracker(session)
    await tracker.sync_with_broker(broker_name)
    return {"status": "synced"}

@router.post("/update-position/{pos_id}")
async def update_position(pos_id: int, sl: float = None, tp: float = None, session: Session = Depends(get_session)):
    pos = session.get(Position, pos_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")

    if sl is not None:
        pos.stop_loss = sl
    if tp is not None:
        pos.take_profit = tp

    session.add(pos)
    session.commit()
    return pos
