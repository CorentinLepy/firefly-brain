from fastapi import APIRouter, Query
from app.modules.firefly.client import FireflyClient
from app.services.finance import simplified_transactions

router = APIRouter()


@router.get("")
async def transactions_alias(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
    limit: int = 50,
) -> dict:
    return await FireflyClient().transactions(start=start, end=end, page=page, limit=limit)


@router.get("/firefly")
async def firefly_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
    limit: int = 50,
) -> dict:
    return await FireflyClient().transactions(start=start, end=end, page=page, limit=limit)


@router.get("/simple")
async def simple_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = 1,
    limit: int = 50,
) -> dict:
    data = await FireflyClient().transactions(start=start, end=end, page=page, limit=limit)
    groups = data.get("data", [])
    return {
        "count": len(groups),
        "items": simplified_transactions(groups),
        "pagination": data.get("meta", {}).get("pagination", {}),
    }


@router.get("/uncategorized")
async def uncategorized_transactions(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
) -> dict:
    groups = await FireflyClient().all_transactions(start=start, end=end, max_pages=60)
    results = []
    for item in simplified_transactions(groups):
        if item.get("type") != "transfer" and not item.get("category"):
            results.append(item)
    return {"count": len(results), "items": results[:200]}
