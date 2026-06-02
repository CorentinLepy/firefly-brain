from fastapi import APIRouter, Query
from app.modules.firefly.client import FireflyClient

router = APIRouter()


def flatten_transactions(groups: list[dict]) -> list[dict]:
    items: list[dict] = []

    for group in groups:
        for tx in group.get("attributes", {}).get("transactions", []):
            items.append(
                {
                    "id": tx.get("transaction_journal_id"),
                    "type": tx.get("type"),
                    "date": tx.get("date"),
                    "description": tx.get("description"),
                    "amount": tx.get("amount"),
                    "currency": tx.get("currency_code"),
                    "source": tx.get("source_name"),
                    "destination": tx.get("destination_name"),
                    "category": tx.get("category_name"),
                    "budget": tx.get("budget_name"),
                    "tags": tx.get("tags") or [],
                }
            )

    return items


@router.get("")
async def transactions_alias(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
) -> dict:
    return await FireflyClient().transactions(start=start, end=end, page=page)


@router.get("/firefly")
async def firefly_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
) -> dict:
    return await FireflyClient().transactions(start=start, end=end, page=page)


@router.get("/simple")
async def simple_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
) -> dict:
    data = await FireflyClient().transactions(start=start, end=end, page=page)
    groups = data.get("data", [])
    return {
        "count": len(groups),
        "items": flatten_transactions(groups),
        "pagination": data.get("meta", {}).get("pagination", {}),
    }


@router.get("/uncategorized")
async def uncategorized_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
) -> dict:
    groups = await FireflyClient().all_transactions(start=start, end=end, max_pages=40)

    results = []
    for group in groups:
        for tx in group.get("attributes", {}).get("transactions", []):
            tx_type = tx.get("type")

            if tx_type == "transfer":
                continue

            if not tx.get("category_name"):
                results.append(
                    {
                        "id": tx.get("transaction_journal_id"),
                        "description": tx.get("description"),
                        "amount": tx.get("amount"),
                        "date": tx.get("date"),
                        "type": tx_type,
                        "source": tx.get("source_name"),
                        "destination": tx.get("destination_name"),
                        "budget": tx.get("budget_name"),
                    }
                )

    return {"count": len(results), "items": results[:100]}
