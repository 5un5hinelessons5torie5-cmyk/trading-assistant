from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from .manager import AlertManager
from ..models.alert import Alert
from typing import List

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/", response_model=List[Alert])
async def get_alerts(unread_only: bool = True, session: Session = Depends(get_session)):
    query = select(Alert)
    if unread_only:
        query = query.where(Alert.is_read == False)
    return session.exec(query).all()

@router.post("/mark-read/{alert_id}")
async def mark_read(alert_id: int, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    session.add(alert)
    session.commit()
    return {"status": "read"}
