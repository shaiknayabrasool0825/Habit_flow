from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Habit, HabitLog, Suggestion, WeeklyReport
from datetime import datetime
from ml_logic import retrain_habit_model

habits_bp = Blueprint('habits', __name__)

@habits_bp.route('/add_habit', methods=['POST'])
@login_required
def add_habit():
    name = request.form.get('name')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    
    if name:
        new_habit = Habit(
            user_id=current_user.id, 
            name=name,
            color=request.form.get('color', 'blue'),
            icon=request.form.get('icon', '⭐')
        )
        if start_time_str:
            new_habit.start_time = datetime.strptime(start_time_str, '%H:%M').time()
        if end_time_str:
            new_habit.end_time = datetime.strptime(end_time_str, '%H:%M').time()
        db.session.add(new_habit)
        db.session.commit()
    return redirect(url_for('dashboard.dashboard'))

@habits_bp.route('/update_habit', methods=['POST'])
@login_required
def update_habit():
    habit_id = request.form.get('habit_id')
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard.dashboard'))
        
    habit.name = request.form.get('name')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    if start_time_str:
        habit.start_time = datetime.strptime(start_time_str, '%H:%M').time()
    if end_time_str:
        habit.end_time = datetime.strptime(end_time_str, '%H:%M').time()
    habit.color = request.form.get('color', 'blue')
    habit.icon = request.form.get('icon', '⭐')
    db.session.commit()
    
    retrain_habit_model(current_user.id, habit.id)
    flash("✨ Habit updated! We will optimize your schedule.", "success")
    return redirect(url_for('dashboard.dashboard'))

@habits_bp.route('/delete_habit/<int:habit_id>')
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id == current_user.id:
        try:
            reports = WeeklyReport.query.filter(
                (WeeklyReport.strongest_habit_id == habit_id) | 
                (WeeklyReport.weakest_habit_id == habit_id)
            ).all()
            for r in reports:
                if r.strongest_habit_id == habit_id: r.strongest_habit_id = None
                if r.weakest_habit_id == habit_id: r.weakest_habit_id = None
            db.session.commit()
            Suggestion.query.filter_by(habit_id=habit_id).delete()
            HabitLog.query.filter_by(habit_id=habit_id).delete()
            db.session.delete(habit)
            db.session.commit()
            flash('Habit deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting habit: {e}")
            flash('Error deleting habit.', 'danger')
    return redirect(url_for('dashboard.dashboard'))
