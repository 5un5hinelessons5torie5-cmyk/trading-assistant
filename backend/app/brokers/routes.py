from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models.symbol import Symbol
from ..models.broker import BrokerAccount
from .manager import broker_manager
from .eligibility import get_symbol_status, get_blocked_reason
from typing import List, Dict, Any

router = APIRouter(prefix="/brokers", tags=["Brokers"])

@router.post("/accounts", response_model=BrokerAccount)
async def create_account(account: BrokerAccount, session: Session = Depends(get_session)):
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/accounts", response_model=List[BrokerAccount])
async def get_accounts(session: Session = Depends(get_session)):
    return session.exec(select(BrokerAccount)).all()

@router.post("/test-connection/{account_id}")
async def test_connection(account_id: int, session: Session = Depends(get_session)):
    account = session.get(BrokerAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    from .mt5_adapter import MT5Adapter
    adapter = MT5Adapter(login=account.login, password=account.password, server=account.server)
    success = await adapter.connect()
    if success:
        acc_info = await adapter.get_account_info()
        await adapter.disconnect()
        return {"status": "success", "info": acc_info}
    else:
        return {"status": "failed", "error": "Could not connect to MT5"}

@router.get("/symbols", response_model=List[Symbol])
async def get_all_symbols(session: Session = Depends(get_session)):
    # Sync with active accounts
    accounts = session.exec(select(BrokerAccount).where(BrokerAccount.is_active == True)).all()
    for acc in accounts:
        # Update manager with credentials
        adapter = broker_manager.get_adapter(acc.broker_name)
        if adapter and hasattr(adapter, 'login'):
            adapter.login = acc.login
            adapter.password = acc.password
            adapter.server = acc.server

    symbols = await broker_manager.get_all_symbols()

    for s in symbols:
        adapter = broker_manager.get_adapter(s.broker)
        tick = await adapter.get_latest_tick(s.name) if adapter else {}
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
