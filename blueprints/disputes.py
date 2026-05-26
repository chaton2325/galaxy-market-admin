from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

disputes_bp = Blueprint('disputes', __name__)

@disputes_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@disputes_bp.route('/')
def index():
    status = request.args.get('status')
    limit = request.args.get('limit', 20)
    cursor = request.args.get('cursor')
    params = {'limit': limit}
    if status: params['status'] = status
    if cursor: params['cursor'] = cursor
    
    response = APIClient.get('/disputes', params=params)
    disputes = []
    next_cursor = None
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            disputes = data
        elif isinstance(data, dict):
            disputes = data.get('disputes') or data.get('data') or []
            next_cursor = data.get('nextCursor')
            
        # Normalization
        for d in disputes:
            if isinstance(d, dict) and 'id' not in d and '_id' in d:
                d['id'] = d['_id']
                
    return render_template('admin/disputes.html', disputes=disputes, current_status=status, next_cursor=next_cursor, limit=limit, cursor=cursor)

@disputes_bp.route('/create', methods=['POST'])
def create():
    target_type = request.form.get('targetType')
    target_id = request.form.get('targetId')
    reason = request.form.get('reason')
    
    response = APIClient.post('/disputes', json={
        'targetType': target_type,
        'targetId': target_id,
        'reason': reason
    })
    
    if response and response.status_code in [200, 201]:
        flash('Litige ouvert avec succès.', 'success')
    else:
        flash('Erreur lors de l\'ouverture du litige.', 'danger')
    return redirect(url_for('disputes.index'))

@disputes_bp.route('/<dispute_id>/close', methods=['POST'])
def close(dispute_id):
    note = request.form.get('resolutionNote')
    response = APIClient.patch(f'/disputes/{dispute_id}/close', json={
        'resolutionNote': note
    })
    
    if response and response.status_code == 200:
        flash('Litige clôturé.', 'success')
    else:
        flash('Erreur lors de la clôture.', 'danger')
    return redirect(url_for('disputes.index'))
