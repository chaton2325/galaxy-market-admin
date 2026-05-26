from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

services_bp = Blueprint('services', __name__)

@services_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@services_bp.route('/')
def list_services():
    limit = request.args.get('limit', 20)
    cursor = request.args.get('cursor')
    params = {'limit': limit}
    if cursor: params['cursor'] = cursor
    
    response = APIClient.get('/services', params=params)
    services = []
    next_cursor = None
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            services = data
        elif isinstance(data, dict):
            services = data.get('services') or data.get('data') or data.get('items') or []
            next_cursor = data.get('nextCursor')
            
        for s in services:
            if isinstance(s, dict) and 'id' not in s and '_id' in s:
                s['id'] = s['_id']
            
    return render_template('admin/services_list.html', services=services, next_cursor=next_cursor, limit=limit, cursor=cursor)

@services_bp.route('/owner/<user_id>')
def owner_services(user_id):
    response = APIClient.get(f'/services/owner/{user_id}')
    services = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            services = data
        elif isinstance(data, dict):
            services = data.get('services') or data.get('data') or data.get('items') or []

        for s in services:
            if isinstance(s, dict) and 'id' not in s and '_id' in s:
                s['id'] = s['_id']

    return render_template('admin/services_list.html', services=services, next_cursor=None, limit=20, cursor=None, owner_id=user_id)

@services_bp.route('/<service_id>')
def service_details(service_id):
    response = APIClient.get(f'/services/{service_id}')
    service = None
    if response and response.status_code == 200:
        service = response.json()
        if service and isinstance(service, dict):
            if 'id' not in service and '_id' in service:
                service['id'] = service['_id']
                
    return render_template('admin/service_details.html', service=service)

@services_bp.route('/<service_id>/moderate', methods=['POST'])
def moderate_service(service_id):
    status = request.form.get('status')
    reason = request.form.get('reason')
    data = {'moderationStatus': status}
    if reason:
        data['reason'] = reason
    
    response = APIClient.patch(f'/services/{service_id}/moderate', json=data)
    if response and response.status_code == 200:
        flash('Service modéré avec succès.', 'success')
    else:
        flash('Erreur lors de la modération.', 'danger')
    return redirect(url_for('services.service_details', service_id=service_id))

@services_bp.route('/<service_id>/update', methods=['POST'])
def update_service(service_id):
    data = {key: value for key, value in request.form.items() if value != ''}
    response = APIClient.patch(f'/services/{service_id}', json=data)
    if response and response.status_code == 200:
        flash('Service mis a jour.', 'success')
    else:
        flash('Erreur lors de la mise a jour.', 'danger')
    return redirect(url_for('services.service_details', service_id=service_id))

@services_bp.route('/<service_id>/archive', methods=['POST'])
def archive_service(service_id):
    response = APIClient.patch(f'/services/{service_id}/archive')
    if response and response.status_code == 200:
        flash('Service archivé.', 'success')
    else:
        flash('Erreur lors de l\'archivage.', 'danger')
    return redirect(url_for('services.service_details', service_id=service_id))

@services_bp.route('/<service_id>/delete', methods=['POST'])
def delete_service(service_id):
    response = APIClient.delete(f'/services/{service_id}')
    if response and response.status_code == 200:
        flash('Service supprimé.', 'success')
        return redirect(url_for('services.list_services'))
    else:
        flash('Erreur lors de la suppression.', 'danger')
        return redirect(url_for('services.service_details', service_id=service_id))
