from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from api_client import APIClient

carrousel_bp = Blueprint('carrousel', __name__)

SOURCE_TYPES = ['MANUAL', 'PRODUCT', 'SERVICE']


@carrousel_bp.before_request
def check_auth():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))


def clean_payload(keys):
    payload = {}
    for key in keys:
        value = request.form.get(key)
        if value not in [None, '']:
            if key == 'position':
                try:
                    payload[key] = int(value)
                except ValueError:
                    payload[key] = value
            elif key == 'isActive':
                payload[key] = value == 'true'
            else:
                payload[key] = value
    return payload


def multipart_fields(data):
    fields = []
    for key, value in data.items():
        if value not in [None, '']:
            fields.append((key, (None, str(value))))
    return fields


def normalize_items(data, list_keys):
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = []
        for key in list_keys:
            items = data.get(key)
            if items is not None:
                break
        if items is None:
            items = []
    else:
        items = []

    for item in items:
        if isinstance(item, dict) and 'id' not in item and '_id' in item:
            item['id'] = item['_id']
    return items


def fetch_catalog_options():
    products_response = APIClient.get('/products', params={'limit': 100})
    services_response = APIClient.get('/services', params={'limit': 100})

    products = []
    services = []
    if products_response and products_response.status_code == 200:
        products = normalize_items(products_response.json(), ['products', 'data', 'items'])
    if services_response and services_response.status_code == 200:
        services = normalize_items(services_response.json(), ['services', 'data', 'items'])

    return products, services


@carrousel_bp.route('/')
def index():
    response = APIClient.carrousel_get('/admin/all')
    items = []
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get('data') or data.get('items') or []

    for item in items:
        if isinstance(item, dict) and 'id' not in item and '_id' in item:
            item['id'] = item['_id']
    if response is not None and response.status_code != 200:
        detail = ''
        try:
            detail = response.json().get('message', '')
        except ValueError:
            detail = response.text[:200]
        flash(f"Erreur lors du chargement des bannieres: HTTP {response.status_code}. {detail}", 'danger')

    products, services = fetch_catalog_options()

    return render_template(
        'admin/carrousel.html',
        items=items,
        source_types=SOURCE_TYPES,
        products=products,
        services=services,
    )


@carrousel_bp.route('/create', methods=['POST'])
def create():
    source_type = request.form.get('sourceType') or 'MANUAL'
    data = clean_payload(['title', 'subtitle', 'ctaLabel', 'ctaLink', 'position'])
    data['sourceType'] = source_type

    if source_type in ['PRODUCT', 'SERVICE']:
        source_id = request.form.get('productSourceId') if source_type == 'PRODUCT' else request.form.get('serviceSourceId')
        source_id = source_id or request.form.get('sourceId')
        if source_id:
            data['sourceId'] = source_id

    file = request.files.get('file')
    files = multipart_fields(data)
    if source_type == 'MANUAL' and file and file.filename:
        files.append(('file', (file.filename, file.stream, file.content_type)))

    response = APIClient.carrousel_post('', files=files)
    if response and response.status_code in [200, 201]:
        flash('Banniere carrousel creee.', 'success')
    else:
        detail = ''
        if response is not None:
            try:
                detail = response.json().get('message', '')
            except ValueError:
                detail = response.text[:200]
        flash(f"Erreur lors de la creation de la banniere. {detail}", 'danger')

    return redirect(url_for('carrousel.index'))


@carrousel_bp.route('/<carousel_id>/update', methods=['POST'])
def update(carousel_id):
    payload = clean_payload(['title', 'subtitle', 'ctaLabel', 'ctaLink', 'position', 'isActive'])
    response = APIClient.carrousel_patch(f'/{carousel_id}', json=payload)

    if response and response.status_code == 200:
        flash('Banniere mise a jour.', 'success')
    else:
        flash('Erreur lors de la mise a jour de la banniere.', 'danger')

    return redirect(url_for('carrousel.index'))


@carrousel_bp.route('/<carousel_id>/image', methods=['POST'])
def replace_image(carousel_id):
    file = request.files.get('file')
    if not file or not file.filename:
        flash('Selectionne une image a uploader.', 'warning')
        return redirect(url_for('carrousel.index'))

    files = {'file': (file.filename, file.stream, file.content_type)}
    response = APIClient.carrousel_patch(f'/{carousel_id}/image', files=files)
    if response and response.status_code == 200:
        flash('Image de la banniere remplacee.', 'success')
    else:
        flash('Erreur lors du remplacement de l image.', 'danger')

    return redirect(url_for('carrousel.index'))


@carrousel_bp.route('/<carousel_id>/delete', methods=['POST'])
def delete(carousel_id):
    response = APIClient.carrousel_delete(f'/{carousel_id}')
    if response and response.status_code in [200, 204]:
        flash('Banniere supprimee.', 'success')
    else:
        flash('Erreur lors de la suppression de la banniere.', 'danger')

    return redirect(url_for('carrousel.index'))
