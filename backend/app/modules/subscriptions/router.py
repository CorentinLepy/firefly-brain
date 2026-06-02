from fastapi import APIRouter, Query
from app.modules.firefly.client import FireflyClient
from app.services.finance import detect_subscriptions, flatten_transactions

router = APIRouter()


@router.get("/detect")
async def detect(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
) -> dict:
    groups = await FireflyClient().all_transactions(start=start, end=end, max_pages=80)
    subscriptions = detect_subscriptions(flatten_transactions(groups))
    total_monthly = sum(item["amount"] for item in subscriptions if item["frequency"] == "monthly")
    total_yearly = sum(item["yearly_cost"] for item in subscriptions)
    return {
        "count": len(subscriptions),
        "monthly_cost_detected": round(total_monthly, 2),
        "yearly_cost_detected": round(total_yearly, 2),
        "items": subscriptions,
    }
