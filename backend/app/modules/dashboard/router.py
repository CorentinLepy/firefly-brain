from decimal import Decimal
from fastapi import APIRouter
from app.modules.firefly.client import FireflyClient

router = APIRouter()

def parse_amount(value: str | int | float | None) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))

@router.get("/summary")
async def dashboard_summary(start: str | None = None, end: str | None = None) -> dict:
    data = await FireflyClient().transactions(start=start, end=end)

    income = Decimal("0")
    expenses = Decimal("0")
    uncategorized = 0
    by_category: dict[str, Decimal] = {}

    for group in data.get("data", []):
        for tx in group.get("attributes", {}).get("transactions", []):
            amount = parse_amount(tx.get("amount"))
            tx_type = tx.get("type")
            category = tx.get("category_name") or "Sans catégorie"

            if not tx.get("category_name"):
                uncategorized += 1

            if tx_type == "deposit":
                income += abs(amount)
            elif tx_type == "withdrawal":
                expenses += abs(amount)
                by_category[category] = by_category.get(category, Decimal("0")) + abs(amount)

    savings = income - expenses
    savings_rate = float((savings / income * 100) if income > 0 else 0)

    top_categories = sorted(
        [{"category": key, "amount": float(value)} for key, value in by_category.items()],
        key=lambda item: item["amount"],
        reverse=True,
    )[:8]

    return {
        "income": float(income),
        "expenses": float(expenses),
        "savings": float(savings),
        "savings_rate": round(savings_rate, 2),
        "uncategorized_transactions": uncategorized,
        "top_categories": top_categories,
    }
