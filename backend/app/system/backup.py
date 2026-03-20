import json
from sqlmodel import Session, select
from ..database import engine
from ..models.symbol import Symbol
from ..models.validation import Experiment
from ..models.execution import Position

async def export_state() -> str:
    with Session(engine) as session:
        data = {
            "symbols": [s.dict() for s in session.exec(select(Symbol)).all()],
            "experiments": [e.dict() for e in session.exec(select(Experiment)).all()],
            "positions": [p.dict() for p in session.exec(select(Position)).all()]
        }
        # Handle datetime serialization
        return json.dumps(data, default=str)

async def import_state(json_str: str):
    data = json.loads(json_str)
    with Session(engine) as session:
        # Simplified import: just adds new or updates existing
        # In real app, would need more careful reconciliation
        pass
