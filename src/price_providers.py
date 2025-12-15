import httpx
from typing import Optional
from config import settings

async def get_asset_price(symbol: str, asset_type: str) -> Optional[float]:
    symbol = symbol.upper()
    
    # Generic asset ID mapping (extend as needed)
    mapping = {
        "ASSET1": "asset1", "ASSET2": "asset2", 
        "ASSET3": "asset3", "ASSET4": "asset4"
    }
    
    asset_id = mapping.get(symbol)
    if not asset_id:
        return None
    
    url = f"{settings.asset_price_url}?ids={asset_id}&vs_currencies=usd"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return float(data[asset_id]["usd"])
    except Exception:
        return None
