from fastapi import APIRouter, Query

from app.modules.firefly.client import FireflyClient
from app.services.finance import (
    build_financial_summary,
    detect_alerts,
    detect_subscriptions,
    flatten_transactions,
    month_bounds,
    previous_period,
)

router = APIRouter()


@router.get("/summary")
async def dashboard_summary(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
) -> dict:
    if not start or not end:
        default_start, default_end = month_bounds()
        start = start or default_start
        end = end or default_end

    client = FireflyClient()
    accounts = await client.all_accounts()
    budgets = await client.all_budgets()
    tx_groups = await client.all_transactions(start=start, end=end, max_pages=60)
    transactions = flatten_transactions(tx_groups)

    summary = build_financial_summary(accounts, transactions)
    subscriptions = detect_subscriptions(transactions)
    alerts = detect_alerts(summary, subscriptions)

    budget_items = [
        {
            "id": budget.get("id"),
            "name": budget.get("attributes", {}).get("name"),
            "amount": budget.get("attributes", {}).get("auto_budget_amount"),
            "currency": budget.get("attributes", {}).get("currency_code"),
            "active": budget.get("attributes", {}).get("active"),
        }
        for budget in budgets
    ]

    summary.update(
        {
            "period": {"start": start, "end": end},
            "budgets_count": len(budgets),
            "budgets": budget_items,
            "subscriptions_count": len(subscriptions),
            "subscriptions_yearly_cost": round(sum(item["yearly_cost"] for item in subscriptions), 2),
            "alerts_count": len(alerts),
            "alerts": alerts,
        }
    )
    return summary


@router.get("/comparison")
async def dashboard_comparison(
    start: str = Query(..., description="YYYY-MM-DD"),
    end: str = Query(..., description="YYYY-MM-DD"),
) -> dict:
    client = FireflyClient()
    accounts = await client.all_accounts()

    current_groups = await client.all_transactions(start=start, end=end, max_pages=60)
    previous_start, previous_end = previous_period(start, end)
    previous_groups = await client.all_transactions(start=previous_start, end=previous_end, max_pages=60)

    current = build_financial_summary(accounts, flatten_transactions(current_groups))
    previous = build_financial_summary(accounts, flatten_transactions(previous_groups))

    def delta(key: str) -> float:
        return round(float(current.get(key, 0)) - float(previous.get(key, 0)), 2)

    return {
        "current_period": {"start": start, "end": end},
        "previous_period": {"start": previous_start, "end": previous_end},
        "current": current,
        "previous": previous,
        "delta": {
            "income": delta("income"),
            "expenses": delta("expenses"),
            "savings": delta("savings"),
            "net_worth": delta("net_worth"),
        },
    }
