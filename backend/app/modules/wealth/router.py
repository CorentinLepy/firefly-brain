from fastapi import APIRouter
from app.modules.firefly.client import FireflyClient
from app.services.finance import money_float, parse_amount

router = APIRouter()


@router.get('/summary')
async def wealth_summary() -> dict:
    accounts = await FireflyClient().all_accounts()
    assets = []
    liabilities = []
    ignored = []

    for account in accounts:
        attrs = account.get('attributes', {})
        item = {
            'id': account.get('id'),
            'name': attrs.get('name'),
            'type': attrs.get('type'),
            'role': attrs.get('account_role'),
            'balance': money_float(parse_amount(attrs.get('current_balance'))),
            'include_net_worth': bool(attrs.get('include_net_worth')),
            'currency': attrs.get('currency_code'),
        }
        if item['include_net_worth'] and item['type'] == 'asset':
            assets.append(item)
        elif item['include_net_worth'] and item['type'] == 'liabilities':
            liabilities.append(item)
        else:
            ignored.append(item)

    gross_assets = round(sum(item['balance'] for item in assets), 2)
    total_liabilities = round(sum(abs(item['balance']) for item in liabilities), 2)
    net_worth = round(gross_assets - total_liabilities, 2)

    return {
        'gross_assets': gross_assets,
        'total_liabilities': total_liabilities,
        'net_worth': net_worth,
        'assets_count': len(assets),
        'liabilities_count': len(liabilities),
        'ignored_count': len(ignored),
        'assets': sorted(assets, key=lambda item: item['balance'], reverse=True),
        'liabilities': sorted(liabilities, key=lambda item: abs(item['balance']), reverse=True),
    }
