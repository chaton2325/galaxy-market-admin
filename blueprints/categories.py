from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

categories_bp = Blueprint('categories', __name__)

@categories_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@categories_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        scope = request.form.get('scope')
        file = request.files.get('file')
        
        if file and file.filename:
            files = {'file': (file.filename, file.stream, file.content_type)}
            data = {'name': name, 'scope': scope}
            response = APIClient.post('/categories', data=data, files=files)
        else:
            response = APIClient.post('/categories', json={'name': name, 'scope': scope})
            
        if response and response.status_code in [200, 201]:
            flash('Catégorie créée.', 'success')
        else:
            flash('Erreur lors de la création.', 'danger')
        return redirect(url_for('categories.index'))

    params = {}
    scope = request.args.get('scope')
    q = request.args.get('q')
    if scope: params['scope'] = scope
    if q: params['q'] = q

    response = APIClient.get('/categories', params=params)
    categories = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            categories = data
        elif isinstance(data, dict):
            categories = data.get('categories') or data.get('data') or []
    
    return render_template('admin/categories.html', categories=categories, current_scope=scope, current_q=q)

@categories_bp.route('/<cat_id>', methods=['POST'])
def update(cat_id):
    name = request.form.get('name')
    scope = request.form.get('scope')
    file = request.files.get('file')
    
    if file and file.filename:
        files = {'file': (file.filename, file.stream, file.content_type)}
        data = {'name': name, 'scope': scope}
        response = APIClient.patch(f'/categories/{cat_id}', data=data, files=files)
    else:
        response = APIClient.patch(f'/categories/{cat_id}', json={'name': name, 'scope': scope})
        
    if response and response.status_code == 200:
        flash('Catégorie mise à jour.', 'success')
    else:
        flash('Erreur lors de la mise à jour.', 'danger')
    return redirect(url_for('categories.index'))

@categories_bp.route('/<cat_id>/delete', methods=['POST'])
def delete(cat_id):
    response = APIClient.delete(f'/categories/{cat_id}')
    if response and response.status_code == 200:
        flash('Catégorie supprimée.', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
    return redirect(url_for('categories.index'))
