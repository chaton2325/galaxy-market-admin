from flask import Blueprint, render_template, session, redirect, url_for, request
from api_client import APIClient

audit_bp = Blueprint('audit', __name__)

@audit_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@audit_bp.route('/')
def index():
    limit = request.args.get('limit', 50)
    response = APIClient.get('/audit-logs', params={'limit': limit})
    logs = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            logs = data
        elif isinstance(data, dict):
            logs = data.get('auditLogs') or data.get('data') or data.get('logs') or []
            
    return render_template('admin/audit_logs.html', logs=logs)
