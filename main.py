from flask import Flask, render_template, session, redirect, url_for
import os
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.users import users_bp
from blueprints.products import products_bp
from blueprints.services import services_bp
from blueprints.moderation import moderation_bp
from blueprints.audit import audit_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(services_bp, url_prefix='/services')
app.register_blueprint(moderation_bp, url_prefix='/moderation')
app.register_blueprint(audit_bp, url_prefix='/audit')

@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
