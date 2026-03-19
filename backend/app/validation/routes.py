from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from .validator import ValidationLab
from ..models.validation import Experiment
from typing import List, Dict, Any
import json

router = APIRouter(prefix="/validation", tags=["Validation"])

@router.get("/experiments", response_model=List[Experiment])
async def get_experiments(session: Session = Depends(get_session)):
    return session.exec(select(Experiment)).all()

@router.post("/run-backtest")
async def run_backtest(strategy_id: str, symbol: str, session: Session = Depends(get_session)):
    lab = ValidationLab(session)
    from datetime import datetime, timedelta
    end = datetime.utcnow()
    start = end - timedelta(days=365)

    result = await lab.run_backtest(strategy_id, symbol, start, end)

    # Save as experiment
    exp = Experiment(
        strategy_id=strategy_id,
        preset_name=f"{strategy_id}_{symbol}_default",
        oos_winrate=result["oos"]["winrate"],
        oos_profit_factor=result["oos"]["profit_factor"],
        oos_trades_count=result["oos"]["trades_count"],
        trust_score=result["trust_score"],
        decision_state="watch",
        experiment_data=json.dumps(result)
    )
    session.add(exp)
    session.commit()
    session.refresh(exp)
    return exp

@router.post("/promote/{experiment_id}")
async def promote_experiment(experiment_id: int, session: Session = Depends(get_session)):
    lab = ValidationLab(session)
    await lab.promote_experiment(experiment_id)
    return {"status": "promoted"}
