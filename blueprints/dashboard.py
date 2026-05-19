from flask import Blueprint, render_template, session, redirect, url_for
from api_client import APIClient

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@dashboard_bp.route('/')
def index():
    response = APIClient.get('/dashboard')
    if response and response.status_code == 200:
        data = response.json()
        return render_template('admin/dashboard.html', 
                               metrics=data.get('metrics', {}),
                               recent_audit=data.get('recentAuditLogs', []),
                               recent_disputes=data.get('recentDisputes', []),
                               recent_moderation=data.get('recentModerationItems', []))
    else:
        # Handle error or empty state
        return render_template('admin/dashboard.html', metrics={}, recent_audit=[], recent_disputes=[], recent_moderation=[])
