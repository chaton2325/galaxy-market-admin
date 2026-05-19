from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

services_bp = Blueprint('services', __name__)

@services_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@services_bp.route('/')
def list_services():
    limit = request.args.get('limit')
    cursor = request.args.get('cursor')
    params = {}
    if limit: params['limit'] = limit
    if cursor: params['cursor'] = cursor
    
    response = APIClient.get('/services', params=params)
    services = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            services = data
        elif isinstance(data, dict):
            services = data.get('services') or data.get('data') or data.get('items') or []
            
        # Normalization for MongoDB _id
        for s in services:
            if isinstance(s, dict):
                if 'id' not in s and '_id' in s:
                    s['id'] = s['_id']
            
    return render_template('admin/services_list.html', services=services)

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
