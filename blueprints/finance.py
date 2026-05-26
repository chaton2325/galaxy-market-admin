from urllib.parse import urlencode
from flask import Blueprint, Response, flash, redirect, render_template, request, session, url_for
from api_client import APIClient

finance_bp = Blueprint('finance', __name__)

ENTRY_TYPES = [
    'FUNDS_BLOCKED',
    'COMMISSION_RECOGNIZED',
    'SELLER_PAYOUT',
    'REFUND',
    'DISPUTE_HOLD',
    'DISPUTE_RELEASE',
]

RESOURCE_TYPES = ['ORDER', 'INVOICE', 'DISPUTE', 'PAYOUT']


@finance_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))


def finance_filters(include_limit=True, default_limit=50):
    params = {}
    if include_limit:
        params['limit'] = request.args.get('limit', default_limit)

    for key in ['cursor', 'entryType', 'resourceType', 'sellerId', 'customerId', 'from', 'to']:
        value = request.args.get(key)
        if value:
            params[key] = value

    return params


def response_json(response, default):
    if response and response.status_code == 200:
        return response.json()
    return default


def query_string(params):
    clean_params = {key: value for key, value in params.items() if value not in [None, '']}
    return urlencode(clean_params)


@finance_bp.route('/')
def index():
    stats_response = APIClient.finance_get('/admin/stats')
    ledger_params = finance_filters()
    ledger_response = APIClient.finance_get('/admin/ledger', params=ledger_params)

    stats = response_json(stats_response, {})
    ledger = response_json(ledger_response, {})
    entries = ledger.get('data', []) if isinstance(ledger, dict) else []
    summary = ledger.get('summary', {}) if isinstance(ledger, dict) else {}
    next_cursor = ledger.get('nextCursor') if isinstance(ledger, dict) else None

    if stats_response and stats_response.status_code not in [200, 401]:
        flash('Erreur lors du chargement des statistiques finance.', 'danger')
    if ledger_response and ledger_response.status_code not in [200, 401]:
        flash('Erreur lors du chargement du grand livre.', 'danger')

    return render_template(
        'admin/finance.html',
        stats=stats,
        entries=entries,
        summary=summary,
        next_cursor=next_cursor,
        filters=ledger_params,
        entry_types=ENTRY_TYPES,
        resource_types=RESOURCE_TYPES,
        balance=None,
        balance_seller_id=request.args.get('balanceSellerId'),
        export_query=query_string({key: value for key, value in ledger_params.items() if key != 'limit' and key != 'cursor'}),
        next_page_query=query_string({**ledger_params, 'cursor': next_cursor}) if next_cursor else '',
    )


@finance_bp.route('/balance')
def balance_lookup():
    seller_id = request.args.get('sellerId')
    if not seller_id:
        flash('Renseigne un sellerId pour consulter un solde vendeur.', 'warning')
        return redirect(url_for('finance.index'))
    return redirect(url_for('finance.balance', seller_id=seller_id))


@finance_bp.route('/balance/<seller_id>')
def balance(seller_id):
    stats_response = APIClient.finance_get('/admin/stats')
    balance_response = APIClient.finance_get(f'/admin/balance/{seller_id}')

    stats = response_json(stats_response, {})
    balance_data = response_json(balance_response, {})
    if balance_response and balance_response.status_code != 200:
        flash('Erreur lors du chargement du solde vendeur.', 'danger')

    return render_template(
        'admin/finance.html',
        stats=stats,
        entries=[],
        summary={},
        next_cursor=None,
        filters={},
        entry_types=ENTRY_TYPES,
        resource_types=RESOURCE_TYPES,
        balance=balance_data,
        balance_seller_id=seller_id,
        export_query='',
        next_page_query='',
    )


@finance_bp.route('/export')
def export():
    params = finance_filters(include_limit=False)
    response = APIClient.finance_get('/admin/export', params=params)
    if not response or response.status_code != 200:
        flash('Erreur lors de l export CSV du grand livre.', 'danger')
        return redirect(url_for('finance.index', **params))

    content_type = response.headers.get('Content-Type', 'text/csv; charset=utf-8')
    disposition = response.headers.get('Content-Disposition', 'attachment; filename="ledger.csv"')

    return Response(
        response.content,
        status=response.status_code,
        content_type=content_type,
        headers={'Content-Disposition': disposition},
    )
