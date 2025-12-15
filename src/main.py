import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
import storage, price_providers, ntfy_client
from config import settings
import models

async def check_all_asset_alerts():
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
    yield
    scheduler.shutdown()

app = FastAPI(title="NtfyTicker", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

