from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # We don't have the login endpoint in the documentation, 
        # but we can try common ones or allow manual token input for now.
        # Let's assume there is a login endpoint at /api/auth/login
        try:
            # Attempting to login to get a token
            # If the endpoint is different, this might fail.
            response = requests.post("https://galaxy.mirhosty.com/api/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                token = data.get('access_token') or data.get('token')
                if token:
                    session['access_token'] = token
                    flash('Connexion réussie !', 'success')
                    return redirect(url_for('dashboard.index'))
                else:
                    flash('Token non reçu du serveur.', 'danger')
            else:
                flash('Identifiants invalides ou erreur serveur.', 'danger')
        except Exception as e:
            flash(f"Erreur de connexion : {str(e)}", 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('access_token', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))
