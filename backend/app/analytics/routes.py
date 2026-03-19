from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from .engine import AnalyticsEngine
from typing import Dict, Any

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
async def get_summary(session: Session = Depends(get_session)):
    engine = AnalyticsEngine(session)
    return await engine.get_performance_summary()
