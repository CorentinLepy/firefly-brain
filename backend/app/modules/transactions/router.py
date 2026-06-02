from fastapi import APIRouter, Query
from app.modules.firefly.client import FireflyClient

router = APIRouter()

@router.get("/firefly")
async def firefly_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
) -> dict:
    return await FireflyClient().transactions(start=start, end=end, page=page)

@router.get("/uncategorized")
async def uncategorized_transactions(start: str | None = None, end: str | None = None) -> dict:
    data = await FireflyClient().transactions(start=start, end=end)
    results = []
    for group in data.get("data", []):
        for tx in group.get("attributes", {}).get("transactions", []):
            if not tx.get("category_name"):
                results.append({
                    "id": tx.get("transaction_journal_id"),
                    "description": tx.get("description"),
                    "amount": tx.get("amount"),
                    "date": tx.get("date"),
                    "source": tx.get("source_name"),
                    "destination": tx.get("destination_name"),
                })
    return {"count": len(results), "items": results}
