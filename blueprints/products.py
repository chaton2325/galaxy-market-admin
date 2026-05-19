from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from api_client import APIClient

products_bp = Blueprint('products', __name__)

@products_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))

@products_bp.route('/')
def list_products():
    limit = request.args.get('limit')
    cursor = request.args.get('cursor')
    params = {}
    if limit: params['limit'] = limit
    if cursor: params['cursor'] = cursor
    
    response = APIClient.get('/products', params=params)
    products = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict):
            products = data.get('products') or data.get('data') or data.get('items') or []
            
        # Normalization for MongoDB _id
        for p in products:
            if isinstance(p, dict):
                if 'id' not in p and '_id' in p:
                    p['id'] = p['_id']
            
    return render_template('admin/products_list.html', products=products)

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
