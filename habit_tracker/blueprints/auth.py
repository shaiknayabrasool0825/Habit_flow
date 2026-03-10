from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import re

from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from email_service import send_reset_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Password Validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('register.html')
        if not re.search(r"[A-Z]", password):
            flash('Password must contain at least one uppercase letter', 'error')
            return render_template('register.html')
        if not re.search(r"[\d]", password):
            flash('Password must contain at least one number', 'error')
            return render_template('register.html')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash('Password must contain at least one special character', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Send welcome email
            try:
                from email_service import send_welcome_email
                send_welcome_email(new_user.email, new_user.username)
            except Exception as e:
                print(f"Failed to send welcome email: {e}")
            
            login_user(new_user)
            return redirect(url_for('dashboard.dashboard'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate Reset Token based on secret_key
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='reset-password-salt')
            
            reset_url = url_for('auth.reset_token', token=token, _external=True)
            try:
                send_reset_email(user.email, reset_url)
                flash('An email with instructions to reset your password has been sent to you.', 'success')
            except Exception as e:
                flash("There was an error sending the reset email. Please try again.", 'error')
                print(f"Failed to send reset email: {e}")
        else:
            # Always return this even if user isn't found for security reasons
            flash('An email with instructions to reset your password has been sent to you.', 'success')
            
        return redirect(url_for('auth.login'))
        
    return render_template('reset_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Token expires in 1 Hour (3600 seconds)
        email = s.loads(token, salt='reset-password-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.reset_request'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords must match.', 'error')
            return render_template('reset_token.html', token=token)
            
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been securely updated! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('reset_token.html', token=token)
