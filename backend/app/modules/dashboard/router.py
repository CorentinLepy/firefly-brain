from datetime import date
from decimal import Decimal, InvalidOperation
from fastapi import APIRouter, Query
from app.modules.firefly.client import FireflyClient

router = APIRouter()


def parse_amount(value: str | int | float | None) -> Decimal:
    if value is None:
        return Decimal("0")
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return Decimal("0")


def money_float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01")))


def month_bounds() -> tuple[str, str]:
    today = date.today()
    start = today.replace(day=1)
    return start.isoformat(), today.isoformat()


def extract_split_transactions(groups: list[dict]) -> list[dict]:
    transactions: list[dict] = []

    for group in groups:
        attributes = group.get("attributes", {})
        for tx in attributes.get("transactions", []):
            transactions.append(tx)

    return transactions


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
    transaction_groups = await client.all_transactions(start=start, end=end, max_pages=40)
    transactions = extract_split_transactions(transaction_groups)

    income = Decimal("0")
    expenses = Decimal("0")
    transfers = Decimal("0")
    uncategorized = 0

    by_category: dict[str, Decimal] = {}
    by_merchant: dict[str, Decimal] = {}

    for tx in transactions:
        amount = abs(parse_amount(tx.get("amount")))
        tx_type = tx.get("type")
        category = tx.get("category_name") or "Sans catégorie"
        merchant = tx.get("destination_name") or tx.get("source_name") or "Inconnu"

        if not tx.get("category_name") and tx_type != "transfer":
            uncategorized += 1

        if tx_type == "deposit":
            income += amount
        elif tx_type == "withdrawal":
            expenses += amount
            by_category[category] = by_category.get(category, Decimal("0")) + amount
            by_merchant[merchant] = by_merchant.get(merchant, Decimal("0")) + amount
        elif tx_type == "transfer":
            transfers += amount

    gross_assets = Decimal("0")
    total_liabilities = Decimal("0")
    available_cash = Decimal("0")

    account_items = []

    for account in accounts:
        attributes = account.get("attributes", {})
        account_type = attributes.get("type")
        name = attributes.get("name")
        balance = parse_amount(attributes.get("current_balance"))
        include_net_worth = bool(attributes.get("include_net_worth"))

        account_items.append(
            {
                "id": account.get("id"),
                "name": name,
                "type": account_type,
                "balance": money_float(balance),
                "include_net_worth": include_net_worth,
            }
        )

        if account_type == "asset" and include_net_worth:
            gross_assets += balance
            available_cash += balance

        if account_type == "liabilities" and include_net_worth:
            total_liabilities += abs(balance)

    net_worth = gross_assets - total_liabilities
    savings = income - expenses
    savings_rate = (savings / income * Decimal("100")) if income > 0 else Decimal("0")
    expense_ratio = (expenses / income * Decimal("100")) if income > 0 else Decimal("0")

    top_categories = sorted(
        [
            {"category": key, "amount": money_float(value)}
            for key, value in by_category.items()
        ],
        key=lambda item: item["amount"],
        reverse=True,
    )[:10]

    top_merchants = sorted(
        [
            {"merchant": key, "amount": money_float(value)}
            for key, value in by_merchant.items()
        ],
        key=lambda item: item["amount"],
        reverse=True,
    )[:10]

    active_budgets = [
        {
            "id": budget.get("id"),
            "name": budget.get("attributes", {}).get("name"),
            "amount": budget.get("attributes", {}).get("auto_budget_amount"),
            "currency": budget.get("attributes", {}).get("currency_code"),
            "active": budget.get("attributes", {}).get("active"),
        }
        for budget in budgets
    ]

    return {
        "period": {
            "start": start,
            "end": end,
        },
        "income": money_float(income),
        "expenses": money_float(expenses),
        "savings": money_float(savings),
        "savings_rate": round(float(savings_rate), 2),
        "expense_ratio": round(float(expense_ratio), 2),
        "transfers": money_float(transfers),
        "gross_assets": money_float(gross_assets),
        "total_liabilities": money_float(total_liabilities),
        "net_worth": money_float(net_worth),
        "available_cash": money_float(available_cash),
        "uncategorized_transactions": uncategorized,
        "transactions_count": len(transactions),
        "accounts_count": len(accounts),
        "budgets_count": len(budgets),
        "top_categories": top_categories,
        "top_merchants": top_merchants,
        "accounts": account_items,
        "budgets": active_budgets,
    }
