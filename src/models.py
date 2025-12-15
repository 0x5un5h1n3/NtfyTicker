from typing import Literal, Optional
from pydantic import BaseModel, Field

AssetType = Literal["asset1", "asset2"] 
Direction = Literal["above", "below"]

class CreateAssetAlert(BaseModel):
    symbol: str = Field(..., description="ex: ASSET1 or ASSET2")
    asset_type: AssetType
    direction: Direction
    target_price: float = Field(..., gt=0)
    ntfy_topic: str = Field(...)

class AssetAlert(CreateAssetAlert):
    id: int
    active: bool = True

class AssetAlertResponse(AssetAlert):
    last_price: Optional[float] = None
    triggered: bool = False
