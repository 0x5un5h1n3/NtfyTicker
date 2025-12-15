from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from config import settings

app = FastAPI(title="NtfyTicker", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "NtfyTicker running", "asset_price_url": settings.asset_price_url}

@app.post("/asset-alerts", response_model=models.AssetAlertResponse)
async def create_asset_alert(payload: models.CreateAssetAlert):
    return models.AssetAlertResponse(id=1, **payload.dict())
