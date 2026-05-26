from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

products_bp = Blueprint('products', __name__)

@products_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@products_bp.route('/')
def list_products():
    limit = request.args.get('limit', 20)
    cursor = request.args.get('cursor')
    params = {'limit': limit}
    if cursor: params['cursor'] = cursor
    
    response = APIClient.get('/products', params=params)
    products = []
    next_cursor = None
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict):
            products = data.get('products') or data.get('data') or data.get('items') or []
            next_cursor = data.get('nextCursor')
            
        for p in products:
            if isinstance(p, dict) and 'id' not in p and '_id' in p:
                p['id'] = p['_id']
            
    return render_template('admin/products_list.html', products=products, next_cursor=next_cursor, limit=limit, cursor=cursor)

@products_bp.route('/owner/<user_id>')
def owner_products(user_id):
    response = APIClient.get(f'/products/owner/{user_id}')
    products = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict):
            products = data.get('products') or data.get('data') or data.get('items') or []

        for p in products:
            if isinstance(p, dict) and 'id' not in p and '_id' in p:
                p['id'] = p['_id']

    return render_template('admin/products_list.html', products=products, next_cursor=None, limit=20, cursor=None, owner_id=user_id)

@products_bp.route('/<product_id>')
def product_details(product_id):
    response = APIClient.get(f'/products/{product_id}')
    product = None
    if response and response.status_code == 200:
        product = response.json()
        if product and isinstance(product, dict):
            if 'id' not in product and '_id' in product:
                product['id'] = product['_id']
                
    return render_template('admin/product_details.html', product=product)

@products_bp.route('/<product_id>/moderate', methods=['POST'])
def moderate_product(product_id):
    status = request.form.get('status')
    reason = request.form.get('reason')
    data = {'moderationStatus': status}
    if reason:
        data['reason'] = reason
    
    response = APIClient.patch(f'/products/{product_id}/moderate', json=data)
    if response and response.status_code == 200:
        flash('Produit modéré avec succès.', 'success')
    else:
        flash('Erreur lors de la modération.', 'danger')
    return redirect(url_for('products.product_details', product_id=product_id))

@products_bp.route('/<product_id>/update', methods=['POST'])
def update_product(product_id):
    data = {key: value for key, value in request.form.items() if value != ''}
    response = APIClient.patch(f'/products/{product_id}', json=data)
    if response and response.status_code == 200:
        flash('Produit mis a jour.', 'success')
    else:
        flash('Erreur lors de la mise a jour.', 'danger')
    return redirect(url_for('products.product_details', product_id=product_id))

@products_bp.route('/<product_id>/archive', methods=['POST'])
def archive_product(product_id):
    response = APIClient.patch(f'/products/{product_id}/archive')
    if response and response.status_code == 200:
        flash('Produit archivé.', 'success')
    else:
        flash('Erreur lors de l\'archivage.', 'danger')
    return redirect(url_for('products.product_details', product_id=product_id))

@products_bp.route('/<product_id>/delete', methods=['POST'])
def delete_product(product_id):
    response = APIClient.delete(f'/products/{product_id}')
    if response and response.status_code == 200:
        flash('Produit supprimé.', 'success')
        return redirect(url_for('products.list_products'))
    else:
        flash('Erreur lors de la suppression.', 'danger')
        return redirect(url_for('products.product_details', product_id=product_id))
