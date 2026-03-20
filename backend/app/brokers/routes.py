from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models.symbol import Symbol
from .manager import broker_manager
from .eligibility import get_symbol_status, get_blocked_reason
from typing import List, Dict, Any

router = APIRouter(prefix="/brokers", tags=["Brokers"])

@router.get("/symbols", response_model=List[Symbol])
async def get_all_symbols(session: Session = Depends(get_session)):
    symbols = await broker_manager.get_all_symbols()

    for s in symbols:
        # Get live tick for eligibility
        adapter = broker_manager.get_adapter(s.broker)
        tick = await adapter.get_latest_tick(s.name) if adapter else {}

        # Determine status/blocked reason
        effective_status = get_symbol_status(s, tick, {"is_open": True})
        blocked_reason = get_blocked_reason(s, tick, {"is_open": True})

        existing = session.exec(select(Symbol).where(Symbol.name == s.name)).first()
        if existing:
            existing.status = effective_status
            existing.blocked_reason = blocked_reason
            session.add(existing)
        else:
            s.status = effective_status
            s.blocked_reason = blocked_reason
            session.add(s)

    session.commit()
    return session.exec(select(Symbol)).all()

@router.get("/account-info/{broker_name}")
async def get_account_info(broker_name: str):
    adapter = broker_manager.get_adapter(broker_name)
    if not adapter:
        return {"error": "Broker not found"}
    if not adapter.connected: await adapter.connect()
    return await adapter.get_account_info()

@router.get("/positions/{broker_name}")
async def get_positions(broker_name: str):
    adapter = broker_manager.get_adapter(broker_name)
    if not adapter:
        return {"error": "Broker not found"}
    if not adapter.connected: await adapter.connect()
    return await adapter.get_positions()
