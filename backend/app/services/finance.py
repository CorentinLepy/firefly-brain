from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from statistics import mean
from typing import Any

NO_NAME_VALUES = {"", "(no name)", "no name", "inconnu", "unknown", "none", "null"}
SUBSCRIPTION_EXCLUDED_KEYWORDS = [
    "pret", "prêt", "credit", "crédit", "dette", "mortgage", "loan", "immo", "ptz",
    "familial", "virement", "transfert", "remboursement", "remise", "cotisation bancaire",
    "achat-exceptionnel", "freedom bike", "moto", "vehicule", "véhicule", "investissement",
]
EXPENSE_EXCLUDED_FROM_OPTIMIZATION = {"crédit", "credit", "moto / véhicule", "moto / vehicule", "investissements"}


def parse_amount(value: str | int | float | None) -> Decimal:
    if value is None:
        return Decimal("0")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def money_float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01")))


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


def month_bounds(target: date | None = None) -> tuple[str, str]:
    current = target or date.today()
    start = current.replace(day=1)
    return start.isoformat(), current.isoformat()


def previous_period(start: str, end: str) -> tuple[str, str]:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    days = (end_date - start_date).days + 1
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=days - 1)
    return previous_start.isoformat(), previous_end.isoformat()


def flatten_transactions(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in groups:
        for tx in group.get("attributes", {}).get("transactions", []):
            items.append(tx)
    return items


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(str(value).replace("\n", " ").split()).strip()


def normalize_key(value: str | None) -> str:
    text = clean_text(value).lower()
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ù", "u").replace("ç", "c")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def is_empty_label(value: str | None) -> bool:
    return normalize_key(value) in NO_NAME_VALUES


def best_merchant(tx: dict[str, Any]) -> str:
    """Return a useful merchant label, avoiding Firefly's generic '(no name)' expense account."""
    destination = clean_text(tx.get("destination_name"))
    source = clean_text(tx.get("source_name"))
    description = clean_text(tx.get("description"))
    notes = clean_text(tx.get("notes"))

    if tx.get("type") == "deposit":
        if source and not is_empty_label(source):
            return source
        return description or destination or "Inconnu"

    if destination and not is_empty_label(destination):
        return destination
    if description and not is_empty_label(description):
        return description
    if notes and not is_empty_label(notes):
        return notes[:80]
    if source and not is_empty_label(source):
        return source
    return "Inconnu"


def simplified_transactions(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for tx in flatten_transactions(groups):
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
                "merchant": best_merchant(tx),
                "category": tx.get("category_name"),
                "budget": tx.get("budget_name"),
                "tags": tx.get("tags") or [],
                "notes": tx.get("notes"),
            }
        )
    return items


def build_financial_summary(accounts: list[dict[str, Any]], transactions: list[dict[str, Any]]) -> dict[str, Any]:
    income = Decimal("0")
    expenses = Decimal("0")
    transfers = Decimal("0")
    uncategorized = 0

    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    by_merchant: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    by_day: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for tx in transactions:
        amount = abs(parse_amount(tx.get("amount")))
        tx_type = tx.get("type")
        category = tx.get("category_name") or "Sans catégorie"
        merchant = best_merchant(tx)
        tx_date = (tx.get("date") or "")[:10]

        if tx_type != "transfer" and not tx.get("category_name"):
            uncategorized += 1

        if tx_type == "deposit":
            income += amount
        elif tx_type == "withdrawal":
            expenses += amount
            by_category[category] += amount
            by_merchant[merchant] += amount
            if tx_date:
                by_day[tx_date] += amount
        elif tx_type == "transfer":
            transfers += amount

    gross_assets = Decimal("0")
    total_liabilities = Decimal("0")
    available_cash = Decimal("0")
    account_items: list[dict[str, Any]] = []

    for account in accounts:
        attrs = account.get("attributes", {})
        account_type = attrs.get("type")
        balance = parse_amount(attrs.get("current_balance"))
        include_net_worth = bool(attrs.get("include_net_worth"))

        account_items.append(
            {
                "id": account.get("id"),
                "name": attrs.get("name"),
                "type": account_type,
                "balance": money_float(balance),
                "include_net_worth": include_net_worth,
                "role": attrs.get("account_role"),
            }
        )

        if account_type == "asset" and include_net_worth:
            gross_assets += balance
            available_cash += balance
        elif account_type == "liabilities" and include_net_worth:
            total_liabilities += abs(balance)

    net_worth = gross_assets - total_liabilities
    savings = income - expenses
    savings_rate = (savings / income * Decimal("100")) if income > 0 else Decimal("0")
    expense_ratio = (expenses / income * Decimal("100")) if income > 0 else Decimal("0")

    top_categories = sorted(
        [{"category": k, "amount": money_float(v)} for k, v in by_category.items()],
        key=lambda item: item["amount"],
        reverse=True,
    )[:10]
    top_merchants = sorted(
        [{"merchant": k, "amount": money_float(v)} for k, v in by_merchant.items()],
        key=lambda item: item["amount"],
        reverse=True,
    )[:10]
    daily_expenses = sorted(
        [{"date": k, "amount": money_float(v)} for k, v in by_day.items()],
        key=lambda item: item["date"],
    )

    return {
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
        "top_categories": top_categories,
        "top_merchants": top_merchants,
        "daily_expenses": daily_expenses,
        "accounts": account_items,
    }


