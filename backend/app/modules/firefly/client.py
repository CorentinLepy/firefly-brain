from typing import Any
import httpx
from app.core.config import settings

class FireflyClient:
    def __init__(self, base_url: str | None = None, access_token: str | None = None) -> None:
        self.base_url = (base_url or settings.firefly_base_url).rstrip("/")
        self.access_token = access_token or settings.firefly_access_token

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def about(self) -> dict[str, Any]:
        return await self.get("about")

    async def transactions(self, start: str | None = None, end: str | None = None, page: int = 1) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self.get("transactions", params=params)

    async def accounts(self) -> dict[str, Any]:
        return await self.get("accounts")

    async def budgets(self) -> dict[str, Any]:
        return await self.get("budgets")
