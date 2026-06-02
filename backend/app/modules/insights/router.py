from fastapi import APIRouter, Query
from app.modules.firefly.client import FireflyClient
from app.services.finance import build_financial_summary, detect_subscriptions, flatten_transactions, month_bounds, optimization_opportunities

router = APIRouter()


@router.get("/overview")
async def overview(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
) -> dict:
    if not start or not end:
        default_start, default_end = month_bounds()
        start = start or default_start
        end = end or default_end

    client = FireflyClient()
    accounts = await client.all_accounts()
    groups = await client.all_transactions(start=start, end=end, max_pages=60)
    transactions = flatten_transactions(groups)
    summary = build_financial_summary(accounts, transactions)
    subscriptions = detect_subscriptions(transactions)

    opportunities = optimization_opportunities(summary, subscriptions)

    return {
        "period": {"start": start, "end": end},
        "summary": summary,
        "subscriptions": subscriptions,
        "optimization_opportunities": opportunities[:10],
    }
