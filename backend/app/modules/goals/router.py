from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.goals.models import Goal

router = APIRouter()


class GoalIn(BaseModel):
    name: str
    target_amount: Decimal
    current_amount: Decimal = Decimal("0")
    target_date: date | None = None
    priority: str = "medium"
    status: str = "active"


def serialize(goal: Goal) -> dict:
    target = Decimal(goal.target_amount)
    current = Decimal(goal.current_amount)
    progress = float((current / target * Decimal("100")) if target > 0 else Decimal("0"))
    return {
        "id": goal.id,
        "name": goal.name,
        "target_amount": float(target),
        "current_amount": float(current),
        "remaining_amount": float(max(target - current, Decimal("0"))),
        "progress": round(progress, 2),
        "target_date": goal.target_date.isoformat() if goal.target_date else None,
        "priority": goal.priority,
        "status": goal.status,
    }


@router.get("")
def list_goals(db: Session = Depends(get_db)) -> dict:
    goals = db.query(Goal).order_by(Goal.id.desc()).all()
    return {"count": len(goals), "items": [serialize(goal) for goal in goals]}


@router.post("")
def create_goal(payload: GoalIn, db: Session = Depends(get_db)) -> dict:
    goal = Goal(**payload.model_dump(), updated_at=datetime.utcnow())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return serialize(goal)


@router.put("/{goal_id}")
def update_goal(goal_id: int, payload: GoalIn, db: Session = Depends(get_db)) -> dict:
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    for key, value in payload.model_dump().items():
        setattr(goal, key, value)
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return serialize(goal)


@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)) -> dict:
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"deleted": True}
