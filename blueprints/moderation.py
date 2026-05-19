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
    status = request.args.get('status')
    params = {}
    if item_type: params['type'] = item_type
    if status: params['status'] = status
    
    response = APIClient.get('/moderation', params=params)
    data = {}
    if response and response.status_code == 200:
        data = response.json()
        
        # Normalization for all lists in data
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict) and 'id' not in item and '_id' in item:
                            item['id'] = item['_id']
        elif isinstance(data, list):
             for item in data:
                if isinstance(item, dict) and 'id' not in item and '_id' in item:
                    item['id'] = item['_id']
        
    return render_template('admin/moderation.html', data=data, item_type=item_type, status=status)
