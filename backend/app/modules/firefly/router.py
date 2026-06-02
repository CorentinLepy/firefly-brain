from fastapi import APIRouter, HTTPException
import httpx
from app.modules.firefly.client import FireflyClient

router = APIRouter()

@router.get("/status")
async def status() -> dict:
    client = FireflyClient()
    try:
        about = await client.about()
        return {"connected": True, "about": about}
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Firefly III unreachable: {exc}") from exc

@router.get("/accounts")
async def accounts() -> dict:
    return await FireflyClient().accounts()

@router.get("/budgets")
async def budgets() -> dict:
    return await FireflyClient().budgets()
