from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from .orchestrator import SignalOrchestrator
from ..models.signal import Signal
from typing import List, Optional, Any

router = APIRouter(prefix="/strategies", tags=["Strategies"])

@router.post("/scan/{symbol}/{timeframe}")
async def run_scan(symbol: str, timeframe: str, broker: str = "Exness", session: Session = Depends(get_session)):
    orchestrator = SignalOrchestrator(session)
    signals = await orchestrator.run_scan(symbol, timeframe, broker)
    # Manual conversion to dict to avoid SQLModel issues in return
    return [s.dict() for s in signals]

@router.get("/signals")
async def get_signals(session: Session = Depends(get_session)):
    return session.exec(select(Signal)).all()

@router.post("/auto-best-setup/{symbol}")
async def auto_best_setup(symbol: str, timeframes: str = "H1,H4,D1", broker: str = "Exness", session: Session = Depends(get_session)):
    tf_list = timeframes.split(",")
    orchestrator = SignalOrchestrator(session)
    best_signal = await orchestrator.auto_best_setup_scan(symbol, tf_list, broker)
    return best_signal
