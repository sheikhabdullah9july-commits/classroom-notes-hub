from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page and next_page.startswith('/') and not next_page.startswith('//') and '\\' not in next_page else url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'student'  # Privileged roles must be granted by an existing admin.
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# Profile Page
@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')


# Change Password
@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Check new password match
        if new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Check password length
        if len(new_password) < 4:
            flash('Password must be at least 4 characters!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Update password
        current_user.set_password(new_password)
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html')


# Forgot Password - Step 1: Enter Email
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if not current_app.config.get("ALLOW_INSECURE_DEMO_RESET", False):
        abort(503, description="Password recovery requires an email delivery integration.")
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            # For now, show the reset link (in production, send via email)
            flash(f'Password reset link has been generated! Token: {token}', 'info')
            return redirect(url_for('auth.reset_password', token=token))
        else:
            flash('Email not found in our system!', 'danger')

    return render_template('auth/forgot_password.html')


# Forgot Password - Step 2: Reset Password with Token
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_app.config.get("ALLOW_INSECURE_DEMO_RESET", False):
        abort(503, description="Password recovery requires an email delivery integration.")
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Find user with this token
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash('Invalid or expired reset link!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    # Check if token expired
    if user.reset_token_expiry < datetime.utcnow():
        flash('Reset link has expired! Please request a new one.', 'danger')
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        if len(new_password) < 4:
            flash('Password must be at least 4 characters!', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        # Update password and clear token
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Password reset successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token, email=user.email)
