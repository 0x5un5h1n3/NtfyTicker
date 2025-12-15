import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import create_engine, func, select
from typing import List, Optional
import models
from config import settings

Base = declarative_base()
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)

class AssetAlertDB(Base):
    __tablename__ = "asset_alerts"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    symbol = sa.Column(sa.String, nullable=False, index=True)
    asset_type = sa.Column(sa.String(10), nullable=False)
    direction = sa.Column(sa.String(10), nullable=False)
    target_price = sa.Column(sa.Float, nullable=False)
    ntfy_topic = sa.Column(sa.String, nullable=False)
    active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now())

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_asset_alert(db: Session, data: models.CreateAssetAlert) -> models.AssetAlert:
    db_alert = AssetAlertDB(**data.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return models.AssetAlert(
        id=db_alert.id, symbol=db_alert.symbol, asset_type=db_alert.asset_type,
        direction=db_alert.direction, target_price=db_alert.target_price,
        ntfy_topic=db_alert.ntfy_topic, active=True
    )

def list_asset_alerts(db: Session) -> List[models.AssetAlert]:
    return [models.AssetAlert(
        id=a.id, symbol=a.symbol, asset_type=a.asset_type,
        direction=a.direction, target_price=a.target_price,
        ntfy_topic=a.ntfy_topic, active=a.active
    ) for a in db.execute(select(AssetAlertDB).where(AssetAlertDB.active == True)).scalars()]

def delete_asset_alert(db: Session, alert_id: int) -> bool:
    result = db.execute(sa.delete(AssetAlertDB).where(AssetAlertDB.id == alert_id))
    db.commit()
    return result.rowcount > 0

def deactivate_asset_alert(db: Session, alert_id: int) -> bool:
    result = db.execute(sa.update(AssetAlertDB)
                       .where(AssetAlertDB.id == alert_id)
                       .values(active=False))
    db.commit()
    return result.rowcount > 0
