from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

users_bp = Blueprint('users', __name__)

@users_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@users_bp.route('/')
def list_users():
    page = request.args.get('page', 1)
    response = APIClient.get(f'/users?page={page}')
    users = []
    if response and response.status_code == 200:
        users = response.json()
    return render_template('admin/users_list.html', users=users)

@users_bp.route('/<user_id>')
def user_details(user_id):
    response = APIClient.get(f'/users/{user_id}')
    user = None
    if response and response.status_code == 200:
        user = response.json()
    return render_template('admin/user_details.html', user=user)

@users_bp.route('/<user_id>/suspend', methods=['POST'])
def suspend_user(user_id):
    reason = request.form.get('reason')
    response = APIClient.patch(f'/users/{user_id}/suspend', json={'reason': reason})
    if response and response.status_code == 200:
        flash('Utilisateur suspendu avec succès.', 'success')
    else:
        flash('Erreur lors de la suspension.', 'danger')
    return redirect(url_for('users.user_details', user_id=user_id))

@users_bp.route('/<user_id>/reactivate', methods=['POST'])
def reactivate_user(user_id):
    reason = request.form.get('reason')
    response = APIClient.patch(f'/users/{user_id}/reactivate', json={'reason': reason})
    if response and response.status_code == 200:
        flash('Utilisateur réactivé avec succès.', 'success')
    else:
        flash('Erreur lors de la réactivation.', 'danger')
    return redirect(url_for('users.user_details', user_id=user_id))
