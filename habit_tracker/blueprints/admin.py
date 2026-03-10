from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
import sys

# Setting up paths for importing models
from models import db, User, Habit, HabitLog, Suggestion, UserAchievement, WeeklyReport, Session, Friendship

admin_bp = Blueprint('admin', __name__)

# Basic protection: Only allow a specific user, or an 'is_admin' flag. 
# For now, we'll allow access but you should protect this in production.
def is_admin():
    # Strictly limit access to the master admin email
    return current_user.is_authenticated and current_user.email == 'nayabrasoolshaik4842@gmail.com'

@admin_bp.route('/')
@login_required
def admin_dashboard():
    if not is_admin():
        flash("Access Denied", "error")
        return redirect(url_for('dashboard.home'))
        
    users = User.query.all()
    return render_template('admin.html', users=users, user=current_user)

@admin_bp.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if not is_admin():
        return redirect(url_for('admin.admin_dashboard'))
        
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        flash('Email or Username already exists.', 'error')
    else:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {username} successfully created!', 'success')
        
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not is_admin():
        return redirect(url_for('admin.admin_dashboard'))
        
    if user_id == current_user.id:
        flash("You cannot delete yourself from the admin panel.", "error")
        return redirect(url_for('admin.admin_dashboard'))
        
    target_user = User.query.get_or_404(user_id)
    
    # Cascade deletion matching delete_user.py
    Friendship.query.filter((Friendship.user_id == target_user.id) | (Friendship.friend_id == target_user.id)).delete()
    Session.query.filter_by(user_id=target_user.id).delete()
    WeeklyReport.query.filter_by(user_id=target_user.id).delete()
    Suggestion.query.filter_by(user_id=target_user.id).delete()
    UserAchievement.query.filter_by(user_id=target_user.id).delete()
    
    habits = Habit.query.filter_by(user_id=target_user.id).all()
    for habit in habits:
        HabitLog.query.filter_by(habit_id=habit.id).delete()
        db.session.delete(habit)
        
    db.session.delete(target_user)
    db.session.commit()
    
    flash(f"User {target_user.username} destroyed completely.", "success")
    return redirect(url_for('admin.admin_dashboard'))
