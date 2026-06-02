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
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def about(self) -> dict[str, Any]:
        return await self.get("about")

    async def accounts(self, page: int = 1, limit: int = 50) -> dict[str, Any]:
        return await self.get("accounts", params={"page": page, "limit": limit})

    async def budgets(self, page: int = 1, limit: int = 50) -> dict[str, Any]:
        return await self.get("budgets", params={"page": page, "limit": limit})

    async def transactions(
        self,
        start: str | None = None,
        end: str | None = None,
        page: int = 1,
        limit: int = 50,
        tx_type: str = "default",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "page": page,
            "limit": limit,
            "type": tx_type,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self.get("transactions", params=params)

    async def all_pages(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        limit: int = 50,
        max_pages: int = 50,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1

        while page <= max_pages:
            query = dict(params or {})
            query["page"] = page
            query["limit"] = limit

            payload = await self.get(path, params=query)
            items.extend(payload.get("data", []))

            pagination = payload.get("meta", {}).get("pagination", {})
            total_pages = int(pagination.get("total_pages") or page)

            if page >= total_pages:
                break

            page += 1

        return items

    async def all_accounts(self) -> list[dict[str, Any]]:
        return await self.all_pages("accounts", limit=50, max_pages=20)

    async def all_budgets(self) -> list[dict[str, Any]]:
        return await self.all_pages("budgets", limit=50, max_pages=20)

    async def all_transactions(
        self,
        start: str | None = None,
        end: str | None = None,
        max_pages: int = 40,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"type": "default"}
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        return await self.all_pages(
            "transactions",
            params=params,
            limit=50,
            max_pages=max_pages,
        )