def is_subscription_candidate(tx: dict[str, Any], amount: float, merchant: str) -> tuple[bool, str | None]:
    category = normalize_key(tx.get("category_name"))
    budget = normalize_key(tx.get("budget_name"))
    source = normalize_key(tx.get("source_name"))
    destination = normalize_key(tx.get("destination_name"))
    description = normalize_key(tx.get("description"))
    notes = normalize_key(tx.get("notes"))
    tags = " ".join(normalize_key(tag) for tag in (tx.get("tags") or []))
    source_type = normalize_key(tx.get("source_type"))
    destination_type = normalize_key(tx.get("destination_type"))
    haystack = " ".join([category, budget, source, destination, description, notes, tags, source_type, destination_type, normalize_key(merchant)])

    if tx.get("type") != "withdrawal":
        return False, "not_withdrawal"
    if amount <= 0:
        return False, "invalid_amount"
    if amount >= 500:
        return False, "amount_too_high"
    if "debt" in source_type or "debt" in destination_type:
        return False, "debt_account"
    if any(keyword in haystack for keyword in SUBSCRIPTION_EXCLUDED_KEYWORDS):
        return False, "excluded_keyword"
    if category in {"credit", "crédit", "investissements", "moto vehicule", "moto véhicule"}:
        return False, "excluded_category"
    return True, None


def detect_subscriptions(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    ignored = 0
    for tx in transactions:
        amount = money_float(abs(parse_amount(tx.get("amount"))))
        merchant = best_merchant(tx)
        allowed, _reason = is_subscription_candidate(tx, amount, merchant)
        if not allowed:
            ignored += 1
            continue
        tx_date = parse_date(tx.get("date"))
        if not tx_date:
            continue
        key = f"{normalize_key(merchant)}:{round(amount, 2)}"
        groups[key].append(
            {
                "merchant": merchant,
                "amount": amount,
                "date": tx_date,
                "description": tx.get("description"),
                "category": tx.get("category_name"),
                "budget": tx.get("budget_name"),
            }
        )

    results: list[dict[str, Any]] = []
    for entries in groups.values():
        if len(entries) < 2:
            continue
        dates = sorted(item["date"] for item in entries)
        gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        if not gaps:
            continue
        avg_gap = mean(gaps)
        if 25 <= avg_gap <= 35:
            frequency = "monthly"
            yearly_multiplier = 12
        elif 6 <= avg_gap <= 8:
            frequency = "weekly"
            yearly_multiplier = 52
        elif 360 <= avg_gap <= 370:
            frequency = "yearly"
            yearly_multiplier = 1
        else:
            continue
        last_date = max(dates)
        amount = Decimal(str(entries[-1]["amount"]))
        confidence = min(98, 55 + len(entries) * 10)
        # Reduce confidence for generic labels even after merchant cleanup.
        if is_empty_label(entries[-1]["merchant"]):
            confidence -= 20
        next_expected = last_date + timedelta(days=round(avg_gap))
        results.append(
            {
                "merchant": entries[-1]["merchant"],
                "amount": money_float(amount),
                "frequency": frequency,
                "occurrences": len(entries),
                "last_seen": last_date.isoformat(),
                "next_expected": next_expected.isoformat(),
                "yearly_cost": money_float(amount * Decimal(yearly_multiplier)),
                "confidence": max(confidence, 0),
                "category": entries[-1].get("category"),
                "budget": entries[-1].get("budget"),
            }
        )

    return sorted(results, key=lambda item: item["yearly_cost"], reverse=True)[:30]


def detect_alerts(summary: dict[str, Any], subscriptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    if summary.get("expenses", 0) > summary.get("income", 0) and summary.get("income", 0) > 0:
        alerts.append({"type": "cashflow_negative", "severity": "high", "title": "Dépenses supérieures aux revenus", "message": "La période analysée présente un cash-flow négatif."})
    if summary.get("uncategorized_transactions", 0) > 0:
        alerts.append({"type": "uncategorized", "severity": "medium", "title": "Transactions non catégorisées", "message": f"{summary['uncategorized_transactions']} transaction(s) restent à catégoriser."})
    if summary.get("savings_rate", 0) < 10 and summary.get("income", 0) > 0:
        alerts.append({"type": "low_savings", "severity": "medium", "title": "Taux d'épargne faible", "message": "Le taux d'épargne est inférieur à 10 % sur la période."})
    if summary.get("net_worth", 0) < 0:
        alerts.append({"type": "negative_net_worth", "severity": "medium", "title": "Patrimoine net négatif", "message": "Les dettes incluses dans le patrimoine dépassent les actifs inclus."})
    expensive_subscriptions = [s for s in subscriptions if s.get("yearly_cost", 0) >= 300 and s.get("confidence", 0) >= 75]
    if expensive_subscriptions:
        alerts.append({"type": "subscriptions", "severity": "low", "title": "Abonnements coûteux détectés", "message": f"{len(expensive_subscriptions)} abonnement(s) estimés à plus de 300 €/an."})
    return alerts


def optimization_opportunities(summary: dict[str, Any], subscriptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    opportunities: list[dict[str, Any]] = []
    for category in summary.get("top_categories", [])[:8]:
        category_key = normalize_key(category.get("category"))
        if category_key in EXPENSE_EXCLUDED_FROM_OPTIMIZATION:
            continue
        amount = float(category.get("amount") or 0)
        potential = round(amount * 0.1, 2)
        if potential > 10:
            opportunities.append(
                {
                    "type": "category_reduction",
                    "title": f"Optimiser {category['category']}",
                    "message": f"Une réduction de 10 % représenterait environ {potential} € sur la période.",
                    "potential_saving": potential,
                }
            )

    for subscription in subscriptions[:6]:
        if subscription.get("confidence", 0) < 75:
            continue
        opportunities.append(
            {
                "type": "subscription_review",
                "title": f"Revoir {subscription['merchant']}",
                "message": f"Coût annuel estimé : {subscription['yearly_cost']} €.",
                "potential_saving": subscription["yearly_cost"],
            }
        )
    return opportunities[:10]
