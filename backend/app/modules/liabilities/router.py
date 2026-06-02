from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.liabilities.models import Liability

router = APIRouter()

class LiabilityIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = "loan"
    lender: str | None = None
    initial_amount: Decimal
    remaining_amount: Decimal
    interest_rate: Decimal | None = None
    monthly_payment: Decimal
    start_date: date | None = None
    end_date: date | None = None

@router.get("")
def list_liabilities(db: Session = Depends(get_db)) -> dict:
    liabilities = db.query(Liability).order_by(Liability.name.asc()).all()
    total_remaining = sum((item.remaining_amount for item in liabilities), Decimal("0"))
    total_monthly = sum((item.monthly_payment for item in liabilities), Decimal("0"))
    return {
        "total_remaining": float(total_remaining),
        "total_monthly_payment": float(total_monthly),
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "lender": item.lender,
                "initial_amount": float(item.initial_amount),
                "remaining_amount": float(item.remaining_amount),
                "interest_rate": float(item.interest_rate) if item.interest_rate is not None else None,
                "monthly_payment": float(item.monthly_payment),
                "start_date": item.start_date.isoformat() if item.start_date else None,
                "end_date": item.end_date.isoformat() if item.end_date else None,
            }
            for item in liabilities
        ],
    }

@router.post("")
def create_liability(payload: LiabilityIn, db: Session = Depends(get_db)) -> dict:
    liability = Liability(**payload.model_dump())
    db.add(liability)
    db.commit()
    db.refresh(liability)
    return {"id": liability.id, "created": True}

@router.delete("/{liability_id}")
def delete_liability(liability_id: int, db: Session = Depends(get_db)) -> dict:
    liability = db.get(Liability, liability_id)
    if liability is None:
        raise HTTPException(status_code=404, detail="Liability not found")
    db.delete(liability)
    db.commit()
    return {"deleted": True}
