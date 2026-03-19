from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models.system import SystemSettings
from typing import List
from .backup import export_state

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/settings", response_model=SystemSettings)
def get_settings(session: Session = Depends(get_session)):
    settings = session.exec(select(SystemSettings)).first()
    if not settings:
        settings = SystemSettings()
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings

@router.post("/settings", response_model=SystemSettings)
def update_settings(new_settings: SystemSettings, session: Session = Depends(get_session)):
    settings = session.exec(select(SystemSettings)).first()
    if not settings:
        settings = SystemSettings()

    for key, value in new_settings.dict(exclude_unset=True).items():
        if key != "id":
            setattr(settings, key, value)

    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings

@router.post("/kill-switch")
def toggle_kill_switch(session: Session = Depends(get_session)):
    settings = get_settings(session)
    settings.kill_switch = not settings.kill_switch
    session.add(settings)
    session.commit()
    return {"kill_switch": settings.kill_switch}

@router.get("/export")
async def export_workstation_state():
    return await export_state()
