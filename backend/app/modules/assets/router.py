from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.assets.models import Asset

router = APIRouter()

class AssetIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(default="other")
    current_value: Decimal
    currency_code: str = "EUR"
    risk_level: str | None = None
    liquidity_level: str | None = None

class AssetOut(AssetIn):
    id: int

@router.get("")
def list_assets(db: Session = Depends(get_db)) -> dict:
    assets = db.query(Asset).order_by(Asset.name.asc()).all()
    total = sum((asset.current_value for asset in assets), Decimal("0"))
    return {
        "total": float(total),
        "items": [
            {
                "id": asset.id,
                "name": asset.name,
                "type": asset.type,
                "current_value": float(asset.current_value),
                "currency_code": asset.currency_code,
                "risk_level": asset.risk_level,
                "liquidity_level": asset.liquidity_level,
            }
            for asset in assets
        ],
    }

@router.post("", response_model=AssetOut)
def create_asset(payload: AssetIn, db: Session = Depends(get_db)) -> Asset:
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> dict:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"deleted": True}
