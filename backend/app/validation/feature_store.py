from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from ..models.validation import FeatureSnapshot
import json

class FeatureStore:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def save_snapshot(self, broker: str, symbol: str, timeframe: str, bar_open_utc: datetime, features: Dict[str, Any]):
        unique_key = f"{broker}:{symbol}:{timeframe}:{bar_open_utc.isoformat()}"

        existing = self.db.exec(select(FeatureSnapshot).where(FeatureSnapshot.unique_key == unique_key)).first()
        if existing:
            existing.features = json.dumps(features)
        else:
            snapshot = FeatureSnapshot(
                broker=broker,
                symbol=symbol,
                timeframe=timeframe,
                bar_open_utc=bar_open_utc,
                features=json.dumps(features),
                unique_key=unique_key
            )
            self.db.add(snapshot)

        self.db.commit()

    async def get_snapshot(self, broker: str, symbol: str, timeframe: str, bar_open_utc: datetime) -> Optional[Dict[str, Any]]:
        unique_key = f"{broker}:{symbol}:{timeframe}:{bar_open_utc.isoformat()}"
        snapshot = self.db.exec(select(FeatureSnapshot).where(FeatureSnapshot.unique_key == unique_key)).first()
        return json.loads(snapshot.features) if snapshot else None
