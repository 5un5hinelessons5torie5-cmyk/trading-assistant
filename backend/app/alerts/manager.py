from typing import List, Optional
from sqlmodel import Session, select
from ..models.alert import Alert

class AlertManager:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def create_alert(self, category: str, level: str, title: str, message: str, dedupe_key: Optional[str] = None):
        if dedupe_key:
            existing = self.db.exec(
                select(Alert).where(Alert.dedupe_key == dedupe_key, Alert.is_read == False)
            ).first()
            if existing:
                existing.message = message
                self.db.add(existing)
                self.db.commit()
                return existing

        alert = Alert(
            category=category,
            level=level,
            title=title,
            message=message,
            dedupe_key=dedupe_key
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        # Real version: Telegram delivery here if needed
        return alert

    async def get_unread_alerts(self) -> List[Alert]:
        return self.db.exec(select(Alert).where(Alert.is_read == False)).all()
