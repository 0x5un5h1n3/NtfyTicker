import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
import storage, price_providers, ntfy_client, models
from config import settings

async def check_all_asset_alerts():
    """Background task to check all active asset alerts"""
    db = next(storage.get_db())
    alerts = storage.list_asset_alerts(db)
    
    for alert in alerts:
        price = await price_providers.get_asset_price(alert.symbol, alert.asset_type)
        if price is None:
            continue
            
        should_trigger = (
            (alert.direction == "above" and price >= alert.target_price) or
            (alert.direction == "below" and price <= alert.target_price)
        )
        
        if should_trigger:
            title = f"🚨 {alert.symbol} Asset Alert"
            msg = f"{alert.symbol}: ${price:,.2f} ({alert.direction} ${alert.target_price:,.2f})"
            tags = "📈" if alert.direction == "above" else "📉"
            
            success = await ntfy_client.send_notification(
                alert.ntfy_topic, title, msg + f"\n{tags}", priority=4
            )
            
            if success:
                storage.deactivate_asset_alert(db, alert.id)
    
    db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_all_asset_alerts, "interval", 
                     seconds=settings.check_interval_seconds)
    scheduler.start()
    print(f"🚀 NtfyTicker started - checking every {settings.check_interval_seconds}s")
    yield
    scheduler.shutdown()

app = FastAPI(
    title="NtfyTicker", 
    description="Asset price alerts via ntfy",
    version="0.1.0", 
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {
        "message": "NtfyTicker is running", 
        "version": "1.0.0",
        "check_interval": f"{settings.check_interval_seconds}s",
        "asset_price_url": settings.asset_price_url,
        "ntfy_url": settings.ntfy_base_url
    }

@app.get("/asset-alerts", response_model=list[models.AssetAlertResponse])
async def list_asset_alerts(db: Session = Depends(storage.get_db)):
    alerts = storage.list_asset_alerts(db)
    return [
        models.AssetAlertResponse(
            id=alert.id,
            symbol=alert.symbol,
            asset_type=alert.asset_type,
            direction=alert.direction,
            target_price=alert.target_price,
            ntfy_topic=alert.ntfy_topic,
            active=alert.active,
            last_price=None,
            triggered=not alert.active
        ) for alert in alerts
    ]

@app.post("/asset-alerts", response_model=models.AssetAlertResponse)
async def create_asset_alert(
    payload: models.CreateAssetAlert, 
    db: Session = Depends(storage.get_db)
):
    alert = storage.create_asset_alert(db, payload)
    return models.AssetAlertResponse(
        id=alert.id,
        symbol=alert.symbol,
        asset_type=alert.asset_type,
        direction=alert.direction,
        target_price=alert.target_price,
        ntfy_topic=alert.ntfy_topic,
        active=alert.active,
        last_price=None,
        triggered=False
    )

@app.delete("/asset-alerts/{alert_id}")
async def delete_asset_alert(alert_id: int, db: Session = Depends(storage.get_db)):
    success = storage.delete_asset_alert(db, alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset alert not found")
    return {"status": "deleted", "alert_id": alert_id}

