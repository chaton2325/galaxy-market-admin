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
        data = response.json()
        if isinstance(data, list):
            users = data
        elif isinstance(data, dict):
            users = data.get('data') or data.get('users') or []
            
        # Normalization
        for u in users:
            if isinstance(u, dict) and 'id' not in u and '_id' in u:
                u['id'] = u['_id']
            
    return render_template('admin/users_list.html', users=users)

@users_bp.route('/<user_id>')
def user_details(user_id):
    response = APIClient.get(f'/users/{user_id}')
    user = None
    if response and response.status_code == 200:
        user = response.json()
        if user and isinstance(user, dict):
            if 'id' not in user and '_id' in user:
                user['id'] = user['_id']
                
    return render_template('admin/user_details.html', user=user)

@users_bp.route('/<user_id>', methods=['POST'])
def update_user(user_id):
    data = {
        'firstName': request.form.get('firstName'),
        'lastName': request.form.get('lastName'),
        'city': request.form.get('city')
    }
    response = APIClient.patch(f'/users/{user_id}', json=data)
    if response and response.status_code == 200:
        flash('Utilisateur mis à jour.', 'success')
    else:
        flash('Erreur lors de la mise à jour.', 'danger')
    return redirect(url_for('users.user_details', user_id=user_id))

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

@users_bp.route('/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    response = APIClient.delete(f'/users/{user_id}')
    if response and response.status_code == 200:
        flash('Utilisateur supprimé.', 'success')
        return redirect(url_for('users.list_users'))
    else:
        flash('Erreur lors de la suppression.', 'danger')
        return redirect(url_for('users.user_details', user_id=user_id))
