from flask import Blueprint, render_template, session, redirect, url_for, request
from api_client import APIClient

moderation_bp = Blueprint('moderation', __name__)

@moderation_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@moderation_bp.route('/')
def index():
    item_type = request.args.get('type')
    status = request.args.get('status') or 'pending'
    limit = request.args.get('limit', 20)
    cursor = request.args.get('cursor')
    params = {'status': status, 'limit': limit}
    if item_type: params['type'] = item_type
    if cursor: params['cursor'] = cursor
    
    response = APIClient.get('/moderation', params=params)
    data = {}
    items = []
    next_cursor = None
    next_cursor_products = None
    next_cursor_services = None
    if response and response.status_code == 200:
        data = response.json()
        
        # Normalization for all lists in data
        if isinstance(data, dict):
            if item_type:
                items = data.get('data', [])
                next_cursor = data.get('nextCursor')
            else:
                next_cursor = data.get('nextCursor')
                if isinstance(next_cursor, dict):
                    next_cursor_products = next_cursor.get('products')
                    next_cursor_services = next_cursor.get('services')
            for key in data:
                if isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict) and 'id' not in item and '_id' in item:
                            item['id'] = item['_id']
            for item in items:
                if isinstance(item, dict) and 'id' not in item and '_id' in item:
                    item['id'] = item['_id']
        elif isinstance(data, list):
            items = data
            for item in data:
                if isinstance(item, dict) and 'id' not in item and '_id' in item:
                    item['id'] = item['_id']
        
    return render_template('admin/moderation.html', data=data, items=items, item_type=item_type, status=status, limit=limit, cursor=cursor, next_cursor=next_cursor, next_cursor_products=next_cursor_products, next_cursor_services=next_cursor_services)
